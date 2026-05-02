from datetime import datetime, timedelta
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app


def hash_password(password):
    return generate_password_hash(password)


def verify_password(password, hashed_password):
    return check_password_hash(hashed_password, password)

def create_access_token(user):
    now = datetime.utcnow()

    payload = {
        "user_id": user.id,
        "role": user.role,
        "iat": now,
        "exp": now + timedelta(hours=24),
        "type": "access"
    }

    return jwt.encode(
        payload,
        current_app.config["JWT_SECRET"],
        algorithm="HS256"
    )


def create_monitoring_token(user):
    now = datetime.utcnow()

    payload = {
        "user_id": user.id,
        "role": user.role,
        "iat": now,
        "exp": now + timedelta(hours=1),
        "type": "monitoring"
    }

    return jwt.encode(
        payload,
        current_app.config["JWT_SECRET"],
        algorithm="HS256"
    )