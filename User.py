from flask import request
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from models import db, UserModel, AdminModel, RevokedTokenModel, GenderEnum
import re
from decorators import jwt_required_with_blacklist, admin_required
from flask_cors import cross_origin

admin_parse = reqparse.RequestParser()
admin_parse.add_argument('username', help='This field cannot be blank', required=True)
admin_parse.add_argument('password', help='This field cannot be blank', required=True)

user_parse = reqparse.RequestParser()
user_parse.add_argument('username', help='This field cannot be blank', required=True)
user_parse.add_argument('password', help='This field cannot be blank', required=True)
user_parse.add_argument('name', help='This field cannot be blank', required=True)
user_parse.add_argument('gender', help='This field cannot be blank', required=True)
user_parse.add_argument('age', type=int, help='This field cannot be blank', required=True)
user_parse.add_argument('tel', help='This field cannot be blank', required=True)


class AdminRegistration(Resource):
    def post(self):
        # 获取JSON数据
        data = request.get_json()

        # # 使用parse_args解析数据
        # args = user_parse.parse_args(req=data)
        username = data['username']
        password = data['password']

        # 检查数据库中是否存在相同的用户名
        existing_user = AdminModel.query.filter_by(username=username).first()
        existing_normal_user = UserModel.query.filter_by(username=username).first()

        if existing_user or existing_normal_user:
            return {'message': '用户名已存在'}, 400

        # 创建新用户并保存到数据库中
        new_user = AdminModel(username=username)
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            return {'message': '用户注册成功', 'status': 200}, 200
        except:
            return {'message': 'Something went wrong'}, 500


class AdminLogin(Resource):
    def post(self):
        # 表单验证
        data = admin_parse.parse_args()
        current_user: 'AdminModel' = AdminModel.query.filter_by(username=data['username']).first()

        if not current_user:
            return {'message': '用户不存在', 'status': 400}

        if AdminModel.check_password(current_user, data['password']):
            access_token = create_access_token(identity=data['username'])
            refresh_token = create_refresh_token(identity=data['username'])
            return {
                'message': f'{current_user.username}登录成功',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'status': 200
            }
        else:
            return {'message': '密码错误', 'status': 400}


class AdminAccessLogout(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return {'message': 'Access Token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class AdminRefreshLogout(Resource):
    @jwt_required(refresh=True)
    def post(self):
        jti = get_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return {'message': 'Refresh Token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class UserRegistration(Resource):
    def post(self):
        # 表单验证
        data = user_parse.parse_args()
        username = data['username']
        password = data['password']
        name = data['name']
        gender = data['gender']
        if gender not in [category.value for category in GenderEnum]:
            return {'message': str(gender) + '类不存在'}
        age = data['age']
        tel = data['tel']

        # 验证手机号格式是否正确
        if not re.match(r'^(13[0-9]|14[01456879]|15[0-35-9]|16[2567]|17[0-8]|18[0-9]|19[0-35-9])\d{8}$', tel):
            return {'message': '手机号格式不正确', 'status': '400'}

        if not (1 <= len(username) <= 20):
            return {'message': 'Invalid username length'}

        if not (6 <= len(password) <= 255):
            return {'message': 'Invalid password length'}

        # 检查数据库中是否存在相同的用户名
        existing_user = UserModel.query.filter_by(username=username).first()
        existing_admin_user = AdminModel.query.filter_by(username=username).first()

        # 确保不和管理员用户名重复
        if existing_user or existing_admin_user:
            return {'message': '用户名已存在', 'status': '400'}
        else:
            # 创建新用户并保存到数据库中
            new_user = UserModel(username=username)
            new_user.set_password(password)
            new_user.name = name
            new_user.gender = gender
            new_user.age = age
            new_user.tel = tel
            db.session.add(new_user)
            db.session.commit()
            return {'message': '用户注册成功', 'status': '200'}, 200


class UserLogin(Resource):
    def post(self):
        # 只验证用户名、密码
        data = admin_parse.parse_args()
        current_user: 'UserModel' = UserModel.query.filter_by(username=data['username']).first()

        print(data)

        if not current_user:
            return {'message': '用户不存在', 'status': 400}

        if UserModel.check_password(current_user, data['password']):
            access_token = create_access_token(identity=data['username'])
            refresh_token = create_refresh_token(identity=data['username'])
            return {
                'message': f'{current_user.username}登录成功',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'status': 200
            }
        else:
            return {'message': '密码错误', 'status': 400}


class UserLogoutAccess(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        print(get_jwt())

        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogoutRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        jti = get_jwt()['jti']
        print(get_jwt())

        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return {'message': 'Refresh token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class UserProfile(Resource):
    @jwt_required()
    def get(self):
        current_username = get_jwt_identity()
        current_user = UserModel.query.filter_by(username=current_username).first()
        return UserModel.to_json(current_user)

    @jwt_required()
    def put(self):
        current_username = get_jwt_identity()
        current_user: 'UserModel' = UserModel.query.filter_by(username=current_username).first()

        data = user_parse.parse_args()

        # 验证手机号格式是否正确
        if not re.match(r'^(13[0-9]|14[01456879]|15[0-35-9]|16[2567]|17[0-8]|18[0-9]|19[0-35-9])\d{8}$', data['tel']):
            return {'message': '手机号格式不正确'}

        current_user.name = data['name']
        current_user.gender = data['gender']
        current_user.age = data['age']
        current_user.tel = data['tel']

        db.session.commit()

        return {'message': '用户信息更新完成', 'status': 200}, 200


class UserChangePwd(Resource):
    @jwt_required()
    def post(self):
        current_username = get_jwt_identity()
        current_user: 'UserModel' = UserModel.query.filter_by(username=current_username).first()

        if not current_user:
            return {'status': 400, 'message': '用户不存在'}, 404

        data = request.get_json()

        parser = reqparse.RequestParser()
        parser.add_argument('current_password', type=str, required=True, help='当前密码不能为空')
        parser.add_argument('new_password', type=str, required=True, help='新密码不能为空')

        args = parser.parse_args()

        current_password = args['current_password']
        new_password = args['new_password']

        # 验证当前密码是否正确
        if not UserModel.check_password(current_user, current_password):
            return {'status': 400, 'message': '当前密码不正确'}

        # 更新用户密码
        current_user.set_password(new_password)
        db.session.commit()

        return {'status': 200, 'message': '密码修改成功'}, 200


class AllUserProfile(Resource):
    @jwt_required()
    def get(self):
        return UserModel.return_all()


# 测试登录登出接口
class SecretResource(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()

        jti = get_jwt()['jti']
        if RevokedTokenModel.is_jti_blacklisted(jti):
            return {'message': '你没有权限访问'}, 401
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
