from flask_restful import Resource, reqparse
from models import db, User

user_parse = reqparse.RequestParser()
user_parse.add_argument('username', help='This field cannot be blank', required=True)
user_parse.add_argument('password', help='This field cannot be blank', required=True)


class UserRegistration(Resource):
    def post(self):
        # 表单验证
        data = user_parse.parse_args()
        username = data['username']
        password = data['password']

        if not (1 <= len(username) <= 20):
            return {'message': 'Invalid username length'}, 400

        if not (6 <= len(password) <= 255):
            return {'message': 'Invalid password length'}, 400

        # 检查数据库中是否存在相同的用户名
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            return {'message': '用户名已存在'}, 400
        else:
            # 创建新用户并保存到数据库中
            new_user = User(username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            return {'message': '用户注册成功'}, 201


class UserLogin(Resource):
    def post(self):
        return {'message': 'User login'}


class UserLogoutAccess(Resource):
    def post(self):
        return {'message': 'User logout'}


class UserLogoutRefresh(Resource):
    def post(self):
        return {'message': 'User logout'}


class TokenRefresh(Resource):
    def post(self):
        return {'message': 'Token refresh'}
