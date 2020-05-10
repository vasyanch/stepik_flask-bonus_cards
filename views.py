import datetime

from flask import jsonify, request

from app import app
from models import db, User, Card, Purchase, Store
from serialize_schemas import UserSchema, StoreSchema, PurchaseSchema, CardSchema


LEVEL_BONUS_PERCENT = {
    1: (10000, 0.05),  # здесь; уровень_лояльности: (верхний порог уровня, бонусный процент)
    2: (20000, 0.1),
    3: (30000, 0.15),
    4: (float('inf'), 0.2),
}


@app.route('/stores/', methods=['GET'])
def get_stores_user():
    stores = Store.query.order_by(Store.name).all()
    return jsonify(StoreSchema(many=True).dump(stores)), 200


@app.route('/cards/<int:card_id>/', methods=['GET'])
def get_card_info_user(card_id):
    card = Card.query.get(card_id)
    if card:
        return jsonify(CardSchema().dump(card)), 200
    return jsonify(), 404


@app.route('/purchases/', methods=['GET'])
def get_purchases_user():
    purchases = Purchase.query.order_by(Purchase.date.desc())
    return jsonify(PurchaseSchema(many=True).dump(purchases)), 200


@app.route('/users/<int:user_id>/', methods=['GET'])
def get_users(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify(UserSchema().dump(user)), 200
    return jsonify(), 404


@app.route('/purchases/<int:purchase_id>/', methods=['GET'])
def get_purchase(purchase_id):
    purchase = Purchase.query.get(purchase_id)
    if purchase:
        return jsonify(PurchaseSchema().dump(purchase)), 200
    return jsonify(), 404


@app.route('/cards/', methods=['POST'])
def post_card_store():
    ans_dict = {}
    data = request.get_json()
    if not data:
        ans_dict['error'] = 'empty data'
        return jsonify(ans_dict), 400
    try:
        user = User(name=data['name'])
        user_card = Card(user_id=user.id)
        db.session.add_all([user, user_card])
        db.session.commit()
    except KeyError:
        ans_dict['error'] = 'invalid data'
        return jsonify(ans_dict), 400
    except Exception:
        ans_dict['error'] = 'sorry, something went wrong'
        return jsonify(ans_dict), 500
    ans_dict['user_id'] = user.id
    ans_dict['id'] = user_card.id
    return jsonify(ans_dict), 201, {'Location': f'/cards/{user_card.id}/'}


@app.route('/purchase/', methods=['POST'])
def post_purchase_store():
    ans_dict = {}
    data = request.get_json()
    if not data:
        ans_dict['error'] = 'empty data'
        return jsonify(ans_dict), 400
    try:
        card = Card.query.get(data['card'])
        bonus_spent = int(data['bonus_spent'])
        purchase_sum = int(data['sum'])
        if not card:
            ans_dict['error'] = 'invalid card number, this card not exist'
            return jsonify(ans_dict), 400
        if purchase_sum < 0:
            ans_dict['error'] = "purchase sum can't be less 0"
            return jsonify(ans_dict), 400
        if bonus_spent > card.bonus:
            ans_dict['error'] = "not enough bonuses"
            return jsonify(ans_dict), 400
        card.bonus = card.bonus - bonus_spent
        bonus_earned = int(purchase_sum * LEVEL_BONUS_PERCENT[card.level][1])
        card.bonus += bonus_earned
        card_full_sum = sum([purchase.sum for purchase in card.purchases])
        while card_full_sum > LEVEL_BONUS_PERCENT[card.level][0]:
            card.level += 1
        purchase = Purchase(
            sum=purchase_sum,
            date=datetime.datetime.now(),
            bonus_earned=bonus_earned,
            bonus_spent=bonus_spent,
            card_id=card.id,
            store_id=data['store']
        )
        db.session.add_all([card, purchase])
        db.session.commit()
    except KeyError:
        ans_dict['error'] = 'invalid data'
        return jsonify(ans_dict), 400
    except Exception:
        ans_dict['error'] = 'sorry, something went wrong'
        return jsonify(ans_dict), 500
    ans_dict['id'] = purchase.id
    ans_dict['bonus_earned'] = bonus_earned
    return jsonify(ans_dict), 201, {'Location': f'/purchases/{purchase.id}/'}


