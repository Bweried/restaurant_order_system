# decorators.py
from functools import wraps
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import AdminModel


def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_username = get_jwt_identity()
        if current_username in [admin.username for admin in AdminModel.query.all()]:
            return fn(*args, **kwargs)
        else:
            return {'message': '权限不足'}, 403

    return wrapper
