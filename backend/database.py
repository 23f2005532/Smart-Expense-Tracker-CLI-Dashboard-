import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from flask_migrate import Migrate


db = SQLAlchemy()
engine = None
Session = None
migrate = None

def init_db(app):
    global engine, Session, migrate
    
    db.init_app(app)

    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    engine = create_engine(db_uri, future=True)

    Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

    migrate = Migrate(app, db, directory=os.path.join(os.path.dirname(__file__), 'migrations'))

    with app.app_context():
        db.create_all()
    print(f"Database initialized and alembic migrations environment ready at {migrate.directory}")

def get_db_session():
    global Session
    
    if not Session:
        raise Exception("Database session is not initialized. Call init_db(app) first.")
    return Session()

def close_db_session(session):
    try:
        session.close()
    except Exception:
        pass