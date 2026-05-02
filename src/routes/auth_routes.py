from flask import Blueprint, request, jsonify, current_app
import jwt

from src.models import User
from src.extensions import db
from src.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_monitoring_token
)
from src.utils import validate_required

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/auth/signup")
def signup():
    data = request.get_json(silent=True)

    validation_error = validate_required(data, ["name", "email", "password", "role"])
    if validation_error:
        return validation_error

    allowed_roles = [
        "student",
        "trainer",
        "institution",
        "programme_manager",
        "monitoring_officer"
    ]

    if data["role"] not in allowed_roles:
        return jsonify({
            "error": "Invalid role",
            "allowed_roles": allowed_roles
        }), 422

    if "@" not in data["email"]:
        return jsonify({"error": "Invalid email address"}), 422

    existing_user = User.query.filter_by(email=data["email"]).first()
    if existing_user:
        return jsonify({"error": "Email already registered"}), 409

    user = User(
        name=data["name"],
        email=data["email"],
        hashed_password=hash_password(data["password"]),
        role=data["role"],
        institution_id=data.get("institution_id")
    )

    db.session.add(user)
    db.session.commit()

    token = create_access_token(user)

    return jsonify({
        "message": "Signup successful",
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }), 201


@auth_bp.post("/auth/login")
def login():
    data = request.get_json(silent=True)

    validation_error = validate_required(data, ["email", "password"])
    if validation_error:
        return validation_error

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not verify_password(data["password"], user.hashed_password):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(user)

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }), 200


@auth_bp.post("/auth/monitoring-token")
def monitoring_token():
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing token"}), 401

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(
            token,
            current_app.config["JWT_SECRET"],
            algorithms=["HS256"]
        )
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

    if payload.get("role") != "monitoring_officer":
        return jsonify({
            "error": "Only monitoring officers can request this token"
        }), 403

    data = request.get_json(silent=True)

    validation_error = validate_required(data, ["key"])
    if validation_error:
        return validation_error

    if data["key"] != current_app.config["MONITORING_API_KEY"]:
        return jsonify({"error": "Invalid monitoring API key"}), 401

    user = User.query.get(payload["user_id"])

    if not user:
        return jsonify({"error": "User not found"}), 404

    monitoring_access_token = create_monitoring_token(user)

    return jsonify({
        "message": "Monitoring token created",
        "token": monitoring_access_token
    }), 200