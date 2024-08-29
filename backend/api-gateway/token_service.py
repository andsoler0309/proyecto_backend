from functools import wraps
from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models import UserRole


# def gateway_auth_required(fn):
#     @wraps(fn)
#     def wrapper(*args, **kwargs):
#         # Determine if the route should be protected
#         if request.endpoint in ['protected_service', 'another_protected_route']:
#             try:
#                 verify_jwt_in_request()
#                 current_user = get_jwt_identity()
#
#                 # Proceed to the route function if the JWT is valid
#                 return fn(*args, **kwargs)
#
#             except Exception:
#                 return {"message": "Unauthorized"}, 401
#         else:
#             return fn(*args, **kwargs)
#
#     return wrapper


def roles_required(required_roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()  # Ensures the JWT is valid
            current_user = get_jwt_identity()

            if UserRole(current_user['role']) not in required_roles:
                return {"message": "Access forbidden: insufficient privileges"}, 403

            return fn(*args, **kwargs)

        return decorator

    return wrapper