from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))  # 密码散列值

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class DishCategory(Enum):
    APPETIZER = 'Appetizer'
    MAIN_COURSE = 'Main Course'
    DESSERT = 'Dessert'


class Dishes(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), nullable=False)
    D_class = db.Column(db.String(20), nullable=False, server_default=DishCategory.APPETIZER.value)
    price = db.Column(db.Float, nullable=False)

    @staticmethod
    def to_json(x: 'Dishes' = None):
        return {
            'name': x.name,
            'class': x.D_class,
            'price': x.price
        }

    @staticmethod
    def return_all():
        return {'dishes': list(map(lambda x: Dishes.to_json(x), Dishes.query.all()))}


class Employee(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    emp_id = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    salary = db.Column(db.Float, nullable=False)


class DiscountRules(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    spending_amount = db.Column(db.Float, nullable=False)
    discount_percentage = db.Column(db.Float, nullable=False)
