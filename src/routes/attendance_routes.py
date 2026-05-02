from flask import Blueprint, request, jsonify, g
from extensions import db
from models import Session, Attendance, User
from decorators import role_required

attendance_bp = Blueprint("attendance", __name__)


@attendance_bp.post("/attendance/mark")
@role_required("student")
def mark_attendance():
    data = request.get_json()

    required = ["session_id", "status"]
    missing = [field for field in required if not data.get(field)]

    if missing:
        return jsonify({"error": "Missing required fields", "missing": missing}), 422

    if data["status"] not in ["present", "absent", "late"]:
        return jsonify({"error": "Invalid status. Use present, absent, or late"}), 422

    session = Session.query.get(data["session_id"])

    if not session:
        return jsonify({"error": "Session not found"}), 404

    student = User.query.get(g.current_user["user_id"])

    if not student:
        return jsonify({"error": "Student not found"}), 404

    enrolled_batch_ids = [batch.id for batch in student.student_batches]

    if session.batch_id not in enrolled_batch_ids:
        return jsonify({"error": "Student is not enrolled in this session's batch"}), 403

    existing = Attendance.query.filter_by(
        session_id=session.id,
        student_id=student.id
    ).first()

    if existing:
        existing.status = data["status"]
        db.session.commit()

        return jsonify({
            "message": "Attendance updated",
            "attendance": {
                "id": existing.id,
                "session_id": existing.session_id,
                "student_id": existing.student_id,
                "status": existing.status,
                "marked_at": existing.marked_at.isoformat()
            }
        }), 200

    attendance = Attendance(
        session_id=session.id,
        student_id=student.id,
        status=data["status"]
    )

    db.session.add(attendance)
    db.session.commit()

    return jsonify({
        "message": "Attendance marked",
        "attendance": {
            "id": attendance.id,
            "session_id": attendance.session_id,
            "student_id": attendance.student_id,
            "status": attendance.status,
            "marked_at": attendance.marked_at.isoformat()
        }
    }), 201