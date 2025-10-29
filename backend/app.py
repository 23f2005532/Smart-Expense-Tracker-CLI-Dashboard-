from flask import Flask
from flask_restful import Api
from flask_cors import CORS 
from dotenv import load_dotenv
import os



load_dotenv()


def create_app():

    app = Flask(__name__)
    if os.getenv("ENV", "development") == "production":
        raise Exception("Currently no production confi is set up.")
    else:
        print("Starting in development mode")
        app.config.from_object(LDC)
    
    init_app(app)

    api = Api(app)
    register_routes(api)

    CORS(app, supports_credentials=True, origins=[LDC.CORS_ORIGIN])

    app.secret_key = os.getenv("SECRET_KEY", os.urandom(24))

    return app , api

app, api = create_app()



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)