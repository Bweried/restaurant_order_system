from flask import Flask, jsonify, request
from flask_cors import CORS,cross_origin
from flask_restful import Api
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
import secrets
from datetime import timedelta

from User import *
from Dish import DishList, DishCategoryResource
from employee import EmpList
from order import OrderList, POrder
from models import *

app = Flask(__name__)
api = Api(app)
# CORS(app, resources={r"/*": {"origins": "*"}})
CORS(app)

# 连接 MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:a441523@localhost/restaurant_order_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 禁用追踪修改
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['JWT_SECRET_KEY'] = secrets.token_hex(16)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)
jwt = JWTManager(app)

# 初始化 SQLAlchemy
db.init_app(app)
migrate = Migrate(app, db)

# db.create_all()

# Admin
api.add_resource(AdminRegistration, '/admin/register')
api.add_resource(AdminLogin, '/admin/login')
api.add_resource(AdminAccessLogout, '/admin/logout')
api.add_resource(AdminRefreshLogout, '/admin/logout')

# User
api.add_resource(UserRegistration, '/register')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogoutAccess, '/logout')
api.add_resource(UserLogoutRefresh, '/logout')
api.add_resource(TokenRefresh, '/token/refresh')
api.add_resource(SecretResource, '/secret')

# UserProfile
api.add_resource(UserProfile, '/user/profile')
api.add_resource(AllUserProfile, '/users/profile')

# Dishes
api.add_resource(DishList, '/dish')
api.add_resource(DishList, '/dish/<int:d_id>', endpoint='dish_list')

# Employee
api.add_resource(EmpList, '/emp')
api.add_resource(EmpList, '/emp/<int:e_id>', endpoint='emp_list')

# Order
api.add_resource(OrderList, '/order')
api.add_resource(OrderList, '/order/<int:o_id>', endpoint='order_list')

# pOrder
api.add_resource(POrder, '/porder')

# 枚举类
api.add_resource(DishCategoryResource, '/dish_categories')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
