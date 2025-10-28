from application.api import *
from flask import make_response, jsonify
from werkzeug.exceptions import HTTPException
# Dictionary mapping error codes to user-related error messages
error_messages_user = {
    0: "Error Message",
    1: "Email Already Registered",
    2: "Necessary Details Missing!!",
    3: "Username already in Use"
}

# Dictionary mapping error codes to template-related error messages
error_messages_template = {
    0: "Error Message",
    2: "Necessary Details Missing!!",
    1: "Template Name already exists",
}

# Dictionary mapping error codes to subscription-related error messages
error_messages_subscription = {
    0: "Error Message",
    1: "Name Already Used"
}

# Dictionary mapping error codes to login-related error messages
error_messages_login = {
    0: "Error Message",
    1: "Email Or Password Incorrect",
    2: "Login Details missing!!",
    3: "Email Or Username Not Found",
    4: "Login using the Google SignIn Button",
    5: "Incorrect Password!!",
    6: "Your Account has been blocked, Contact us if you think something's wrong..",
    7: "Your account is not verified, Please Check email for verification link."
}


# Custom exception class for user-related errors
class userException(HTTPException):
    def __init__(self, error_code, status_code):
        """
        Initialize userException with error code and HTTP status code.

        Args:
            error_code (int): The code identifying the specific user error.
            status_code (int): HTTP status code to return (e.g., 400, 404).
        """
        message = {
            "error_code": error_code,
            "message": error_messages_user[error_code]  # Fetch message based on code
        }
        # Create a Flask response object with JSON error message and status code
        self.response = make_response(jsonify(message), status_code)


# Custom exception class for template-related errors
class templateException(HTTPException):
    def __init__(self, error_code, status_code):
        """
        Initialize templateException with error code and HTTP status code.

        Args:
            error_code (int): The code identifying the specific template error.
            status_code (int): HTTP status code to return.
        """
        message = {
            "error_code": error_code,
            "message": error_messages_template[error_code]
        }
        self.response = make_response(jsonify(message), status_code)


# Custom exception class for subscription-related errors
class subscriptionException(HTTPException):
    def __init__(self, error_code, status_code):
        """
        Initialize subscriptionException with error code and HTTP status code.

        Args:
            error_code (int): The code identifying the subscription error.
            status_code (int): HTTP status code to return.
        """
        message = {
            "error_code": error_code,
            "message": error_messages_subscription[error_code]
        }
        self.response = make_response(jsonify(message), status_code)


# Custom exception class for login-related errors
class loginException(HTTPException):
    def __init__(self, error_code, status_code):
        """
        Initialize loginException with error code and HTTP status code.

        Args:
            error_code (int): The code identifying the login error.
            status_code (int): HTTP status code to return.
        """
        message = {
            "error_code": error_code,
            "message": error_messages_login[error_code]
        }
        self.response = make_response(jsonify(message), status_code)
