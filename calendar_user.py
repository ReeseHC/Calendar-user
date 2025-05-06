from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from db import get_db
from psycopg2.extras import RealDictCursor
from datetime import datetime

bp = Blueprint('calendar_user', __name__)

# App name
APP_NAME = "Doctor's R US"

@bp.route("/")
def calendar_view():
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    customer_id = session['user_id']
    
    # Query to get counts of booked and open appointments per day
    # This query considers a slot "open" if it exists in Schedule but not in Appointment for this customer
    query = """
    SELECT 
        s.schedule_day as appointment_date,
        COUNT(DISTINCT CASE WHEN a.appointment_status = 'booked' AND a.customer_id = %s THEN (a.appointment_date, a.appointment_slot, a.staff_id) END) AS booked,
        COUNT(DISTINCT CASE WHEN a.appointment_status = 'open' OR a.appointment_status IS NULL THEN (s.schedule_day, s.schedule_slot, s.staff_id) END) AS open
    FROM 
        Schedule s
    LEFT JOIN 
        Appointment a ON s.schedule_day = a.appointment_date AND s.schedule_slot = a.appointment_slot AND s.staff_id = a.staff_id
    GROUP BY 
        s.schedule_day
    ORDER BY 
        s.schedule_day;
    """
    db.execute(query, (customer_id,))
    rows = db.fetchall()

    calendar_view = {
        row['appointment_date'].strftime("%Y-%m-%d"): {"booked": row['booked'], "open": row['open']}
        for row in rows
    }

    return render_template("calendar_user.html", app_name=APP_NAME, calendar_view=calendar_view)

@bp.route("/details/<date>")
def appointment_details(date):
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    db = get_db()
    customer_id = session['user_id']
    
    try:
        # Convert string date to datetime object
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        
        # Query to get all available slots for the date and customer's booked appointments
        query = """
        SELECT 
            s.schedule_day, 
            s.schedule_slot, 
            s.staff_id,
            s.location_id,
            COALESCE(a.appointment_status, 'available') as status,
            u.user_name as staff_name,
            l.location_name
        FROM 
            Schedule s
        LEFT JOIN 
            Appointment a ON s.schedule_day = a.appointment_date AND s.schedule_slot = a.appointment_slot AND s.staff_id = a.staff_id
                         AND (a.customer_id = %s OR a.customer_id IS NULL)
        JOIN 
            Users u ON s.staff_id = u.user_id
        JOIN 
            Location l ON s.location_id = l.location_id
        WHERE 
            s.schedule_day = %s
        ORDER BY 
            s.schedule_slot;
        """
        db.execute(query, (customer_id, date_obj))
        rows = db.fetchall()

        details = {}
        for row in rows:
            slot_time = row['schedule_slot'].strftime("%H:%M")
            details[slot_time] = {
                "status": row['status'] if row['status'] != 'available' else 'open',
                "staff_id": row['staff_id'],
                "staff_name": row['staff_name'],
                "location_id": row['location_id'],
                "location_name": row['location_name']
            }
        
        return jsonify(details)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route("/calendar")
def calendar():
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    return render_template("/calendar_user/calendar.html", app_name=APP_NAME)

@bp.route("/calendar/schedule")
def schedule():
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    date = request.args.get('date', '')
    customer_id = session['user_id']
    
    try:
        # Convert string date to datetime object
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        
        db = get_db()
        
        # Get counts of booked and open appointments
        count_query = """
        SELECT 
            COUNT(DISTINCT CASE WHEN a.appointment_status = 'booked' AND a.customer_id = %s THEN (a.appointment_date, a.appointment_slot, a.staff_id) END) AS booked,
            COUNT(DISTINCT CASE WHEN a.appointment_status = 'open' OR a.appointment_status IS NULL THEN (s.schedule_day, s.schedule_slot, s.staff_id) END) AS open
        FROM 
            Schedule s
        LEFT JOIN 
            Appointment a ON s.schedule_day = a.appointment_date AND s.schedule_slot = a.appointment_slot AND s.staff_id = a.staff_id
        WHERE 
            s.schedule_day = %s
        """
        db.execute(count_query, (customer_id, date_obj))
        date_data = db.fetchone()
        
        if not date_data:
            date_data = {"booked": 0, "open": 0}
        
        # Get detailed schedule for the date
        details_query = """
        SELECT 
            s.schedule_day, 
            s.schedule_slot, 
            s.staff_id,
            s.location_id,
            COALESCE(a.appointment_status, 'available') as status,
            u.user_name as staff_name,
            l.location_name
        FROM 
            Schedule s
        LEFT JOIN 
            Appointment a ON s.schedule_day = a.appointment_date AND s.schedule_slot = a.appointment_slot AND s.staff_id = a.staff_id
                         AND (a.customer_id = %s OR a.customer_id IS NULL)
        JOIN 
            Users u ON s.staff_id = u.user_id
        JOIN 
            Location l ON s.location_id = l.location_id
        WHERE 
            s.schedule_day = %s
        ORDER BY 
            s.schedule_slot;
        """
        db.execute(details_query, (customer_id, date_obj))
        slots = db.fetchall()
        
        date_details = {}
        for row in slots:
            slot_time = row['schedule_slot'].strftime("%H:%M")
            date_details[slot_time] = {
                "status": row['status'] if row['status'] != 'available' else 'open',
                "staff_id": row['staff_id'],
                "staff_name": row['staff_name'],
                "location_id": row['location_id'],
                "location_name": row['location_name']
            }
        
        return render_template("/calendar_user/schedule.html", 
                             date=date, 
                             appointments=date_data, 
                             appointment_details=date_details, 
                             app_name=APP_NAME)
    except Exception as e:
        # Handle errors
        return render_template("/calendar_user/schedule.html", 
                             date=date, 
                             appointments={"booked": 0, "open": 0}, 
                             appointment_details={}, 
                             app_name=APP_NAME,
                             error=str(e))

@bp.route("/api/appointments")
def get_appointments():
    """API endpoint to get all appointment data"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    db = get_db()
    customer_id = session['user_id']
    
    query = """
    SELECT 
        s.schedule_day as appointment_date,
        COUNT(DISTINCT CASE WHEN a.appointment_status = 'booked' AND a.customer_id = %s THEN (a.appointment_date, a.appointment_slot, a.staff_id) END) AS booked,
        COUNT(DISTINCT CASE WHEN a.appointment_status = 'open' OR a.appointment_status IS NULL THEN (s.schedule_day, s.schedule_slot, s.staff_id) END) AS open
    FROM 
        Schedule s
    LEFT JOIN 
        Appointment a ON s.schedule_day = a.appointment_date AND s.schedule_slot = a.appointment_slot AND s.staff_id = a.staff_id
    GROUP BY 
        s.schedule_day
    ORDER BY 
        s.schedule_day;
    """
    db.execute(query, (customer_id,))
    rows = db.fetchall()

    calendar_data = {
        row['appointment_date'].strftime("%Y-%m-%d"): {"booked": row['booked'], "open": row['open']}
        for row in rows
    }
    
    return jsonify(calendar_data)

@bp.route("/api/appointments/<date>")
def get_appointment_by_date(date):
    """API endpoint to get appointment data for a specific date"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    try:
        db = get_db()
        customer_id = session['user_id']
        
        # Convert string date to datetime object
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        
        query = """
        SELECT 
            COUNT(DISTINCT CASE WHEN a.appointment_status = 'booked' AND a.customer_id = %s THEN (a.appointment_date, a.appointment_slot, a.staff_id) END) AS booked,
            COUNT(DISTINCT CASE WHEN a.appointment_status = 'open' OR a.appointment_status IS NULL THEN (s.schedule_day, s.schedule_slot, s.staff_id) END) AS open
        FROM 
            Schedule s
        LEFT JOIN 
            Appointment a ON s.schedule_day = a.appointment_date AND s.schedule_slot = a.appointment_slot AND s.staff_id = a.staff_id
        WHERE 
            s.schedule_day = %s
        """
        db.execute(query, (customer_id, date_obj))
        result = db.fetchone()
        
        if result:
            return jsonify({"booked": result['booked'], "open": result['open']})
        else:
            return jsonify({"booked": 0, "open": 0})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route("/api/book-appointment", methods=["POST"])
def book_appointment():
    """API endpoint to book an appointment"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Not logged in"}), 401
    
    data = request.json
    date = data.get("date")
    time = data.get("time")
    staff_id = data.get("staff_id")
    location_id = data.get("location_id")
    
    if not date or not time or not staff_id or not location_id:
        return jsonify({"success": False, "error": "Missing required fields"}), 400
    
    try:
        db = get_db()
        customer_id = session['user_id']
        
        # Convert string date and time to datetime objects
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        time_obj = datetime.strptime(time, "%H:%M").time()
        
        # First, check if this slot exists in the schedule
        db.execute("""
        SELECT schedule_day, schedule_slot, staff_id, location_id 
        FROM Schedule 
        WHERE schedule_day = %s AND schedule_slot = %s AND staff_id = %s
        """, (date_obj, time_obj, staff_id))
        
        schedule = db.fetchone()
        
        if not schedule:
            return jsonify({"success": False, "error": "This time slot is not in the schedule"}), 400
        
        # Then check if the appointment already exists
        db.execute("""
        SELECT appointment_id, appointment_date, appointment_slot, staff_id, appointment_status, customer_id
        FROM Appointment
        WHERE appointment_date = %s AND appointment_slot = %s AND staff_id = %s
        """, (date_obj, time_obj, staff_id))
        
        appointment = db.fetchone()
        
        if appointment:
            # If appointment exists and is booked by someone else
            if appointment['appointment_status'] == 'booked' and appointment['customer_id'] != customer_id:
                return jsonify({"success": False, "error": "This appointment is already booked"}), 400
            
            # If appointment exists and is open or has null customer_id, update it
            if appointment['appointment_status'] == 'open' or appointment['customer_id'] is None:
                db.execute("""
                UPDATE Appointment
                SET appointment_status = 'booked', customer_id = %s
                WHERE appointment_date = %s AND appointment_slot = %s AND staff_id = %s
                """, (customer_id, date_obj, time_obj, staff_id))
            
            # If it's already booked by this customer, just return success
            if appointment['appointment_status'] == 'booked' and appointment['customer_id'] == customer_id:
                return jsonify({"success": True, "message": "Appointment already booked by you"})
        else:
            # Create new appointment
            db.execute("""
            INSERT INTO Appointment (appointment_date, appointment_slot, appointment_status, location_id, staff_id, customer_id)
            VALUES (%s, %s, 'booked', %s, %s, %s)
            """, (date_obj, time_obj, location_id, staff_id, customer_id))
        
        # Record in appointment history
        db.execute("""
        INSERT INTO Appointment_History (history_date, appointment_date, appointment_slot, staff_id, history_status, history_notes)
        VALUES (NOW(), %s, %s, %s, 'booked', 'Appointment booked by customer')
        """, (date_obj, time_obj, staff_id))
        
        # Get updated counts
        db.execute("""
        SELECT 
            COUNT(DISTINCT CASE WHEN a.appointment_status = 'booked' AND a.customer_id = %s THEN (a.appointment_date, a.appointment_slot, a.staff_id) END) AS booked,
            COUNT(DISTINCT CASE WHEN a.appointment_status = 'open' OR a.appointment_status IS NULL THEN (s.schedule_day, s.schedule_slot, s.staff_id) END) AS open
        FROM 
            Schedule s
        LEFT JOIN 
            Appointment a ON s.schedule_day = a.appointment_date AND s.schedule_slot = a.appointment_slot AND s.staff_id = a.staff_id
        WHERE 
            s.schedule_day = %s
        """, (customer_id, date_obj))
        
        updated_counts = db.fetchone()
        
        return jsonify({
            "success": True, 
            "message": "Appointment booked successfully!", 
            "appointments": updated_counts
        })
    except Exception as e:
        print(f"Error booking appointment: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

@bp.route("/api/cancel-appointment", methods=["POST"])
def cancel_appointment():
    """API endpoint to cancel an appointment"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    data = request.json
    date = data.get("date")
    time = data.get("time")
    staff_id = data.get("staff_id")
    confirmed = data.get("confirmed", False)
    
    if not date or not time or not staff_id:
        return jsonify({"success": False, "error": "Missing required fields"}), 400
    
    # If not confirmed, just return success so UI can show confirmation dialog
    if not confirmed:
        return jsonify({"success": True, "needsConfirmation": True})
    
    try:
        db = get_db()
        customer_id = session['user_id']
        
        # Convert string date and time to datetime objects
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        time_obj = datetime.strptime(time, "%H:%M").time()
        
        # Check if appointment exists and is booked by this customer
        db.execute("""
        SELECT appointment_date, appointment_slot, staff_id
        FROM Appointment
        WHERE appointment_date = %s AND appointment_slot = %s AND staff_id = %s AND customer_id = %s AND appointment_status = 'booked'
        """, (date_obj, time_obj, staff_id, customer_id))
        
        appointment = db.fetchone()
        
        if appointment:
            # Update appointment status to open AND clear the customer_id
            db.execute("""
            UPDATE Appointment
            SET appointment_status = 'open', customer_id = NULL
            WHERE appointment_date = %s AND appointment_slot = %s AND staff_id = %s AND customer_id = %s
            """, (date_obj, time_obj, staff_id, customer_id))
            
            # Record in appointment history
            db.execute("""
            INSERT INTO Appointment_History (history_date, appointment_date, appointment_slot, staff_id, history_status, history_notes)
            VALUES (NOW(), %s, %s, %s, 'cancelled', 'Appointment cancelled by customer')
            """, (date_obj, time_obj, staff_id))
            
            # Get updated counts
            db.execute("""
            SELECT 
                COUNT(DISTINCT CASE WHEN a.appointment_status = 'booked' AND a.customer_id = %s THEN (a.appointment_date, a.appointment_slot, a.staff_id) END) AS booked,
                COUNT(DISTINCT CASE WHEN a.appointment_status = 'open' OR a.appointment_status IS NULL THEN (s.schedule_day, s.schedule_slot, s.staff_id) END) AS open
            FROM 
                Schedule s
            LEFT JOIN 
                Appointment a ON s.schedule_day = a.appointment_date AND s.schedule_slot = a.appointment_slot AND s.staff_id = a.staff_id
            WHERE 
                s.schedule_day = %s
            """, (customer_id, date_obj))
            
            updated_counts = db.fetchone()
            
            return jsonify({
                "success": True, 
                "message": "Appointment cancelled successfully!", 
                "appointments": updated_counts
            })
        else:
            return jsonify({"success": False, "error": "Appointment not found or not booked by you"}), 400
    except Exception as e:
        print(f"Error cancelling appointment: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

@bp.route("/calendar/feedback")
def feedback():
    """Feedback form page"""
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    date = request.args.get('date', '')
    time = request.args.get('time', '')
    staff_id = request.args.get('staff_id', '')
    
    return render_template("/calendar_user/feedback.html", 
                          date=date, 
                          time=time, 
                          staff_id=staff_id, 
                          app_name=APP_NAME)

@bp.route("/calendar/submit-feedback", methods=["POST"])
def submit_feedback():
    """Handle feedback form submission"""
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        db = get_db()
        customer_id = session['user_id']
        
        # Get form data
        date = request.form.get("date")
        time = request.form.get("time")
        staff_id = request.form.get("staff_id")
        reason = request.form.get("reason")
        comments = request.form.get("comments")
        rating = request.form.get("rating")
        
        if date and time and staff_id:
            # Convert string date and time to datetime objects
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            time_obj = datetime.strptime(time, "%H:%M:%S").time()
            
            # Add to appointment history
            db.execute("""
            INSERT INTO Appointment_History (history_date, appointment_date, appointment_slot, staff_id, history_status, history_notes)
            VALUES (NOW(), %s, %s, %s, 'feedback', %s)
            """, (date_obj, time_obj, staff_id, f"Rating: {rating}, Reason: {reason}, Comments: {comments}"))
        
        # Return success template
        return render_template("/calendar_user/feedback_success.html", app_name=APP_NAME)
    except Exception as e:
        # Handle errors gracefully
        return render_template("/calendar_user/feedback_error.html", 
                              app_name=APP_NAME, 
                              error=str(e))
