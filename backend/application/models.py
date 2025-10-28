"""
SQLAlchemy models for Smart Expense Tracker.

Assumes `application.database` defines `db = SQLAlchemy()` and the Flask app
initializes it before use.

Models:
- User
- Category
- Transaction
- MLModel (metadata for saved ML pipelines)
- AuditLog (simple audit trail; optional)
- RefreshToken (if you want to implement refresh tokens later)
"""

from datetime import datetime, timedelta
from typing import Optional
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.sqlite import JSON as JSONType  # falls back to TEXT if not available
from werkzeug.security import generate_password_hash, check_password_hash
from application.database import db
import secrets

# small helpers / mixins -----------------------------------------------------
class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        index=True,
    )


class SoftDeleteMixin:
    is_deleted = db.Column(db.Boolean, default=False, nullable=False, index=True)
    deleted_at = db.Column(db.DateTime, nullable=True)


# models --------------------------------------------------------------------
class User(db.Model, TimestampMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    # simple role system (user / admin) - can expand to Role table if needed
    role = db.Column(db.String(32), default="user", nullable=False, index=True)
    # prefer country/currency prefs later
    currency = db.Column(db.String(8), default="INR", nullable=False)

    # relationships
    transactions = db.relationship(
        "Transaction", back_populates="user", cascade="all, delete-orphan", lazy="dynamic"
    )
    categories = db.relationship(
        "Category", back_populates="user", cascade="all, delete-orphan", lazy="dynamic"
    )
    ml_models = db.relationship("MLModel", back_populates="owner", lazy="dynamic")

    def set_password(self, password: str) -> None:
        """Store a salted password hash."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self, public: bool = True):
        data = {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "is_active": self.is_active,
            "role": self.role,
            "currency": self.currency,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if not public:
            data["password_hash"] = self.password_hash
        return data

    def __repr__(self):
        return f"<User id={self.id} email={self.email}>"


class Category(db.Model, TimestampMixin):
    __tablename__ = "categories"
    __table_args__ = (
        # allow global categories to exist (user_id NULL) but names unique per owner or globally unique
        db.Index("ix_category_user_name", "user_id", "name", unique=True),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    # null => global category available to all users
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    color = db.Column(db.String(7), nullable=True)  # hex color like #FF8800
    description = db.Column(db.Text, nullable=True)

    user = db.relationship("User", back_populates="categories")
    transactions = db.relationship("Transaction", back_populates="category", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id,
            "color": self.color,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        owner = "global" if self.user_id is None else f"user={self.user_id}"
        return f"<Category id={self.id} name={self.name} owner={owner}>"


class Transaction(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "transactions"
    __table_args__ = (
        db.Index("ix_txn_user_date", "user_id", "date"),
        db.Index("ix_txn_user_category", "user_id", "category_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(8), nullable=False, default="INR")
    # optional relation to Category; allow null for Uncategorized
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True, index=True)
    note = db.Column(db.String(512), nullable=True)
    vendor = db.Column(db.String(255), nullable=True)
    # date of the transaction (user-specified). Keep timezone naive UTC assumption for now.
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    is_recurring = db.Column(db.Boolean, default=False, nullable=False, index=True)
    # recurrence rule as simple RFC5545-like string or JSON in future
    recurrence_rule = db.Column(db.String(255), nullable=True)
    # any extra metadata (tags, raw parsed ML suggestions, source="web"|"cli")
    meta_data = db.Column(JSONType, nullable=True)

    # relationships
    user = db.relationship("User", back_populates="transactions")
    category = db.relationship("Category", back_populates="transactions")

    def to_dict(self, include_user: bool = False):
        d = {
            "id": self.id,
            "user_id": self.user_id,
            "amount": float(self.amount) if self.amount is not None else None,
            "currency": self.currency,
            "category_id": self.category_id,
            "category": self.category.name if self.category else None,
            "note": self.note,
            "vendor": self.vendor,
            "date": self.date.isoformat() if self.date else None,
            "is_recurring": self.is_recurring,
            "recurrence_rule": self.recurrence_rule,
            "meta_data": self.meta_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_deleted": self.is_deleted,
        }
        if include_user:
            d["user"] = self.user.to_dict() if self.user else None
        return d

    def __repr__(self):
        return f"<Transaction id={self.id} user={self.user_id} amount={self.amount} date={self.date.date()}>"


class MLModel(db.Model, TimestampMixin):
    """
    Metadata record for ML model artifacts used by the app (e.g. auto-categorizer).
    Storing training params/metrics here helps auditing in the UI and re-loading models.
    """
    __tablename__ = "ml_models"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    version = db.Column(db.String(64), nullable=False, default="v1")
    description = db.Column(db.Text, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    # store evaluation metrics and params as JSON
    meta_data = db.Column(JSONType, nullable=True)
    # path or URI to the model artifact (file path, S3 URI, etc)
    artifact_path = db.Column(db.String(1024), nullable=True)

    owner = db.relationship("User", back_populates="ml_models")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "owner_id": self.owner_id,
            "meta_data": self.meta_data,
            "artifact_path": self.artifact_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<MLModel id={self.id} name={self.name} version={self.version}>"


class AuditLog(db.Model):
    """
    Lightweight audit table for important admin actions (backups, model training, destructive cleanup).
    """
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    action = db.Column(db.String(255), nullable=False)
    details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    actor = db.relationship("User", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "actor_id": self.actor_id,
            "action": self.action,
            "details": self.details,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self):
        return f"<AuditLog id={self.id} action={self.action} actor={self.actor_id}>"

# Optional: RefreshToken model (useful if you implement refresh flow)
class RefreshToken(db.Model, TimestampMixin):
    __tablename__ = "refresh_tokens"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    token = db.Column(db.String(512), nullable=False, unique=True, index=True)
    revoked = db.Column(db.Boolean, default=False, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", lazy="joined")

    def __repr__(self):
        return f"<RefreshToken id={self.id} user={self.user_id} revoked={self.revoked}>"



class TokenBlocklist(db.Model):
    """
    Store revoked JWT jti values so we can reject them.
    Fields:
      - jti: unique identifier of JWT (we place jti into tokens)
      - token_type: 'access' or 'refresh' (optional)
      - revoked_at: when it was revoked
      - expires_at: when token naturally expires (optional, for cleanup)
      - user_id: optional FK
    """
    __tablename__ = "token_blocklist"

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(255), unique=True, nullable=False, index=True)
    token_type = db.Column(db.String(20), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    revoked_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<TokenBlocklist jti={self.jti} user={self.user_id} revoked_at={self.revoked_at}>"


class PasswordResetToken(db.Model):
    """
    One-time password reset tokens. We store a hashed token so raw token cannot be read from DB.
    Fields:
      - token_hash: hashed token (use werkzeug generate_password_hash)
      - user_id: FK
      - expires_at: datetime
      - used: bool
      - created_at
    """
    __tablename__ = "password_reset_tokens"

    id = db.Column(db.Integer, primary_key=True)
    token_hash = db.Column(db.String(512), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    used = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", lazy="joined")

    @classmethod
    def create_token(cls, user, expire_minutes: int = 30):
        """
        Create a token string and persist its hash. Returns raw token (for emailing) and instance.
        """
        raw = secrets.token_urlsafe(32)
        token_hash = generate_password_hash(raw)
        expires_at = datetime.utcnow() + timedelta(minutes=expire_minutes)
        prt = cls(token_hash=token_hash, user_id=user.id, expires_at=expires_at)
        db.session.add(prt)
        db.session.commit()
        return raw, prt

    def verify_and_mark_used(self, token_raw: str):
        """
        Verify raw token, mark as used and commit if valid.
        """
        if self.used:
            return False
        if datetime.utcnow() > self.expires_at:
            return False
        if not check_password_hash(self.token_hash, token_raw):
            return False
        self.used = True
        db.session.add(self)
        db.session.commit()
        return True

    def __repr__(self):
        return f"<PasswordResetToken id={self.id} user={self.user_id} used={self.used}>"