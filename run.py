from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from flask_restful import Api
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
import secrets
from datetime import timedelta

from User import *
from Dish import DishList, DishCategoryResource
from employee import EmpList
from order import OrderList, PUnFinishedOrders, PFinishedOrders, MOrder, AllUnfinishedOrders, AllCompletedOrder, \
    ConfirmOrder
from models import *

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     supports_credentials=True, max_age=2592000)
api = Api(app)

# 连接 MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:a441523@localhost/restaurant_order_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 禁用追踪修改
app.config['FLASK_ENV'] = 'development'
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

api.add_resource(UserChangePwd, '/user/pwd_chg')

# UserProfile
api.add_resource(UserProfile, '/user/profile')
api.add_resource(AllUserProfile, '/users/profile')

# Dishes
api.add_resource(DishList, '/dish/')
api.add_resource(DishList, '/dish/<int:d_id>', endpoint='dish_list')

# Employee
api.add_resource(EmpList, '/emp', '/emp/<int:e_id>', endpoint='emp_list')

# Manage_Order
api.add_resource(OrderList, '/order/', '/order/<int:o_id>', endpoint='order_list')

# User_Order
api.add_resource(PUnFinishedOrders, '/unfinishedorder/', '/unfinishedorder/<int:o_id>')
api.add_resource(PFinishedOrders, '/finishedorder')
api.add_resource(ConfirmOrder, '/orderConfirm/<int:o_id>')

# 订单详情
api.add_resource(MOrder, '/menuorder/<int:o_id>')

# 未完成\已完成订单
api.add_resource(AllUnfinishedOrders, '/allunfinished')
api.add_resource(AllCompletedOrder, '/allfinished')

# 枚举类
api.add_resource(DishCategoryResource, '/dish_categories')

if __name__ == '__main__':
    # # 第一次运行将下列代码取消注释
    # with app.app_context():
    #     db.create_all()
    app.run(debug=True)
