from flask import Blueprint, request, jsonify, g
from src.extensions import db
from src.models import Batch, BatchInvite, User
from src.decorators import role_required
from datetime import datetime, timedelta
import uuid

batch_bp = Blueprint("batch", __name__)


@batch_bp.post("/batches")
@role_required("trainer", "institution")
def create_batch():
    data = request.get_json()

    if not data or not data.get("name"):
        return jsonify({"error": "Batch name is required"}), 422

    batch = Batch(
        name=data["name"],
        institution_id=data.get("institution_id", 1)
    )

    db.session.add(batch)
    db.session.commit()

    return jsonify({
        "message": "Batch created",
        "batch": {
            "id": batch.id,
            "name": batch.name
        }
    }), 201


@batch_bp.post("/batches/<int:batch_id>/invite")
@role_required("trainer")
def create_batch_invite(batch_id):
    batch = Batch.query.get(batch_id)

    if not batch:
        return jsonify({"error": "Batch not found"}), 404

    token = str(uuid.uuid4())

    invite = BatchInvite(
        batch_id=batch.id,
        token=token,
        created_by=g.current_user["user_id"],
        expires_at=datetime.utcnow() + timedelta(days=7),
        used=False
    )

    db.session.add(invite)
    db.session.commit()

    return jsonify({
        "message": "Invite created",
        "invite_token": token,
        "expires_at": invite.expires_at.isoformat()
    }), 201


@batch_bp.post("/batches/join")
@role_required("student")
def join_batch():
    data = request.get_json()

    if not data or not data.get("token"):
        return jsonify({"error": "Invite token is required"}), 422

    invite = BatchInvite.query.filter_by(token=data["token"]).first()

    if not invite:
        return jsonify({"error": "Invalid invite token"}), 404

    if invite.used:
        return jsonify({"error": "Invite already used"}), 400

    if invite.expires_at < datetime.utcnow():
        return jsonify({"error": "Invite expired"}), 400

    batch = Batch.query.get(invite.batch_id)
    student = User.query.get(g.current_user["user_id"])

    if not batch:
        return jsonify({"error": "Batch not found"}), 404

    if student in batch.students:
        return jsonify({"error": "Student already joined this batch"}), 409

    batch.students.append(student)
    invite.used = True

    db.session.commit()

    return jsonify({
        "message": "Joined batch successfully",
        "batch": {
            "id": batch.id,
            "name": batch.name
        }
    }), 200