from flask import jsonify, abort
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
            # billing_record = BillingRecord(
            #     order_id=new_order.id,
            #     total_amount=total_amount,
            #     billing_time=time
            # )
            # db.session.add(billing_record)
            #
            # db.session.commit()

            return {'status': 200, 'message': '订单创建成功', 'total_amount': total_amount}, 200

        # 如果 dish_details 不存在，返回相应的消息
        return {'message': 'dish_details not found'}, 400

    @jwt_required_with_blacklist
    def delete(self, o_id: int):
        order: 'Order' = Order.query.get(o_id)

        if not order:
            return {'message': '该订单不存在', 'status': 200}, 200

        db.session.delete(order)
        db.session.commit()
        return {'message': '删除成功', 'status': 200}, 200


class ConfirmOrder(Resource):
    @jwt_required_with_blacklist
    def get(self, o_id: int):
        current_username = get_jwt_identity()
        current_user: 'UserModel' = UserModel.query.filter_by(username=current_username).first()
        time = datetime.now()

        # 查询订单是否存在
        order = Order.query.filter_by(id=o_id, customer_id=current_user.id).first()
        if not order:
            return {'message': 'Order not found'}, 404

        # 获取订单的菜品详情，并关联 Dishes 表以获取单价
        menu_orders = MenuOrder.query \
            .join(Dishes, MenuOrder.dish_id == Dishes.id) \
            .filter(MenuOrder.order_id == o_id).all()

        # 计算订单总金额
        total_amount = sum(menu_order.dish.price * menu_order.quantity for menu_order in menu_orders)

        # 创建订单记录
        billing_record = BillingRecord(
            order_id=o_id,
            total_amount=total_amount,
            billing_time=time
        )
        db.session.add(billing_record)
        db.session.commit()

        return {'status': 200, 'message': '付款成功', 'total_amount': total_amount}, 200


# 个人未完成订单
class PUnFinishedOrders(Resource):
    @jwt_required_with_blacklist
    def get(self):
        current_username = get_jwt_identity()
        current_user = UserModel.query.filter_by(username=current_username).first()

        if current_user:
            # 获取未完成订单（不在 billing_record 表中的订单）
            unfinished_orders = Order.query.filter_by(customer_id=current_user.id) \
                .filter(~Order.id.in_(db.session.query(BillingRecord.order_id))) \
                .all()

            orders_data = [Order.to_json(order) for order in unfinished_orders]
            return {'status': 200, 'tabledata': orders_data}, 200

        return {'status': 400, 'message': '用户不存在'}, 404

    @jwt_required_with_blacklist
    def put(self, o_id: int | None = None):
        if o_id is None:
            abort(400, message='订单编号不能为空')

        menu_order: 'MenuOrder' = MenuOrder.query.filter_by(order_id=o_id).first()

        if not menu_order:
            return {'status': 400, 'message': '订单不存在'}, 404

        # 从请求数据中获取新的 quantity
        data = request.get_json()
        new_quantity = data.get('quantity')

        # 校验新的 quantity 是否存在且为整数类型
        if new_quantity is not None and not isinstance(new_quantity, int):
            return {'message': 'quantity 必须是整数类型'}, 400

        menu_order.quantity = new_quantity
        db.session.commit()

        return {'status': 200, 'message': '订单修改成功'}, 200


class PFinishedOrders(Resource):
    @jwt_required_with_blacklist
    def get(self):
        finished_orders = BillingRecord.query.all()
        orders_data = [BillingRecord.to_json(order) for order in finished_orders]

        return {'status': 200, 'tabledata': orders_data}, 200


# 返回订单菜品信息
class MOrder(Resource):
    @jwt_required_with_blacklist
    def get(self, o_id: int | None = None):
        if o_id is None:
            abort(400, message='订单编号不能为空')

        menu_orders = MenuOrder.query.filter_by(order_id=o_id).all()

        if not menu_orders:
            return {'status': 400, 'message': '订单不存在'}, 404

        order_details = []

        for menu_order in menu_orders:
            dish = Dishes.query.get(menu_order.dish_id)

            if not dish:
                return {'status': 400, 'message': '菜品不存在'}, 404

            order_details.append({
                'name': dish.name,
                'quantity': menu_order.quantity,
                'price': dish.price,
                'total_amount': dish.price * menu_order.quantity
            })

        return {'status': 200, 'order_details': order_details}, 200


# 所有未完成订单
class AllUnfinishedOrders(Resource):
    @jwt_required_with_blacklist
    def get(self):
        try:
            # 查询未完成订单
            unfinished_orders = Order.query.filter(~Order.id.in_(
                BillingRecord.query.with_entities(BillingRecord.order_id).distinct())
                                                   ).all()

            # 将订单信息转换为字典列表
            orders_data = [Order.to_json(order) for order in unfinished_orders]

            print(orders_data)

            return {'status': 200, 'tabledata': orders_data}, 200

        except Exception as e:
            return {'message': str(e)}, 500


# 所有已完成订单
class AllCompletedOrder(Resource):
    @jwt_required_with_blacklist
    def get(self):
        completed_orders = BillingRecord.query.all()

        completed_orders_data = [BillingRecord.to_json(order) for order in completed_orders]
        return {'status': 200, 'tabledata': completed_orders_data}, 200
