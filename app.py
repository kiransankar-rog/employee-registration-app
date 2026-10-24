import os
import re

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from mysql.connector import Error, IntegrityError, pooling

load_dotenv()

app = Flask(__name__)

pool = pooling.MySQLConnectionPool(
    pool_name="emp_pool",
    pool_size=5,
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", 3306)),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", ""),
    database=os.getenv("DB_NAME", "employee_db"),
)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^\+?\d{10,13}$")
NAME_RE = re.compile(r"^[A-Za-z][A-Za-z .'-]{1,99}$")
DEPARTMENTS = {"HR", "Engineering", "Finance", "Marketing", "Sales", "Operations"}


def validate(data):
    """Server-side validation; returns dict of field -> error message."""
    errors = {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    dept = (data.get("department") or "").strip()
    phone = (data.get("phone") or "").strip()

    if not name:
        errors["name"] = "Name is required."
    elif not NAME_RE.match(name):
        errors["name"] = "Enter a valid name (letters only, min 2 characters)."

    if not email:
        errors["email"] = "Email is required."
    elif not EMAIL_RE.match(email) or len(email) > 120:
        errors["email"] = "Enter a valid email address."

    if not dept:
        errors["department"] = "Department is required."
    elif dept not in DEPARTMENTS:
        errors["department"] = "Select a valid department."

    if not phone:
        errors["phone"] = "Phone number is required."
    elif not PHONE_RE.match(phone):
        errors["phone"] = "Enter 10-13 digits (optional + prefix)."

    return errors


def query(sql, params=(), fetch=False):
    conn = pool.get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        if fetch:
            rows = cur.fetchall()
            return rows
        conn.commit()
        return cur.rowcount, cur.lastrowid
    finally:
        conn.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/employees", methods=["GET"])
def list_employees():
    try:
        rows = query(
            "SELECT id, name, email, department, phone FROM employees ORDER BY id DESC",
            fetch=True,
        )
        return jsonify(rows)
    except Error as e:
        app.logger.error(e)
        return jsonify({"message": "Database error."}), 500


@app.route("/api/employees", methods=["POST"])
def add_employee():
    data = request.get_json(silent=True) or {}
    errors = validate(data)
    if errors:
        return jsonify({"message": "Validation failed.", "errors": errors}), 400
    try:
        _, new_id = query(
            "INSERT INTO employees (name, email, department, phone) VALUES (%s,%s,%s,%s)",
            (
                data["name"].strip(),
                data["email"].strip().lower(),
                data["department"].strip(),
                data["phone"].strip(),
            ),
        )
        return jsonify({"message": "Employee registered.", "id": new_id}), 201
    except IntegrityError:
        return jsonify({"message": "Validation failed.",
                        "errors": {"email": "This email is already registered."}}), 409
    except Error as e:
        app.logger.error(e)
        return jsonify({"message": "Database error."}), 500


@app.route("/api/employees/<int:emp_id>", methods=["DELETE"])
def delete_employee(emp_id):
    try:
        count, _ = query("DELETE FROM employees WHERE id = %s", (emp_id,))
        if count == 0:
            return jsonify({"message": "Employee not found."}), 404
        return jsonify({"message": "Employee deleted."})
    except Error as e:
        app.logger.error(e)
        return jsonify({"message": "Database error."}), 500


if __name__ == "__main__":
    app.run(debug=True)
