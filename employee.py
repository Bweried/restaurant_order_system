from flask_restful import Resource, reqparse
from models import db, Employee, GenderEnum
from decorators import admin_required
from flask_jwt_extended import jwt_required
import time, random

emp_parse = reqparse.RequestParser()
emp_parse.add_argument('name', help='This field cannot be blank', required=True)
emp_parse.add_argument('gender', help='This field cannot be blank', required=True)
emp_parse.add_argument('age', type=int, help='This field cannot be blank', required=True)
emp_parse.add_argument('salary', type=float, help='This field cannot be blank', required=True)


class EmpList(Resource):
    @jwt_required()
    def get(self, e_id: int | None = None):
        if e_id is not None:
            emp = Employee.query.get(e_id)
            if emp:
                return Employee.to_json(emp)
            else:
                return {'message': 'Employee not found', 'status': 400}, 404
        return Employee.return_all()

    @jwt_required()
    def post(self):
        data = emp_parse.parse_args()
        gender = data['gender']
        if gender not in [category.value for category in GenderEnum]:
            return {'message': '该类别不存在', 'status': 400}, 200

        new_emp = Employee(
            name=data['name'],
            gender=data['gender'],
            age=data['age'],
            salary=data['salary']
        )
        db.session.add(new_emp)
        db.session.commit()
        return {'message': '添加成功', 'status': 200}, 200

    @jwt_required()
    def put(self, e_id: int):
        emp = Employee.query.get(e_id)

        if not emp:
            return {'message': '该员工不存在'}

        data = emp_parse.parse_args()

        # 更新员工信息
        emp.name = data['name']
        emp.gender = data['gender']
        emp.age = data['age']
        emp.salary = data['salary']

        db.session.commit()

        return {'message': '员工信息更新成功', 'status': 200}, 200

    @jwt_required()
    def delete(self, e_id: int):
        emp = Employee.query.get(e_id)

        if not emp:
            return {'message': '该员工不存在', 'status': 400}

        db.session.delete(emp)
        db.session.commit()
        return {'message': '删除成功', 'status': 200}, 200
