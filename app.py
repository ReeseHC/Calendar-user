from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
from datetime import datetime

app = Flask(__name__)

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
    return render_template("calendar.html")

@app.route("/schedule.html")
def schedule():
    date = request.args.get('date', '')
    
    # Get appointment data for this date
    date_data = appointment_data.get(date, {"booked": 0, "open": 0})
    
    # Initialize appointment details for this date if needed
    if date not in appointment_details and (date_data["booked"] > 0 or date_data["open"] > 0):
        appointment_details[date] = {}
        
        # Create booked appointments
        for i in range(date_data["booked"]):
            time_slot = f"{9 + i}:00"
            appointment_details[date][time_slot] = {"status": "booked"}
        
        # Create open appointments
        for i in range(date_data["open"]):
            time_slot = f"{1 + i}:00"
            appointment_details[date][time_slot] = {"status": "open"}
    
    return render_template("schedule.html", date=date, appointments=date_data)

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
        
        return jsonify({"success": True})
    else:
        # If the time wasn't found but we have capacity for open appointments
        if time not in appointment_details.get(date, {}):
            appointment_details[date][time] = {"status": "booked"}
            appointment_data[date]["booked"] += 1
            return jsonify({"success": True})
        
        return jsonify({"success": False, "error": "Appointment not available"}), 400

@app.route("/api/cancel-appointment", methods=["POST"])
def cancel_appointment():
    """API endpoint to cancel an appointment"""
    data = request.json
    date = data.get("date")
    time = data.get("time")
    
    if not date or not time:
        return jsonify({"success": False, "error": "Missing date or time"}), 400
    
    # Check if appointment exists and is booked
    if date in appointment_details and time in appointment_details[date] and appointment_details[date][time]["status"] == "booked":
        # Update the appointment status
        appointment_details[date][time]["status"] = "open"
        
        # Update counts
        appointment_data[date]["booked"] -= 1
        appointment_data[date]["open"] += 1
        
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Appointment not found or not booked"}), 400

if __name__ == "__main__":
    app.run(debug=True)