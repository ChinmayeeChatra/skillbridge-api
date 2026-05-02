from flask import Blueprint, jsonify
from src.models import Batch, Session, Attendance
from src.decorators import role_required

summary_bp = Blueprint("summary", __name__)


@summary_bp.get("/batches/<int:batch_id>/summary")
@role_required("institution")
def batch_summary(batch_id):
    batch = Batch.query.get(batch_id)

    if not batch:
        return jsonify({"error": "Batch not found"}), 404

    sessions = Session.query.filter_by(batch_id=batch_id).all()
    session_ids = [session.id for session in sessions]

    records = Attendance.query.filter(Attendance.session_id.in_(session_ids)).all() if session_ids else []

    summary = {
        "batch_id": batch.id,
        "batch_name": batch.name,
        "total_sessions": len(sessions),
        "total_attendance_records": len(records),
        "present": len([r for r in records if r.status == "present"]),
        "absent": len([r for r in records if r.status == "absent"]),
        "late": len([r for r in records if r.status == "late"])
    }

    return jsonify(summary), 200


@summary_bp.get("/institutions/<int:institution_id>/summary")
@role_required("programme_manager")
def institution_summary(institution_id):
    batches = Batch.query.filter_by(institution_id=institution_id).all()

    batch_ids = [batch.id for batch in batches]
    sessions = Session.query.filter(Session.batch_id.in_(batch_ids)).all() if batch_ids else []
    session_ids = [session.id for session in sessions]

    records = Attendance.query.filter(Attendance.session_id.in_(session_ids)).all() if session_ids else []

    summary = {
        "institution_id": institution_id,
        "total_batches": len(batches),
        "total_sessions": len(sessions),
        "total_attendance_records": len(records),
        "present": len([r for r in records if r.status == "present"]),
        "absent": len([r for r in records if r.status == "absent"]),
        "late": len([r for r in records if r.status == "late"])
    }

    return jsonify(summary), 200


@summary_bp.get("/programme/summary")
@role_required("programme_manager")
def programme_summary():
    batches = Batch.query.all()
    sessions = Session.query.all()
    records = Attendance.query.all()

    summary = {
        "total_batches": len(batches),
        "total_sessions": len(sessions),
        "total_attendance_records": len(records),
        "present": len([r for r in records if r.status == "present"]),
        "absent": len([r for r in records if r.status == "absent"]),
        "late": len([r for r in records if r.status == "late"])
    }

    return jsonify(summary), 200