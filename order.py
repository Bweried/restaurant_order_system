from flask_restful import Resource, reqparse
from models import db, Order, MenuOrder, BillingRecord, UserModel, AdminModel
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from datetime import datetime
from decorators import admin_required


class OrderList(Resource):
    @admin_required
    def get(self):
        return Order.return_all()

    @jwt_required()
    def post(self):
        current_username = get_jwt_identity()
        current_user: 'UserModel' = UserModel.query.filter_by(username=current_username).first()
        time = datetime.now()

        # 创建新订单
        new_order = Order(
            customer_id=current_user.id,
            order_time=time
        )
        db.session.add(new_order)
        db.session.commit()
        return {'message': '订单创建成功'}, 201

    @jwt_required()
    def delete(self, o_id: int):
        order: 'Order' = Order.query.get(o_id)

        if not order:
            return {'message': '该订单不存在'}, 400

        current_username = get_jwt_identity()
        current_user = UserModel.query.filter_by(username=current_username).first()

        # 调试输出
        print(f"Current User ID: {current_user.id}, Order Customer ID: {order.customer_id}")

        # 判断是否为管理员 & 判断是否为用户本人
        if current_username not in [admin.username for admin in
                                    AdminModel.query.all()] and current_user.id != order.customer_id:
            return {'message': '你没有权限删除'}, 401

        db.session.delete(order)
        db.session.commit()
        return {'message': '删除成功'}, 200
