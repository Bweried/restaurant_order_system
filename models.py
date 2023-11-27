from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum

db = SQLAlchemy()


class DishCategory(Enum):
    APPETIZER = 'Appetizer'
    MAIN_COURSE = 'Main Course'
    DESSERT = 'Dessert'


class GenderEnum(Enum):
    MALE = '男'
    FEMALE = '女'


class AdminModel(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))  # 密码散列值
    name = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(20), nullable=False, server_default=GenderEnum.MALE.value)
    age = db.Column(db.Integer, nullable=False)
    tel = db.Column(db.String(20), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def to_json(x: 'UserModel' = None):
        return {
            'id': x.id,
            'username': x.username,
            'name': x.name,
            'gender': x.gender,
            'age': x.age,
            'tel': x.tel
        }

    @classmethod
    def return_all(cls):
        return {'user': list(map(lambda x: cls.to_json(x), cls.query.all()))}


class Dishes(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), nullable=False)
    D_class = db.Column(db.String(20), nullable=False, server_default=DishCategory.APPETIZER.value)
    price = db.Column(db.Float, nullable=False)

    @staticmethod
    def to_json(x: 'Dishes' = None):
        return {
            'id': x.id,
            'name': x.name,
            'class': x.D_class,
            'price': x.price
        }

    @classmethod
    def return_all(cls):
        return {'dishes': list(map(lambda x: cls.to_json(x), cls.query.all()))}


class Employee(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    emp_id = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(20), nullable=False, server_default=GenderEnum.MALE.value)
    age = db.Column(db.Integer, nullable=False)
    salary = db.Column(db.Float, nullable=False)

    @staticmethod
    def to_json(x: 'Employee' = None):
        return {
            'id': x.id,
            'emp_id': x.emp_id,
            'name': x.name,
            'gender': x.gender,
            'age': x.age,
            'salary': x.salary
        }

    @classmethod
    def return_all(cls):
        return {'employees': list(map(lambda x: cls.to_json(x), cls.query.all()))}


class RevokedTokenModel(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    jti = db.Column(db.String(128))

    def add(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)


class Order(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user_model.id', ondelete='CASCADE'), nullable=False)
    order_time = db.Column(db.DateTime, nullable=False)

    @staticmethod
    def to_json(x: 'Order' = None):
        return {
            'id': x.id,
            'customer_id': x.customer_id,
            'order_time': x.order_time.isoformat()
        }

    @classmethod
    def return_all(cls):
        return {'orders': list(map(lambda x: cls.to_json(x), cls.query.all()))}


class MenuOrder(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete='CASCADE'), nullable=False)
    dish_id = db.Column(db.Integer, db.ForeignKey('dishes.id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)


class BillingRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete='CASCADE'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    # discounted_amount = db.Column(db.Float, nullable=False)
    billing_time = db.Column(db.DateTime, nullable=False)


# class DiscountRules(db.Model):
#     id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     spending_amount = db.Column(db.Float, nullable=False)
#     discount_percentage = db.Column(db.Float, nullable=False)
