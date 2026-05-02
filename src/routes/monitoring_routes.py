from flask import Blueprint, jsonify, request, current_app, g
import jwt
from src.models import Attendance, Session, User

monitoring_bp = Blueprint("monitoring", __name__)


def monitoring_token_required(fn):
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing monitoring token"}), 401

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(
                token,
                current_app.config["JWT_SECRET"],
                algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Monitoring token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid monitoring token"}), 401

        if payload.get("role") != "monitoring_officer":
            return jsonify({"error": "Invalid role for monitoring token"}), 401

        if payload.get("type") != "monitoring":
            return jsonify({"error": "Use monitoring token, not login token"}), 401

        g.current_user = payload
        return fn(*args, **kwargs)

    wrapper.__name__ = fn.__name__
    return wrapper


@monitoring_bp.get("/monitoring/attendance")
@monitoring_token_required
def monitoring_attendance():
    records = Attendance.query.all()

    result = []

    for record in records:
        session = Session.query.get(record.session_id)
        student = User.query.get(record.student_id)

        result.append({
            "attendance_id": record.id,
            "session_id": record.session_id,
            "session_title": session.title if session else None,
            "student_id": record.student_id,
            "student_name": student.name if student else None,
            "status": record.status,
            "marked_at": record.marked_at.isoformat()
        })

    return jsonify({
        "total": len(result),
        "attendance": result
    }), 200