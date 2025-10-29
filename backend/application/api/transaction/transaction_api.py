from flask import request
from flask_restful import Resource
from datetime import datetime
from sqlalchemy import and_
from application.database import db
from ...models.models import Transaction
from ..auth.auth_utils import token_required



class TransactionListAPI(Resource):
    """
    List all transactions (user-specific unless admin)
    or create a new transaction.
    """

    @token_required
    def get(self):
        user = request.user
        query = Transaction.query.filter_by(is_deleted=False)

        # Role-based visibility
        if user.role != "admin":
            query = query.filter_by(user_id=user.id)

        # Filters
        category_id = request.args.get("category_id", type=int)
        vendor = request.args.get("vendor")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        is_recurring = request.args.get("is_recurring", type=lambda x: x.lower() == "true")

        if category_id:
            query = query.filter(Transaction.category_id == category_id)
        if vendor:
            query = query.filter(Transaction.vendor.ilike(f"%{vendor}%"))
        if start_date or end_date:
            try:
                if start_date:
                    sd = datetime.fromisoformat(start_date)
                    query = query.filter(Transaction.date >= sd)
                if end_date:
                    ed = datetime.fromisoformat(end_date)
                    query = query.filter(Transaction.date <= ed)
            except ValueError:
                return {"message": "Invalid date format. Use ISO 8601 (YYYY-MM-DD)."}, 400
        if is_recurring is not None:
            query = query.filter(Transaction.is_recurring == is_recurring)

        # Optional pagination helper
        transactions = query.order_by(Transaction.date.desc()).all()
        return {"transactions": [t.to_dict() for t in transactions]}, 200

    @token_required
    def post(self):
        user = request.user
        data = request.get_json() or {}

        try:
            amount = float(data.get("amount"))
        except (ValueError, TypeError):
            return {"message": "Amount must be a valid number."}, 400

        currency = data.get("currency", "INR")
        category_id = data.get("category_id")
        note = data.get("note")
        vendor = data.get("vendor")
        date_str = data.get("date")
        is_recurring = data.get("is_recurring", False)
        recurrence_rule = data.get("recurrence_rule")
        meta_data = data.get("meta_data")

        try:
            date = datetime.fromisoformat(date_str) if date_str else datetime.utcnow()
        except ValueError:
            return {"message": "Invalid date format."}, 400

        txn = Transaction(
            user_id=user.id,
            amount=amount,
            currency=currency,
            category_id=category_id,
            note=note,
            vendor=vendor,
            date=date,
            is_recurring=is_recurring,
            recurrence_rule=recurrence_rule,
            meta_data=meta_data,
        )

        db.session.add(txn)
        db.session.commit()

        return {"message": "Transaction added successfully.", "transaction": txn.to_dict()}, 201


class TransactionDetailAPI(Resource):
    """
    Retrieve, update, or delete a specific transaction.
    """

    @token_required
    def get(self, txn_id):
        user = request.user
        txn = Transaction.query.get(txn_id)
        if not txn or txn.is_deleted:
            return {"message": "Transaction not found."}, 404
        if user.role != "admin" and txn.user_id != user.id:
            return {"message": "Access denied."}, 403
        return {"transaction": txn.to_dict()}, 200

    @token_required
    def put(self, txn_id):
        user = request.user
        txn = Transaction.query.get(txn_id)
        if not txn or txn.is_deleted:
            return {"message": "Transaction not found."}, 404
        if user.role != "admin" and txn.user_id != user.id:
            return {"message": "Access denied."}, 403

        data = request.get_json() or {}

        # Safe field updates
        if "amount" in data:
            try:
                txn.amount = float(data["amount"])
            except ValueError:
                return {"message": "Amount must be a number."}, 400

        txn.currency = data.get("currency", txn.currency)
        txn.category_id = data.get("category_id", txn.category_id)
        txn.note = data.get("note", txn.note)
        txn.vendor = data.get("vendor", txn.vendor)
        txn.is_recurring = data.get("is_recurring", txn.is_recurring)
        txn.recurrence_rule = data.get("recurrence_rule", txn.recurrence_rule)
        txn.meta_data = data.get("meta_data", txn.meta_data)

        if "date" in data:
            try:
                txn.date = datetime.fromisoformat(data["date"])
            except ValueError:
                return {"message": "Invalid date format."}, 400

        db.session.commit()
        return {"message": "Transaction updated.", "transaction": txn.to_dict()}, 200

    @token_required
    def delete(self, txn_id):
        user = request.user
        txn = Transaction.query.get(txn_id)
        if not txn or txn.is_deleted:
            return {"message": "Transaction not found."}, 404
        if user.role != "admin" and txn.user_id != user.id:
            return {"message": "Access denied."}, 403

        txn.is_deleted = True
        db.session.commit()
        return {"message": "Transaction deleted (soft)."}, 200
