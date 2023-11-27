from flask_restful import Resource, reqparse
from models import db, Employee, GenderEnum

emp_parse = reqparse.RequestParser()
emp_parse.add_argument('emp_id', help='This field cannot be blank', required=True, location='form')
emp_parse.add_argument('name', help='This field cannot be blank', required=True, location='form')
emp_parse.add_argument('gender', help='This field cannot be blank', required=True, location='form')
emp_parse.add_argument('age', type=int, help='This field cannot be blank', required=True, location='form')
emp_parse.add_argument('salary', type=float, help='This field cannot be blank', required=True, location='form')


class EmpList(Resource):
    def get(self, e_id: int | None = None):
        if e_id is not None:
            emp = Employee.query.get(e_id)
            if emp:
                return Employee.to_json(emp)
            else:
                return {'message': 'Employee not found'}, 404
        return Employee.return_all()

    def post(self):
        data = emp_parse.parse_args()
        gender = data['gender']
        if gender not in [category.value for category in GenderEnum]:
            return {'message': '该类别不存在'}

        existing_emp = Employee.query.filter_by(emp_id=data['emp_id']).first()

        if existing_emp:
            return {'massage': '该员工已存在'}, 400
        else:
            new_emp = Employee(
                emp_id=data['emp_id'],
                name=data['name'],
                gender=data['gender'],
                age=data['age'],
                salary=data['salary']
            )
            db.session.add(new_emp)
            db.session.commit()
            return {'message': '添加成功'}, 201

    def put(self, e_id: int):
        emp = Employee.query.get(e_id)

        if not emp:
            return {'message': '该员工不存在'}, 400

        data = emp_parse.parse_args()

        # 更新员工信息
        emp.emp_id = data['emp_id']
        emp.name = data['name']
        emp.gender = data['gender']
        emp.age = data['age']
        emp.salary = data['salary']

        db.session.commit()

        return {'message': '员工信息更新成功'}, 200

    def delete(self, e_id: int):
        emp = Employee.query.get(e_id)

        if not emp:
            return {'message': '该员工不存在'}, 400

        db.session.delete(emp)
        db.session.commit()
        return {'message': '删除成功'}
