from flask_restful import Resource
from flask import request, jsonify
from ...models.models import User
from application.database import db
from ..auth.auth_utils import token_required, role_required


class UserProfile(Resource):
    """
    Get or update the current user's own profile.
    """

    @token_required
    def get(self):
        user = request.user
        return {"user": user.to_dict()}, 200

    @token_required
    def put(self):
        user = request.user
        data = request.get_json() or {}
        name = data.get("name")
        email = data.get("email")

        # Allow name/email change
        if name:
            user.name = name.strip()
        if email and email != user.email:
            if User.query.filter_by(email=email).first():
                return {"message": "Email already taken"}, 409
            user.email = email.strip()

        db.session.commit()
        return {"message": "Profile updated", "user": user.to_dict()}, 200


class UserPasswordChange(Resource):
    """
    Allow logged-in user to change password (with current password verification).
    """

    @token_required
    def post(self):
        user = request.user
        data = request.get_json() or {}
        old_pw = data.get("old_password")
        new_pw = data.get("new_password")
        if not (old_pw and new_pw):
            return {"message": "old_password and new_password required"}, 400

        if not user.check_password(old_pw):
            return {"message": "Old password incorrect"}, 403

        user.set_password(new_pw)
        db.session.commit()
        return {"message": "Password changed successfully"}, 200


class UserList(Resource):
    """
    Admin-only list and create users.
    """

    @role_required("admin")
    def get(self):
        users = User.query.all()
        return {"users": [u.to_dict() for u in users]}, 200

    @role_required("admin")
    def post(self):
        data = request.get_json() or {}
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        role = data.get("role", "user")

        if not (name and email and password):
            return {"message": "name, email, password required"}, 400

        if User.query.filter_by(email=email).first():
            return {"message": "Email already exists"}, 409

        new_user = User(name=name, email=email, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return {"message": "User created", "user": new_user.to_dict()}, 201


class UserDetail(Resource):
    """
    Admin-only: view, update, or delete another user.
    """

    @role_required("admin")
    def get(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {"message": "User not found"}, 404
        return {"user": user.to_dict()}, 200

    @role_required("admin")
    def put(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {"message": "User not found"}, 404

        data = request.get_json() or {}
        name = data.get("name")
        email = data.get("email")
        role = data.get("role")

        if name:
            user.name = name.strip()
        if email and email != user.email:
            if User.query.filter_by(email=email).first():
                return {"message": "Email already taken"}, 409
            user.email = email.strip()
        if role:
            user.role = role

        db.session.commit()
        return {"message": "User updated", "user": user.to_dict()}, 200

    @role_required("admin")
    def delete(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {"message": "User not found"}, 404
        db.session.delete(user)
        db.session.commit()
        return {"message": f"User {user_id} deleted"}, 200
