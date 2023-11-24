from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from models import db, UserModel, AdminModel

admin_parse = reqparse.RequestParser()
admin_parse.add_argument('username', help='This field cannot be blank', required=True)
admin_parse.add_argument('password', help='This field cannot be blank', required=True)

user_parse = reqparse.RequestParser()
user_parse.add_argument('username', help='This field cannot be blank', required=True)
user_parse.add_argument('password', help='This field cannot be blank', required=True)
user_parse.add_argument('name', help='This field cannot be blank', required=True)


class AdminRegistration(Resource):
    def post(self):
        # 表单验证
        data = admin_parse.parse_args()
        username = data['username']
        password = data['password']

        # 检查数据库中是否存在相同的用户名
        existing_user = AdminModel.query.filter_by(username=username).first()

        if existing_user:
            return {'message': '用户名已存在'}, 400

        # 创建新用户并保存到数据库中
        new_user = AdminModel(username=username)
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            return {'message': '用户注册成功'}, 201
        except:
            return {'message': 'Something went wrong'}, 500


class AdminLogin(Resource):
    def post(self):
        # 表单验证
        data = admin_parse.parse_args()
        current_user: 'AdminModel' = AdminModel.query.filter_by(username=data['username']).first()

        if not current_user:
            return {'message': '用户不存在'}, 400

        if AdminModel.check_password(current_user, data['password']):
            access_token = create_access_token(identity=data['username'])
            refresh_token = create_refresh_token(identity=data['username'])
            return {
                'message': f'{current_user.username}登录成功',
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        else:
            return {'message': '密码错误'}


class AdminLogout(Resource):
    pass


class UserRegistration(Resource):
    def post(self):
        # 表单验证
        data = user_parse.parse_args()
        username = data['username']
        password = data['password']
        name = data['name']

        if not (1 <= len(username) <= 20):
            return {'message': 'Invalid username length'}, 400

        if not (6 <= len(password) <= 255):
            return {'message': 'Invalid password length'}, 400

        # 检查数据库中是否存在相同的用户名
        existing_user = UserModel.query.filter_by(username=username).first()

        if existing_user:
            return {'message': '用户名已存在'}, 400
        else:
            # 创建新用户并保存到数据库中
            new_user = UserModel(username=username)
            new_user.set_password(password)
            new_user.name = name
            db.session.add(new_user)
            db.session.commit()
            return {'message': '用户注册成功'}, 201


class UserLogin(Resource):
    def post(self):
        # 只验证用户名、密码
        data = admin_parse.parse_args()
        current_user: 'UserModel' = UserModel.query.filter_by(username=data['username']).first()

        if not current_user:
            return {'message': '用户不存在'}, 400

        if UserModel.check_password(current_user, data['password']):
            access_token = create_access_token(identity=data['username'])
            refresh_token = create_refresh_token(identity=data['username'])
            return {
                'message': f'{current_user.username}登录成功',
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        else:
            return {'message': '密码错误'}


class UserLogoutAccess(Resource):
    def post(self):
        return {'message': 'User logout'}


class UserLogoutRefresh(Resource):
    def post(self):
        return {'message': 'User logout'}


class SecretResource(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        return {
            'message': 'secret message',
            'current_user': current_user
        }


class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {'access_token': access_token}
