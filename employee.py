from flask_restful import Resource, reqparse
from models import db, Employee

emp_parse = reqparse.RequestParser()
emp_parse.add_argument('emp_id', help='This field cannot be blank', required=True)
emp_parse.add_argument('name', help='This field cannot be blank', required=True)
emp_parse.add_argument('gender', help='This field cannot be blank', required=True)
emp_parse.add_argument('age', help='This field cannot be blank', required=True)
emp_parse.add_argument('salary', help='This field cannot be blank', required=True)


class EmpList(Resource):
    def get(self, emp_id: int | None = None):
        pass

    def post(self):
        pass

    def put(self, emp_id: int):
        emp = Employee.query.get(emp_id)

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

    def delete(self, emp_id: int):
        emp = Employee.query.get(emp_id)

        if not emp:
            return {'message': '该员工不存在'}, 400

        db.session.delete(emp)
        db.session.commit()
        return {'message': '删除成功'}
