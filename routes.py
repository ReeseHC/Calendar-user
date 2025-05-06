from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from app.models import check_admin_credentials
import psycopg2  # switched from sqlite3 to psycopg2
import os

# Define the blueprint
main = Blueprint('main', __name__)

# === Admin Login (unchanged) ===
@main.route('/')
def index():
    return render_template("login.html")

@main.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        print(f"Login attempt - Email: {email}")
        success, message = check_admin_credentials(email, password)

        if success:
            return jsonify(message="Login successful!"), 200
        else:
            return jsonify(message=message), 401

    except Exception as e:
        print("Login error:", e)
        return jsonify(message="Server error"), 500

@main.route('/admin')
def admin_dashboard():
    return render_template("admin_dashboard.html")


# === User Login with PostgreSQL ===

@main.route('/user/login', methods=['GET'])
def show_user_login():
    return render_template('user_login.html')

@main.route('/user/login', methods=['POST'])
def user_login():
    email = request.form['email']
    password = request.form['password']

    try:
        conn = psycopg2.connect(
            dbname="doctors_office",
            user="postgres",
            password=os.getenv("DB_PASSWORD"),  # keep it safe in .env
            host="localhost"
        )
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE user_email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and user[4] == password:  # assuming password is 5th column
            return redirect(url_for('main.user_dashboard'))
        else:
            flash("Invalid email or password")
            return redirect(url_for('main.show_user_login'))

    except Exception as e:
        print("Login DB error:", e)
        flash("Something went wrong")
        return redirect(url_for('main.show_user_login'))

@main.route('/user/dashboard')
def user_dashboard():
    return render_template('user_dashboard.html')
