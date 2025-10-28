from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from dotenv import load_dotenv
import os

from application.config import LocalDevelopmentConfig as LDC
from application.database import init_app  # use the new init_app
from application.api import register_routes

load_dotenv()


def create_app():
    """
    Application factory function to create and configure the Flask app instance.

    Sets up:
    - Flask app and RESTful API
    - Configs (development only for now)
    - Database (SQLAlchemy + Alembic migrations)
    - CORS and session security
    """

    app = Flask(__name__, template_folder="../templates")

    # Load config
    if os.getenv("ENV", "development") == "production":
        raise Exception("Currently no production config is set up.")
    else:
        print("🚀 Starting in development mode")
        app.config.from_object(LDC)

    # Initialize DB, Alembic migrations, and engine
    init_app(app)

    # REST API
    api = Api(app)
    register_routes(api)

    # Set up CORS
    CORS(app, supports_credentials=True, origins=LDC.ORIGINS)

    # Secret key (use env var if available)
    app.secret_key = os.getenv("SECRET_KEY", os.urandom(50))

    return app, api


# Create global app and api for use in imports
app, api = create_app()

# Import API routes (these will register endpoints with api)
from application.api import *



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
