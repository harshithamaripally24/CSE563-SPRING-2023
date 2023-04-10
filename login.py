# Author : Harshitha Maripally
# Co-Author : Naga Vardhini Garugu
# Description: The project is intended to demonstrate secure user authentication using Flask and MySQL. It includes password hashing, and email verification with OTP during user registration and login. 

import os
import re
from flask import Flask, render_template, request, redirect, url_for, flash
from db_connection import db
import random
import hashlib
import string
import smtplib

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
    # cursor.close()  # Close the previous result set

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
        # flash('OTP has been sent to your registered email', 'success')
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
        # flash('OTP has been sent to your registered email', 'success')

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
            # print("redirect to", redirect_to)
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
            # if redirect_to == 'login':
            #     return redirect(url_for('otp_verification', message='Incorrect OTP', email=email, redirect_to=redirect_to, error='Incorrect OTP'))
            # elif redirect_to == 'register':
            #     return redirect(url_for('otp_verification', message='Incorrect OTP', email=email, redirect_to=redirect_to, error='Incorrect OTP'))

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

if __name__ == '__main__':

    app.run(debug=True)
