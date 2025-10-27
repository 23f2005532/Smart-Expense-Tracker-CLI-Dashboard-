from flask import Flask
from .extensions import db, jwt, cors
from .routes import register_routes
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    
    register_routes(app)
    
    return app
