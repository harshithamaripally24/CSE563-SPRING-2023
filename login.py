# Author 1: Harshitha Maripally
# Author 2: Naga Vardhini Garugu
# Description: The project is intended to demonstrate secure user authentication using Python, Flask and MySQL. It includes features such as password hashing, email verification with OTP, and captcha verification during user registration and login to ensure enhanced security. Additionally, the project implements user roles, where users can have different levels of access to the system based on their roles. The application includes multiple dashboards, each designed for a specific user role, with various tasks and functionalities specific to the user's role. 

import os
import re
from flask import Flask, jsonify, render_template, request, redirect, session, url_for, flash
from db_connection import db
import random
import hashlib
import string
import smtplib
import random
import string
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from flask import make_response
from flask import make_response
import pandas as pd

from flask_mail import Mail, Message

from dotenv import load_dotenv
load_dotenv()

mail_username = os.environ.get('MAIL_USERNAME')
mail_password = os.environ.get('MAIL_PASSWORD')

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = mail_username
app.config['MAIL_PASSWORD'] = mail_password
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = mail_username

mail = Mail(app)

# Set up secret key for the session
app.secret_key = os.getenv("SECRET_KEY")

# Set up database connection

cursor = db.cursor()

# Home page


@app.route('/')
def home():
    # Get message parameter from URL if it exists
    message = request.args.get('message')

    return render_template('home.html', message=message)

# Registration page


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/register', methods=['POST'])
def register():
    # Get form data
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    otp = ""
    role = request.form['role']

    # Validate password length
    if len(password) < 8:
        return render_template('signup.html', error='Password must be at least 8 characters long')
    
    if not re.search(r'[A-Z]', password):
        return render_template('signup.html', error='Password must contain at least one uppercase letter')
    
    if not re.search(r'[a-z]', password):
        return render_template('signup.html', error='Password must contain at least one lowercase letter')
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return render_template('signup.html', error='Password must contain at least one special character')

    # Hash password
    password_bytes = password.encode('utf-8')
    hash_object = hashlib.sha256(password_bytes)
    hash_hex = hash_object.hexdigest()

    # Check if user already exists
    query = 'SELECT * FROM users WHERE email = %s'
    values = (email,)
    cursor.execute(query, values)
    user = cursor.fetchall()

    # If user exists, show message
    if user:
        return render_template('signup.html', error='User already exists with that email')

    # If user does not exist, insert data into database and redirect to login page
    else:
        otp = ''.join(random.choices(string.digits, k=6))
        query = 'INSERT INTO users (name, email, password, otp, role) VALUES (%s, %s, %s, %s, %s)'
        values = (name, email, hash_hex, otp, role)
        cursor.execute(query, values)
        db.commit()
        send_email(email, otp)  # Send OTP to user's email

        return redirect(url_for('otp_verification', email=email, redirect_to='register'))

# Login page


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/verify', methods=['POST'])
def verify():
    # Get form data
    email = request.form['email']
    password = request.form['password']
    password_bytes = password.encode('utf-8')
    hash_object = hashlib.sha256(password_bytes)
    hash_hex = hash_object.hexdigest()
    captcha = request.form['captcha']
    
    # Check if captcha is valid
    captcha_text = session.get('captcha_text')
    if captcha != captcha_text:
        return redirect(url_for('home', message='Invalid captcha'))
    
    # Check if user exists in database
    query = 'SELECT * FROM users WHERE email = %s AND password = %s'
    values = (email, hash_hex)

    # Consume any unread result found in the cursor
    while cursor.nextset():
        pass

    cursor.execute(query, values)
    user = cursor.fetchall()

    if user:
        # Generate a 6-digit OTP store it in db for that user
        otp = ''.join(random.choices(string.digits, k=6))
        query = 'UPDATE users SET otp = %s WHERE email= %s;'
        values = (otp, user[0][2])
        cursor.execute(query, values)
        db.commit()
        send_email(email, otp)  # Send OTP to user's email

        return redirect(url_for('otp_verification', email=email, redirect_to='login'))
    # If user does not exist, redirect to home page with error message
    else:
        return redirect(url_for('home', message='Incorrect email or password'))


@app.route('/otp_verification', methods=['GET', 'POST'])
def otp_verification():
    if request.method == 'GET':
        # Get email
        email = request.args.get('email')
        redirect_to = request.args.get('redirect_to')
        return render_template('otp_verification.html', email=email, redirect_to=redirect_to)

    elif request.method == 'POST':
        # Get form data
        email = request.form['email']
        user_otp = request.form['user_otp']
        query = 'SELECT * FROM users WHERE email = %s;'
        values = (email,)

        cursor.execute(query, values)
        user = cursor.fetchall()
        if user[0][4] == user_otp:
            print("otp verified")
            # If OTP is correct, log user in and redirect
            redirect_to = request.form['redirect_to']
            if redirect_to == 'login':
                # return redirect(url_for('success', message='Login successful!'))
                 if user[0][5] == 'employee':
                    return redirect(url_for('employee_dashboard'))
                 elif user[0][5] == 'manager':
                    return redirect(url_for('manager_dashboard'))
                 elif user[0][5]== 'admin':
                    return redirect(url_for('admin_dashboard'))
            elif redirect_to == 'register':
                    return render_template('signup.html', success='User registered successfully')

        else:
            # If OTP is incorrect, redirect to OTP verification page with error message
            email = request.args.get('email')
            redirect_to = request.args.get('redirect_to')
            error = 'Invalid OTP'
            return redirect(url_for('otp_verification', message='Incorrect OTP', email=email, redirect_to=redirect_to, error=error))


@app.route('/employee/dashboard')
def employee_dashboard():
    return render_template('employee_dashboard.html')

# Manager home page
@app.route('/manager/dashboard')
def manager_dashboard():
    return render_template('manager_dashboard.html')

# Admin home page
@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

def send_email(email, otp):
    # Create message object
    msg = Message(subject='OTP Verification', sender=mail_username, recipients=[email])

    # Set message body
    msg.body = f'Your OTP is {otp}. Please enter this code in the OTP verification page to complete your login.'

    # Send message
    mail.send(msg)


@app.route('/success')
def success():
    message = request.args.get('message')
    return render_template('success.html', message=message)


@app.route('/logout')
def logout():
    print("log out is clicked")
    return redirect(url_for('home'))


@app.route('/captcha_image')
def captcha_image():
    # Generate a random string of 5 uppercase letters, numbers and lowercase letters
    captcha_text = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=5))
    session['captcha_text'] = captcha_text  # Store captcha text in session

    # Create a PIL image object
    width, height = 150, 60
    image = Image.new('RGB', (width, height), color=(255, 255, 255))

    # Create a drawing context
    draw = ImageDraw.Draw(image)

    # Set a random font size and font type
    font_size = random.randint(30, 40)
    font_type = random.choice(['arial.ttf', 'arialbd.ttf', 'calibri.ttf', 'comic.ttf', 'georgia.ttf'])

    # Set a random font
    font = ImageFont.truetype(font_type, font_size)

    # Get the size of the captcha text
    bbox = draw.textbbox((0, 0), captcha_text, font=font)

    # Calculate the center position for the captcha text
    x = (width - bbox[2]) / 2
    y = (height - bbox[3]) / 2

    # Draw the captcha text
    draw.text((x, y), captcha_text, fill=(0, 0, 0), font=font)

    # Add some noise to the image
    for i in range(200):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        draw.point((x, y), fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

    # Add random lines
    for i in range(5):
        x1 = random.randint(0, width - 1)
        y1 = random.randint(0, height - 1)
        x2 = random.randint(0, width - 1)
        y2 = random.randint(0, height - 1)
        draw.line((x1, y1, x2, y2), fill=(0, 0, 0), width=random.randint(1, 2))

    # Add random shapes
    for i in range(3):
        x1 = random.randint(0, width - 20)
        y1 = random.randint(0, height - 20)
        x2 = random.randint(x1 + 10, width - 1)
        y2 = random.randint(y1 + 10, height - 1)
        draw.rectangle((x1, y1, x2, y2), outline=(0, 0, 0), width=random.randint(1, 2))

    # Save the image to a byte buffer
    buffer = BytesIO()
    image.save(buffer, 'jpeg')
    buffer.seek(0)

    # Create a Flask response object with the image data and content type
    response = make_response(buffer.read())
    response.headers.set('Content-Type', 'image/jpeg')

    print(response)
    return response


@app.route('/manage_users', methods=['GET', 'POST'])
def manage_users():
    if request.method == 'POST':
        # get the user ID from the form submission
        user_id = request.form.get('user_id')

        # delete the user from the database
        cursor = db.cursor()
        cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
        db.commit()

        # redirect to the same page to refresh the user list
        return redirect(url_for('manage_users', success='User deleted successfully'))

    else:
        # fetch the list of users
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE role != 'admin'")
        users = cursor.fetchall()

        # render the template and pass the list of users to it
        return render_template('manage_users.html', users=users)



@app.route('/manage_projects')
def manage_projects():
    return render_template('manage_projects.html')


@app.route('/employee_details', methods=['GET', 'POST'])
def employee_details():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE role = 'employee'")
    employees = cursor.fetchall()
    employee = None
    print(employees)
    if request.method == 'POST':
        employee_id = request.form['employee_id']
        cursor.execute("SELECT users.name, users.email, tasks.task_name, tasks.task_hours FROM users INNER JOIN tasks on users.id=tasks.assigned_to WHERE users.id = %s", (employee_id,))
        employee = cursor.fetchone()
    cursor.fetchall()
    return render_template('employee_details.html', employees=employees, employee=employee)


@app.route('/task_details', methods=['GET', 'POST'])
def task_details():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    task = None
    print(tasks)
    if request.method == 'POST':
        task_id = request.form['task_id']
        cursor.execute("SELECT tasks.task_name, tasks.task_desc, users.name, tasks.task_hours FROM tasks INNER JOIN users ON tasks.assigned_to = users.id WHERE tasks.task_id = %s", (task_id,))
        task = cursor.fetchone()
    cursor.fetchall()
    return render_template('task_details.html', tasks=tasks, task=task)


@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    if request.method == 'GET':
        # fetch the list of employees
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE role='employee'")
        employees = cursor.fetchall()

        # render the template and pass the list of employees to it
        return render_template('add_task.html', employees=employees)

    elif request.method == 'POST':
        # Get form data
        task_name = request.form['task-name']
        task_desc = request.form['task-desc']
        assigned_to = request.form['assigned-to']

        # Insert into database
        cursor = db.cursor()
        query = "INSERT INTO tasks (task_name, task_desc, assigned_to) VALUES (%s, %s, %s)"
        values = (task_name, task_desc, assigned_to)
        cursor.execute(query, values)
        db.commit()

        return redirect(url_for('add_task', success='Task added successfully'))


@app.route('/effort_logger', methods=['GET', 'POST'])
def effort_logger():
    if request.method == 'GET':
        # fetch tasks from the tasks table in the database
        cursor = db.cursor()
        cursor.execute("SELECT * FROM tasks")
        tasks = cursor.fetchall()

        # pass the list of tasks to the template
        return render_template('effort_logger.html', tasks=tasks)
    
    elif request.method == 'POST':
        # Get form data
        task_name = request.form['assigned-task']
        task_hours = request.form['task-hours']
        
        print(task_hours)
        print(task_name)

        # Insert into database
        cursor = db.cursor()
        query = "UPDATE tasks SET task_hours = %s WHERE task_name = %s"
        values = (task_hours, task_name)
        print("Query:", query)
        print("Values:", values)
        cursor.execute(query, values)

        db.commit()
        return redirect(url_for('effort_logger', success='Hours logged successfully'))

@app.route('/view reports')
def view_reports():
    return render_template('download_reports.html')
   

@app.route('/download_reports')
def download_reports():
    # fetch data from the database
    cursor = db.cursor()
    cursor.execute("SELECT users.id, users.name, users.email, tasks.task_name, tasks.task_hours FROM users INNER JOIN tasks ON users.id = tasks.assigned_to")
    data = cursor.fetchall()

    # create a pandas dataframe from the fetched data
    df = pd.DataFrame(data, columns=['Employee ID', 'Employee Name', 'Employee Email', 'Assigned Task', 'Logged Hours'])

    # create an excel writer object
    writer = pd.ExcelWriter('employee_effort.xlsx', engine='xlsxwriter')

    # write the dataframe to the excel file
    df.to_excel(writer, sheet_name='Sheet1', index=False)

    # save the excel file and close the writer object
    writer.save()

    # create a Flask response object with the excel file and download it
    response = make_response()
    response.headers['Content-Type'] = 'application/octet-stream'
    response.headers['Content-Disposition'] = 'attachment; filename=employee_effort.xlsx'
    with open('employee_effort.xlsx', 'rb') as file:
        response.data = file.read()
    return response


if __name__ == '__main__':

    app.run(debug=True)
