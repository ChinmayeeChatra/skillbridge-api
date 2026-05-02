from flask import Blueprint, request, jsonify, g
from datetime import datetime
from src.extensions import db
from src.models import Session, Batch, Attendance, User
from src.decorators import role_required

session_bp = Blueprint("session", __name__)


@session_bp.post("/sessions")
@role_required("trainer")
def create_session():
    data = request.get_json()

    required = ["title", "date", "start_time", "end_time", "batch_id"]
    missing = [field for field in required if not data.get(field)]

    if missing:
        return jsonify({"error": "Missing required fields", "missing": missing}), 422

    batch = Batch.query.get(data["batch_id"])

    if not batch:
        return jsonify({"error": "Batch not found"}), 404

    try:
        session = Session(
            title=data["title"],
            date=datetime.strptime(data["date"], "%Y-%m-%d").date(),
            start_time=datetime.strptime(data["start_time"], "%H:%M").time(),
            end_time=datetime.strptime(data["end_time"], "%H:%M").time(),
            batch_id=data["batch_id"],
            trainer_id=g.current_user["user_id"]
        )
    except ValueError:
        return jsonify({
            "error": "Invalid date or time format. Use date YYYY-MM-DD and time HH:MM"
        }), 422

    db.session.add(session)
    db.session.commit()

    return jsonify({
        "message": "Session created",
        "session": {
            "id": session.id,
            "title": session.title,
            "batch_id": session.batch_id,
            "trainer_id": session.trainer_id,
            "date": session.date.isoformat(),
            "start_time": session.start_time.strftime("%H:%M"),
            "end_time": session.end_time.strftime("%H:%M")
        }
    }), 201


@session_bp.get("/sessions/<int:session_id>/attendance")
@role_required("trainer")
def get_session_attendance(session_id):
    session = Session.query.get(session_id)

    if not session:
        return jsonify({"error": "Session not found"}), 404

    records = Attendance.query.filter_by(session_id=session_id).all()

    result = []

    for record in records:
        student = User.query.get(record.student_id)

        result.append({
            "attendance_id": record.id,
            "student_id": record.student_id,
            "student_name": student.name if student else None,
            "status": record.status,
            "marked_at": record.marked_at.isoformat()
        })

    return jsonify({
        "session_id": session.id,
        "title": session.title,
        "attendance": result
    }), 200