# application/api/auth_api.py

from flask import request, jsonify
from flask_restful import Resource
from ...models.models import User
from application.database import db
import jwt
import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash

SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")


# application/api/auth_api.py

from flask_restful import Resource
from flask import request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from ...models.models import User, PasswordResetToken, TokenBlocklist
from application.database import db
from .auth_utils import (
    create_access_token,
    create_refresh_token,
    decode_token,
    revoke_token,
    token_required,
    role_required,
    is_jti_revoked
)
import datetime
import os

# Configs (fallback defaults)
ACCESS_EXPIRES_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRES_MIN", 60))
REFRESH_EXPIRES_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRES_DAYS", 7))


class Register(Resource):
    def post(self):
        data = request.get_json() or {}
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        if not (name and email and password):
            return {"message": "name, email and password required"}, 400

        if User.query.filter_by(email=email).first():
            return {"message": "Email already registered"}, 409

        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return {"message": "registered", "user": user.to_dict()}, 201


class Login(Resource):
    def post(self):
        data = request.get_json() or {}
        email = data.get("email")
        password = data.get("password")
        if not (email and password):
            return {"message": "email and password required"}, 400

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return {"message": "invalid credentials"}, 401

        access_token, access_jti, access_exp = create_access_token(user.id, additional_claims={"role": user.role})
        refresh_token, refresh_jti, refresh_exp = create_refresh_token(user.id)

        # Optionally store refresh_jti in DB (we're not creating a separate refresh model here, but you can)
        # For now we'll not persist refresh tokens but we do allow revocation via blocklist.

        return {
            "message": "ok",
            "access_token": access_token,
            "access_expires": access_exp.isoformat(),
            "refresh_token": refresh_token,
            "refresh_expires": refresh_exp.isoformat(),
            "user": user.to_dict()
        }, 200


class Logout(Resource):
    @token_required
    def post(self):
        """
        Revoke the provided access token (put into blocklist). Also optionally revoke refresh token if provided.
        Body (optional): {"revoke_refresh_token": "<refresh_jti_or_token>"}
        """
        auth = request.headers.get("Authorization", "")
        token = auth.split(" ", 1)[1].strip()
        payload = decode_token(token)
        jti = payload.get("jti")
        exp = datetime.datetime.utcfromtimestamp(payload.get("exp")) if payload.get("exp") else None
        revoke_token(jti=jti, user_id=payload.get("user_id"), token_type=payload.get("type", "access"), expires_at=exp)

        # optionally handle refresh token revocation if refresh token provided in body
        data = request.get_json() or {}
        refresh = data.get("refresh_token")
        if refresh:
            try:
                ref_payload = decode_token(refresh)
                revoke_token(jti=ref_payload.get("jti"), user_id=ref_payload.get("user_id"), token_type="refresh",
                             expires_at=datetime.datetime.utcfromtimestamp(ref_payload.get("exp")))
            except Exception:
                pass

        return {"message": "tokens revoked"}, 200


class Refresh(Resource):
    """
    Refresh access token using refresh token provided in body.
    POST /api/token/refresh
    body: {"refresh_token": "<token>"}
    """
    def post(self):
        data = request.get_json() or {}
        refresh_token = data.get("refresh_token")
        if not refresh_token:
            return {"message": "refresh_token required"}, 400
        try:
            payload = decode_token(refresh_token)
        except Exception as e:
            return {"message": "invalid or expired refresh token", "detail": str(e)}, 401

        # Ensure token is a refresh token and not revoked
        if payload.get("type") != "refresh":
            return {"message": "token provided is not a refresh token"}, 400
        if is_jti_revoked(payload.get("jti")):
            return {"message": "refresh token revoked"}, 401

        user = User.query.get(payload.get("user_id"))
        if not user:
            return {"message": "user not found"}, 404

        access_token, access_jti, access_exp = create_access_token(user.id, additional_claims={"role": user.role})
        return {"access_token": access_token, "access_expires": access_exp.isoformat()}, 200


class PasswordResetRequest(Resource):
    """
    Request a password reset. Returns a reset token (for dev). In production, email it.
    POST /api/password-reset/request
    body: {"email": "<email>"}
    """
    def post(self):
        data = request.get_json() or {}
        email = data.get("email")
        if not email:
            return {"message": "email required"}, 400
        user = User.query.filter_by(email=email).first()
        if not user:
            # don't reveal whether the user exists — respond with generic message
            return {"message": "If an account with that email exists, a password reset has been requested."}, 200

        raw_token, prt = PasswordResetToken.create_token(user, expire_minutes=int(os.getenv("PASSWORD_RESET_EXPIRE_MIN", 30)))
        # TODO: send `raw_token` by email to user — for dev we return token in response
        # In production, do not return token here; send email and log audit.
        return {
            "message": "password reset requested",
            "reset_token_dev": raw_token,
            "expires_at": prt.expires_at.isoformat()
        }, 200


class PasswordResetConfirm(Resource):
    """
    Confirm password reset using token.
    POST /api/password-reset/confirm
    body: {"token": "<token>", "password": "<new_password>"}
    """
    def post(self):
        data = request.get_json() or {}
        token_raw = data.get("token")
        new_pw = data.get("password")
        if not (token_raw and new_pw):
            return {"message": "token and password required"}, 400

        # find any non-used token that isn't expired, and verify hash
        candidate = PasswordResetToken.query.filter_by(used=False).filter(PasswordResetToken.expires_at >= datetime.datetime.utcnow()).order_by(PasswordResetToken.created_at.desc()).all()
        matched = None
        for prt in candidate:
            if prt.verify_and_mark_used(token_raw):
                matched = prt
                break

        if not matched:
            return {"message": "invalid or expired token"}, 400

        user = matched.user
        user.set_password(new_pw)
        db.session.add(user)
        db.session.commit()

        # optionally revoke all outstanding refresh tokens (force logout everywhere)
        # For simplicity, add blocklist entry for all tokens belonging to user created before now
        # (This is rough; a full implementation would store issued jtis for refresh tokens.)
        return {"message": "password reset successful"}, 200


class AdminOnly(Resource):
    """
    Example admin-only route.
    """
    @role_required("admin")
    def get(self):
        return {"message": "hello admin"}, 200


class Profile(Resource):
    """
    Protected route example — requires valid JWT in Authorization header.
    GET /api/profile
    """

    def get(self):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return {"message": "Missing or invalid Authorization header."}, 401

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user = User.query.get(payload["user_id"])
            if not user:
                return {"message": "User not found."}, 404
        except jwt.ExpiredSignatureError:
            return {"message": "Token expired."}, 401
        except jwt.InvalidTokenError:
            return {"message": "Invalid token."}, 401

        return {"user": user.to_dict()}, 200
