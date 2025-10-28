# application/api/__init__.py
from application.api.general_api import *
from application.api.auth_api import *

def register_routes(api):
    """
    Registers all API endpoints with the Flask-RESTful Api instance.
    """
    # General / Utility Routes
    api.add_resource(HealthCheck, "/api/health")
    api.add_resource(Home, "/")

    # Authentication
    api.add_resource(Register, "/api/register")
    api.add_resource(Login, "/api/login")
    api.add_resource(Profile, "/api/profile")
    api.add_resource(Logout, "/api/logout")
    api.add_resource(Refresh, "/api/token/refresh")
    api.add_resource(PasswordResetRequest, "/api/password-reset/request")
    api.add_resource(PasswordResetConfirm, "/api/password-reset/confirm")
    api.add_resource(AdminOnly, "/api/admin-only")
