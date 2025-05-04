import psycopg2

from flask import Blueprint, session, flash, redirect, render_template, request, url_for

from werkzeug.security import check_password_hash, generate_password_hash

from db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = "Username required"
        elif not password:
            error = "Password required"

        
        if error is None:
            try:
                db.execute(
                    "INSERT INTO users (user_name, user_password, user_type_id) VALUES(%s, %s, 3)",
                    (username, generate_password_hash(password,)),
                )
            except psycopg2.OperationalError as err:
                print(err)
                error = f"User {username} is already registered"
            else:
                return redirect(url_for("auth.login"))
        flash(error)

    return render_template('auth/register.html')




@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        db.execute(
            'SELECT * FROM users WHERE user_name = %s', (username,)
        )
        user = db.fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['user_password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['user_id']
            return redirect(url_for('calendar_user.calendar'))

        flash(error)

    return render_template('auth/login.html')