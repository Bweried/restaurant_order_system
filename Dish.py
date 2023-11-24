from flask_restful import Resource, reqparse
from models import db, Dishes, DishCategory

dish_parse = reqparse.RequestParser()
dish_parse.add_argument('name', help='This field cannot be blank', required=True)
dish_parse.add_argument('class', help='This field cannot be blank', required=True)
dish_parse.add_argument('price', help='This field cannot be blank', required=True)


class DishList(Resource):
    def get(self, dish_id: int | None = None):
        if dish_id is not None:
            dish = Dishes.query.get(dish_id)
            if dish:
                return Dishes.to_json(dish)
            else:
                return {'message': 'Dish not fount'}, 404
        else:
            return Dishes.return_all()

    def post(self):
        data = dish_parse.parse_args()
        D_class = data['class']
        if D_class not in [category.value for category in DishCategory]:
            return {'message': '该类别不存在'}, 400

        existing_dish = Dishes.query.filter_by(name=data['name']).first()

        if existing_dish:
            return {'message': '该菜品已存在'}, 400

        else:
            new_dish = Dishes(
                name=data['name'],
                D_class=data['class'],
                price=data['price']
            )
            db.session.add(new_dish)
            db.session.commit()
            return {'message': '添加成功'}, 201

    def put(self, dish_id: int):
        dish = Dishes.query.get(dish_id)

        if not dish:
            return {'message': '菜品不存在'}, 400

        data = dish_parse.parse_args()

        # 更新菜品信息
        dish.name = data['name']
        dish.D_class = data['class']
        dish.price = data['price']

        db.session.commit()

        return {'message': '菜品信息更新成功'}, 200

    def delete(self, dish_id: int):
        dish = Dishes.query.get(dish_id)

        if not dish:
            return {'message': '菜品不存在'}, 400

        db.session.delete(dish)
        db.session.commit()

        return {'message': '删除成功'}