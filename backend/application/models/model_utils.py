"""
Helper functions for interacting with models and database sessions.
Shared between APIs and CLI scripts.
"""

from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from application.database import db
from backend.application.models.models import User, Transaction, Category


# --------------------------- User Helpers ---------------------------
def get_user_by_email(email: str):
    return User.query.filter_by(email=email).first()


def create_user(name: str, email: str, password: str, role: str = "user", currency: str = "INR"):
    """Creates and commits a new user."""
    try:
        user = User(name=name, email=email, role=role, currency=currency)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error creating user: {e}")


# --------------------------- Category Helpers ---------------------------
def get_or_create_category(name: str, user_id: int = None, color: str = None):
    """Return an existing category or create it."""
    cat = Category.query.filter_by(name=name, user_id=user_id).first()
    if cat:
        return cat
    cat = Category(name=name, user_id=user_id, color=color)
    db.session.add(cat)
    db.session.commit()
    return cat


# --------------------------- Transaction Helpers ---------------------------
def add_transaction(user_id: int, amount: float, note: str = "", category_id: int = None,
                    vendor: str = None, date: datetime = None, is_recurring: bool = False,
                    recurrence_rule: str = None, metadata: dict = None):
    """Add a transaction for a user."""
    try:
        txn = Transaction(
            user_id=user_id,
            amount=amount,
            note=note,
            category_id=category_id,
            vendor=vendor,
            date=date or datetime.utcnow(),
            is_recurring=is_recurring,
            recurrence_rule=recurrence_rule,
            metadata=metadata,
        )
        db.session.add(txn)
        db.session.commit()
        return txn
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error adding transaction: {e}")


def get_user_transactions(user_id: int, start_date=None, end_date=None, include_deleted=False):
    """Retrieve transactions with optional date range filters."""
    query = Transaction.query.filter_by(user_id=user_id)
    if not include_deleted:
        query = query.filter_by(is_deleted=False)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    return query.order_by(Transaction.date.desc()).all()


def delete_transaction(txn_id: int, soft_delete=True):
    """Soft-delete or permanently delete a transaction."""
    txn = Transaction.query.get(txn_id)
    if not txn:
        return None
    try:
        if soft_delete:
            txn.is_deleted = True
            txn.deleted_at = datetime.utcnow()
        else:
            db.session.delete(txn)
        db.session.commit()
        return txn
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error deleting transaction: {e}")


# --------------------------- Utility ---------------------------
def commit_session():
    """Safe commit wrapper."""
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"DB commit failed: {e}")
