# decorators.py
from functools import wraps
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from models import AdminModel, RevokedTokenModel


def jwt_required_with_blacklist(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        jwt_required()(fn)(*args, **kwargs)

        jti = get_jwt()['jti']
        if RevokedTokenModel.is_jti_blacklisted(jti):
            return {'message': '你没有权限访问'}, 401

        return fn(*args, **kwargs)

    return wrapper


def admin_required(fn):
    @wraps(fn)
    @jwt_required_with_blacklist
    def wrapper(*args, **kwargs):
        current_username = get_jwt_identity()

        # 查询当前用户是否为管理员
        is_admin = AdminModel.query.filter_by(username=current_username).first()

        if is_admin:
            return fn(*args, **kwargs)
        else:
            return {'message': '权限不足'}, 403

    return wrapper
