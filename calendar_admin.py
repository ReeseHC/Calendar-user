from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

bp = Blueprint('calendar_admin', __name__)

from . import alchemy

# Model without explicit id field
class Schedule(alchemy.Model):
    schedule_day = alchemy.Column(alchemy.Date, nullable=False, primary_key=True)
    schedule_slot = alchemy.Column(alchemy.Time, nullable=False, primary_key=True)
    staff_id = alchemy.Column(alchemy.Integer, nullable=False, primary_key=True)
    location_id = alchemy.Column(alchemy.Integer, nullable=False)

    def __repr__(self):
        return f"<Schedule {self.schedule_day} {self.schedule_slot} {self.staff_id}>"

@bp.route('/admin')
def home():
    return render_template('/calendar_admin/calendar.html')

# Routes
@bp.route('/admin/schedule', methods=['POST'])
def create_schedule():
    data = request.get_json()
    required_fields = ['schedule_day', 'schedule_slot', 'staff_id', 'location_id']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing required field: {field}'}), 400

    try:
        schedule_day = datetime.strptime(data['schedule_day'], '%Y-%m-%d').date()
        schedule_slot = datetime.strptime(data['schedule_slot'], '%H:%M:%S').time()
    except ValueError as e:
        return jsonify({'message': f'Invalid date/time format. {str(e)}'}), 400

    # Using the composite primary key for existence check
    existing = Schedule.query.filter_by(
        schedule_day=schedule_day,
        schedule_slot=schedule_slot,
        staff_id=data['staff_id']
    ).first()

    if existing:
        return jsonify({'message': 'Schedule already exists for this staff on this day and time.'}), 400

    new_schedule = Schedule(
        schedule_day=schedule_day,
        schedule_slot=schedule_slot,
        staff_id=data['staff_id'],
        location_id=data['location_id']
    )

    alchemy.session.add(new_schedule)
    alchemy.session.commit()

    return jsonify({
        'schedule_day': new_schedule.schedule_day.isoformat(),
        'schedule_slot': new_schedule.schedule_slot.strftime('%H:%M:%S'),
        'staff_id': new_schedule.staff_id,
        'location_id': new_schedule.location_id
    }), 201

@bp.route('/admin/schedule', methods=['GET'])
def get_schedules():
    date = request.args.get('date')
    query = Schedule.query
    
    if date:
        try:
            schedule_day = datetime.strptime(date, '%Y-%m-%d').date()
            query = query.filter(Schedule.schedule_day == schedule_day)
        except ValueError:
            return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    schedules = query.all()
    return jsonify([{
        'schedule_day': s.schedule_day.isoformat(),
        'schedule_slot': s.schedule_slot.strftime('%H:%M:%S'),
        'staff_id': s.staff_id,
        'location_id': s.location_id
    } for s in schedules])

@bp.route('/admin/schedule', methods=['DELETE'])
def delete_schedule():
    data = request.get_json()
    required_fields = ['schedule_day', 'schedule_slot', 'staff_id']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing required field: {field}'}), 400

    try:
        schedule_day = datetime.strptime(data['schedule_day'], '%Y-%m-%d').date()
        schedule_slot = datetime.strptime(data['schedule_slot'], '%H:%M:%S').time()
    except ValueError as e:
        return jsonify({'message': f'Invalid date/time format. {str(e)}'}), 400

    # Using composite primary key for deletion
    schedule = Schedule.query.filter_by(
        schedule_day=schedule_day,
        schedule_slot=schedule_slot,
        staff_id=data['staff_id']
    ).first()

    if not schedule:
        return jsonify({'message': 'Schedule not found'}), 404

    alchemy.session.delete(schedule)
    alchemy.session.commit()
    return jsonify({'message': 'Schedule deleted successfully'})