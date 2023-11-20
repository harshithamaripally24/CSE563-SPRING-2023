Project Setup and Execution Instructions

System Requirements
Python 3.x
MySQL Server

Installation Instructions
• Install Python 3.x on your system. You can download the latest version of Python from the official website: https://www.python.org/downloads/
• Install MySQL Server on your system. You can download the latest version of MySQL from the official website: https://dev.mysql.com/downloads/
• Install the required Python packages using pip. Open a command prompt/terminal and run the following command:
Python (version 3 or later)
Flask (a Python web framework)
mysql-connector-python (a Python driver for MySQL)
python-dotenv (a Python module for loading environment variables from a .env file)

pip install Flask
pip install Flask-Mail
pip install Flask-WTF
pip install WTForms
pip install mysql-connector-python
pip install python-dotenv
pip install xlsxwriter
You may need to use pip3 instead of pip depending on your system configuration
• Environment variables are defined in the .env file

# .env file

MAIL_USERNAME=you@example.com
MAIL_PASSWORD=your_email_password
SECRET_KEY=your_secret_key

Replace you@example.com, your_email_password, and your_secret_key with your email username, email password, and secret key, respectively.

Database Setup

1. Open MySQL Command Line Client and enter your MySQL root user password when prompted.
2. Set up a MySQL database:
   Execute the queries.sql script to create the required database and table.

queries.sql

DROP DATABASE IF EXISTS test_db;

CREATE DATABASE test_db;

USE test_db;

DROP TABLE IF EXISTS users;

CREATE TABLE users (
id INT AUTO_INCREMENT PRIMARY KEY,
name VARCHAR(255),
email VARCHAR(255),
password VARCHAR(255),
otp VARCHAR(255)
);

SELECT \* FROM USERS;

ALTER TABLE users ADD role VARCHAR(255);

CREATE TABLE tasks (
task_id INT AUTO_INCREMENT PRIMARY KEY,
task_name VARCHAR(255),
task_desc VARCHAR(255),
assigned_to VARCHAR(255),
task_hours VARCHAR(255)
);

SELECT \* FROM TASKS;

3. Update the database credentials in .env file to match your MySQL database:

# .env file

HOST_NAME=localhost
DB_USER=yourusername
DB_PASSWORD=yourpassword
DB_NAME=yourdatabase

o Replace localhost, yourusername, yourpassword, and yourdatabase with your host name or IP address, MySQL username, password, and database name, respectively.

Execution Instructions

1. Download the source code.
2. Open the command prompt/terminal and navigate to the project directory.
3. Run the following command to start the Flask server:
   FLASK_APP=login.py
   FLASK_ENV=development
   python login.py
4. Navigate to http://localhost:5000 in your web browser to access the application.
5. You can now use the application to register new users, login, and view your profile.

o You can register a new user by clicking on the " Sign up here " link and entering your details
o After registering, you will receive an OTP on your registered email address. Enter the OTP on the verification page to complete the registration process.
o Log in to the application by clicking on the "Log in" button and entering your email address and password.
o Enter the 6-digit OTP sent to your email address to complete the authentication process.
o When you click on the logout button, you will be redirected to the login page.
