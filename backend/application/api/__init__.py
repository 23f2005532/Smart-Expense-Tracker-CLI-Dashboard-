# application/api/__init__.py
from .general_api import *
from .auth.auth_api import *
from .user.user_api import *
from .transaction.transaction_api import *


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

    #User
    api.add_resource(UserProfile, "/api/user/profile")
    api.add_resource(UserPasswordChange, "/api/user/change-password")
    api.add_resource(UserList, "/api/users")
    api.add_resource(UserDetail, "/api/users/<int:user_id>")

    # Transactions
    api.add_resource(TransactionListAPI, "/api/transactions")
    api.add_resource(TransactionDetailAPI, "/api/transactions/<int:txn_id>")