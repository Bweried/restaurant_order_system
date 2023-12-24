from flask_restful import Resource, reqparse, request
from models import db, Order, MenuOrder, BillingRecord, UserModel, AdminModel, Dishes
from flask_jwt_extended import get_jwt, get_jwt_identity
from datetime import datetime
from decorators import admin_required, jwt_required_with_blacklist


# 不会设置。手动校验数据
# dish_parse = reqparse.RequestParser()
# dish_parse.add_argument('dish_details', type=list, help='dish_details cannot be blank', required=True)


class OrderList(Resource):
    @admin_required
    def get(self):
        return Order.return_all()

    @jwt_required_with_blacklist
    def post(self):
        current_username = get_jwt_identity()
        current_user: 'UserModel' = UserModel.query.filter_by(username=current_username).first()
        time = datetime.now()

        # 从请求数据中获取 dish_details
        data = request.get_json()

        # 检查是否存在 dish_details
        if 'dish_details' in data:
            dish_details = data['dish_details']
            # 创建新订单
            new_order = Order(
                customer_id=current_user.id,
                order_time=time
            )
            db.session.add(new_order)
            db.session.commit()

            # 计算订单总金额
            total_amount = 0.0

            # 循环遍历dish_details，为每个菜品创建相关的MenuOrder
            for dish_detail in dish_details:
                # 校验dish_id和quantity是否存在且为整数类型
                if 'dish_id' in dish_detail and 'quantity' in dish_detail:
                    dish_id = dish_detail['dish_id']
                    quantity = dish_detail['quantity']

                    # 确保dish_id和quantity是整数类型
                    if not isinstance(dish_id, int) or not isinstance(quantity, int):
                        return {'message': 'dish_id and quantity must be integers'}, 400

                    # 查询是否有该菜品
                    dish = Dishes.query.filter_by(id=dish_id).first()
                    if not dish:
                        return {'message': "该菜品不存在"}, 400

                    menu_order = MenuOrder(
                        order_id=new_order.id,
                        dish_id=dish_id,
                        quantity=quantity
                    )
                    db.session.add(menu_order)

                    # 账单金额
                    total_amount += dish.price * quantity

                else:
                    # 如果dish_id或quantity不存在，返回相应的错误消息
                    return {'message': 'dish_id or quantity not found in dish_details'}, 400

            # 创建订单记录
            billing_record = BillingRecord(
                order_id=new_order.id,
                total_amount=total_amount,
                billing_time=time
            )
            db.session.add(billing_record)

            db.session.commit()

            return {'status': 201, 'message': '订单创建成功', 'total_amount': total_amount}, 201

        # 如果 dish_details 不存在，返回相应的消息
        return {'message': 'dish_details not found'}, 400

    @admin_required
    def delete(self, o_id: int):
        order: 'Order' = Order.query.get(o_id)

        if not order:
            return {'message': '该订单不存在'}, 400

        db.session.delete(order)
        db.session.commit()
        return {'message': '删除成功'}, 200


# 个人订单管理
class POrder(Resource):
    @jwt_required_with_blacklist
    def get(self):
        current_username = get_jwt_identity()
        current_user = UserModel.query.filter_by(username=current_username).first()

        if current_user:
            orders = Order.query.filter_by(customer_id=current_user.id).all()
            orders_data = [Order.to_json(order) for order in orders]
            return {'status': 200, 'tabledata': orders_data}

        return {'status': 400, 'message': '用户不存在'}, 404
