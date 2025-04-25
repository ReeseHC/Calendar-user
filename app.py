from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
from datetime import datetime

app = Flask(__name__, static_folder='Static')

# App name
APP_NAME = "Calendar-Schedule App"

# Example appointment data - in a real app, this would come from a database
appointment_data = {
    "2025-04-15": {"booked": 2, "open": 1},
    "2025-04-16": {"booked": 1, "open": 3},
    "2025-04-18": {"booked": 3, "open": 0},
    "2025-04-20": {"booked": 0, "open": 2},
    "2025-04-25": {"booked": 1, "open": 1},
    "2025-05-02": {"booked": 2, "open": 2},
    "2025-05-10": {"booked": 1, "open": 0}
}

# This would be a database in a real application
appointment_details = {
    # Format: "YYYY-MM-DD": { "time": {"status": "booked|open"} }
    "2025-04-15": {
        "9:00": {"status": "booked"},
        "10:00": {"status": "booked"},
        "1:00": {"status": "open"}
    },
    "2025-04-16": {
        "9:00": {"status": "booked"},
        "1:00": {"status": "open"},
        "2:00": {"status": "open"},
        "3:00": {"status": "open"}
    }
    # Other dates would be initialized when first accessed
}

@app.route("/")
def calendar():
    return render_template("calendar.html", app_name=APP_NAME)

@app.route("/schedule.html")
def schedule():
    date = request.args.get('date', '')
    
    # Get appointment data for this date
    date_data = appointment_data.get(date, {"booked": 0, "open": 0})
    
    # Initialize appointment details for this date if needed
    if date not in appointment_details and (date_data["booked"] > 0 or date_data["open"] > 0):
        appointment_details[date] = {}
        
        # Create booked appointments - make sure times don't overlap
        hour = 9  # Start at 9 AM
        for i in range(date_data["booked"]):
            time_slot = f"{hour}:00"
            appointment_details[date][time_slot] = {"status": "booked"}
            hour += 1  # Increment by 1 hour
        
        # Create open appointments - start after booked appointments to avoid overlap
        for i in range(date_data["open"]):
            time_slot = f"{hour}:00"
            appointment_details[date][time_slot] = {"status": "open"}
            hour += 1  # Increment by 1 hour
    
    # Get detailed schedule for the date
    date_details = appointment_details.get(date, {})
    
    return render_template("schedule.html", date=date, appointments=date_data, 
                         appointment_details=date_details, app_name=APP_NAME)

@app.route("/api/appointments")
def get_appointments():
    """API endpoint to get appointment data"""
    return jsonify(appointment_data)

@app.route("/api/appointments/<date>")
def get_appointment_by_date(date):
    """API endpoint to get appointment data for a specific date"""
    if date in appointment_data:
        return jsonify(appointment_data[date])
    else:
        return jsonify({"booked": 0, "open": 0})

@app.route("/api/book-appointment", methods=["POST"])
def book_appointment():
    """API endpoint to book an appointment"""
    data = request.json
    date = data.get("date")
    time = data.get("time")
    
    if not date or not time:
        return jsonify({"success": False, "error": "Missing date or time"}), 400
    
    # Initialize date if it doesn't exist
    if date not in appointment_data:
        appointment_data[date] = {"booked": 0, "open": 0}
    
    if date not in appointment_details:
        appointment_details[date] = {}
    
    # Check if appointment is available
    if time in appointment_details.get(date, {}) and appointment_details[date][time]["status"] == "open":
        # Update the appointment status
        appointment_details[date][time]["status"] = "booked"
        
        # Update counts
        appointment_data[date]["booked"] += 1
        appointment_data[date]["open"] -= 1
        
        return jsonify({"success": True, "message": "Appointment booked successfully!", 
                        "appointments": appointment_data[date]})
    else:
        # If the time wasn't found but we have capacity for open appointments
        if time not in appointment_details.get(date, {}):
            appointment_details[date][time] = {"status": "booked"}
            appointment_data[date]["booked"] += 1
            return jsonify({"success": True, "message": "Appointment booked successfully!", 
                           "appointments": appointment_data[date]})
        
        return jsonify({"success": False, "error": "Appointment not available"}), 400

@app.route("/api/cancel-appointment", methods=["POST"])
def cancel_appointment():
    """API endpoint to cancel an appointment"""
    data = request.json
    date = data.get("date")
    time = data.get("time")
    confirmed = data.get("confirmed", False)
    
    if not date or not time:
        return jsonify({"success": False, "error": "Missing date or time"}), 400
    
    # If not confirmed, just return success so UI can show confirmation dialog
    if not confirmed:
        return jsonify({"success": True, "needsConfirmation": True})
    
    # Check if appointment exists and is booked
    if date in appointment_details and time in appointment_details[date] and appointment_details[date][time]["status"] == "booked":
        # Update the appointment status
        appointment_details[date][time]["status"] = "open"
        
        # Update counts
        appointment_data[date]["booked"] -= 1
        appointment_data[date]["open"] += 1
        
        return jsonify({"success": True, "message": "Appointment cancelled successfully!", 
                       "appointments": appointment_data[date]})
    else:
        return jsonify({"success": False, "error": "Appointment not found or not booked"}), 400

@app.route("/feedback")
def feedback():
    """Feedback form page"""
    date = request.args.get('date', '')
    time = request.args.get('time', '')
    return render_template("feedback.html", date=date, time=time, app_name=APP_NAME)

@app.route("/submit-feedback", methods=["POST"])
def submit_feedback():
    """Handle feedback form submission"""
    # In a real app, this would save the feedback to a database
    feedback_data = {
        "date": request.form.get("date"),
        "time": request.form.get("time"),
        "reason": request.form.get("reason"),
        "comments": request.form.get("comments"),
        "rating": request.form.get("rating")
    }
    
    # Just return success for now
    return render_template("feedback_success.html", app_name=APP_NAME)

if __name__ == "__main__":
    app.run(debug=True)