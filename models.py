import psycopg2
import bcrypt
from app.config import Config

def get_db_connection():
    conn = psycopg2.connect(
        dbname=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        host=Config.DB_HOST,
        port=Config.DB_PORT
    )
    return conn

def check_admin_credentials(email, password):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT user_password FROM users WHERE user_email = %s AND user_type_id = 1",
            (email,)
        )
        result = cur.fetchone()
        cur.close()
        conn.close()

        if not result:
            return False, "Invalid email or not an admin"

        hashed_password = result[0]
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
            return True, "Login success"
        else:
            return False, "Incorrect password"

    except Exception as e:
        print("Error:", e)
        return False, "Server error"
