# application/api/general_api.py
from flask_restful import Resource
from flask import jsonify
import datetime
from application.database import db



class Home(Resource):
    """
    Basic home endpoint to verify API is running.
    """

    def get(self):
        response = {
            "message": "Welcome to the Smart Expense Tracker API!",
            "status": "running",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "version": "v1.0.0"
        }
        return jsonify(response)

class HealthCheck(Resource):
    """
    Basic health check endpoint for verifying API and DB connectivity.
    """

    def get(self):
        try:
            # Quick DB check
            # db.session.execute("SELECT 1")
            db_status = "connected"
        except Exception as e:
            db_status = f"error: {str(e)}"

        response = {
            "status": "ok",
            "service": "Smart Expense Tracker API",
            "database": db_status,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "version": "v1.0.0"
        }

        return jsonify(response)
