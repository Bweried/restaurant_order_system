from flask import Flask, jsonify, request
from flask_restful import Api
from flask_migrate import Migrate

from User import *
from Dish import DishList
from employee import EmpList
from models import *

app = Flask(__name__)
api = Api(app)

# 连接 MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:a441523@localhost/restaurant_order_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 禁用追踪修改

# 初始化 SQLAlchemy
db.init_app(app)
migrate = Migrate(app, db)

# User
api.add_resource(UserRegistration, '/register')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogoutAccess, '/logout/access')
api.add_resource(UserLogoutRefresh, '/logout/refresh')
api.add_resource(TokenRefresh, '/token/refresh')

# Dishes
api.add_resource(DishList, '/dish/')
api.add_resource(DishList, '/dish/<int:dish_id>', endpoint='dish_list')

# Employee
api.add_resource(EmpList, '/emp/')
api.add_resource(EmpList, '/emp/<int:emp_id>', endpoint='emp_list')

if __name__ == '__main__':
    app.run(debug=True)
