# Employee Registration App

Flask + MySQL + Bootstrap 5 app to register, list, search and delete employees.

## Features
- Registration form (name, email, department, phone) with client-side **and** server-side validation
- Duplicate email detection (MySQL UNIQUE constraint)
- Bootstrap table with live search, delete confirmation modal, toast notifications
- REST API: `GET/POST /api/employees`, `DELETE /api/employees/<id>`

## Setup
Install and start MySQL Server before running the app. The app connects to
`localhost:3306` by default.

```bash
git clone <your-repo-url> && cd employee-registration-app
python -m venv venv
venv\Scripts\activate          # Windows  (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt

mysql -u root -p < schema.sql  # creates employee_db + employees table
copy .env.example .env         # then edit DB_PASSWORD  (Linux/Mac: cp)

python app.py                  # open http://127.0.0.1:5000
```

On Windows, create `.env` from `.env.example` in the app folder and set
`DB_PASSWORD` to the password for your MySQL user. Create the database and
table by running `schema.sql` in MySQL Workbench, or use the `mysql` command
shown above if the MySQL command-line client is installed.

### MySQL connection refused

If startup reports `Can't connect to MySQL server on 'localhost:3306'`
or `ConnectionRefusedError`, no MySQL server is accepting connections at that
address. Start the MySQL service from the Windows Services app (the service is
often named `MySQL80`) and confirm its configured port matches `DB_PORT` in
`.env`. If no MySQL service is listed, install MySQL Server first. After the
server is running, create the database using `schema.sql` and check that
`DB_USER` and `DB_PASSWORD` in `.env` match your MySQL account.

## Structure
```
app.py             Flask routes, validation, DB access
schema.sql         MySQL schema
templates/         index.html
static/css, js     style.css, app.js
```

## Push to GitHub
```bash
git init
git add .
git commit -m "Employee registration app"
git branch -M main
git remote add origin https://github.com/<username>/employee-registration-app.git
git push -u origin main
```