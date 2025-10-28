# application/api/auth_utils.py

import os
import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app
from application.models import User, TokenBlocklist
from application.database import db

# configuration
SECRET_KEY = os.getenv("SECRET_KEY", current_app.config.get("SECRET_KEY") if current_app else os.getenv("SECRET_KEY", "dev_secret_key"))
ACCESS_TOKEN_EXPIRES = int(os.getenv("ACCESS_TOKEN_EXPIRES_MIN", 60))  # minutes
REFRESH_TOKEN_EXPIRES = int(os.getenv("REFRESH_TOKEN_EXPIRES_DAYS", 7))  # days

def _get_secret():
    # lazy fetch to avoid current_app issues on import
    return os.getenv("SECRET_KEY") or (current_app.config.get("SECRET_KEY") if current_app else "dev_secret_key")

def create_access_token(user_id: int, additional_claims: dict = None):
    now = datetime.datetime.utcnow()
    exp = now + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRES)
    jti = jwt.utils.base64url_encode(os.urandom(16)).decode('utf-8')  # random jti
    payload = {
        "user_id": user_id,
        "type": "access",
        "exp": exp,
        "iat": now,
        "jti": jti
    }
    if additional_claims:
        payload.update(additional_claims)
    token = jwt.encode(payload, _get_secret(), algorithm="HS256")
    return token, jti, exp

def create_refresh_token(user_id: int):
    now = datetime.datetime.utcnow()
    exp = now + datetime.timedelta(days=REFRESH_TOKEN_EXPIRES)
    jti = jwt.utils.base64url_encode(os.urandom(16)).decode('utf-8')
    payload = {
        "user_id": user_id,
        "type": "refresh",
        "exp": exp,
        "iat": now,
        "jti": jti
    }
    token = jwt.encode(payload, _get_secret(), algorithm="HS256")
    return token, jti, exp

def decode_token(token: str):
    try:
        payload = jwt.decode(token, _get_secret(), algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise
    except jwt.InvalidTokenError:
        raise

def is_jti_revoked(jti: str) -> bool:
    if not jti:
        return True
    tb = TokenBlocklist.query.filter_by(jti=jti).first()
    return tb is not None

def revoke_token(jti: str, user_id: int = None, token_type: str = None, expires_at: datetime.datetime = None):
    if is_jti_revoked(jti):
        return
    tb = TokenBlocklist(jti=jti, user_id=user_id, token_type=token_type, expires_at=expires_at)
    db.session.add(tb)
    db.session.commit()

# Decorator to require a valid (non-revoked) access token
def token_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", None)
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"message": "Missing Authorization header (Bearer token required)"}), 401
        token = auth.split(" ", 1)[1].strip()
        try:
            payload = decode_token(token)
        except Exception as e:
            # jwt exceptions will be thrown for expired/invalid
            return jsonify({"message": "Invalid or expired token", "detail": str(e)}), 401

        jti = payload.get("jti")
        if is_jti_revoked(jti):
            return jsonify({"message": "Token has been revoked"}), 401

        # attach user info to request context (flask.g could be used but returning here for simplicity)
        request.user = User.query.get(payload.get("user_id"))
        if not request.user:
            return jsonify({"message": "User not found"}), 404

        return fn(*args, **kwargs)
    return wrapper

# Role-based decorator: requires token + that user has one of accepted roles
def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        @token_required
        def wrapper(*args, **kwargs):
            user = getattr(request, "user", None)
            if not user or user.role not in roles:
                return jsonify({"message": "Forbidden: insufficient privileges"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
