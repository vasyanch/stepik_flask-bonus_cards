import datetime
import random
import string

from flask import jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app import app
from models import db, User, Card, Purchase, Store
from serialize_schemas import UserSchema, StoreSchema, PurchaseSchema, CardSchema

LEVEL_BONUS_PERCENT = {
    1: (10000, 0.05),  # здесь; уровень_лояльности: (верхний порог уровня, бонусный процент)
    2: (20000, 0.1),
    3: (30000, 0.15),
    4: (float('inf'), 0.2),
}

INVALID_TOKEN_MSG = 'you are not authorized, invalid token'

INTERNAL_SERVER_ERROR_MSG = 'sorry, something went wrong'


@app.route('/user_login/', methods=['POST'])
def user_login():
    ans_dict = {}
    data = request.get_json()
    if not data:
        ans_dict["error"] = "empty data"
        return jsonify(ans_dict), 400
    try:
        card_id = data["card_id"]
        password = data["password"]
        user = User.query.join(Card).filter(Card.id == card_id).first()
        if user and user.password_valid(password):
            access_token = create_access_token(identity=f'user {card_id}', expires_delta=datetime.timedelta(1))
        else:
            ans_dict['error'] = "Bad card_id or password"
            return jsonify(ans_dict), 401
        ans_dict['access_token'] = access_token
    except KeyError:
        ans_dict['error'] = 'invalid data'
        return jsonify(ans_dict), 400
    except Exception as e:
        ans_dict['error'] = INTERNAL_SERVER_ERROR_MSG
        print(e)  # здесь надо бы писать в лог эту ошибку
        return jsonify(ans_dict), 500
    return jsonify(ans_dict), 200


@app.route('/store_login/', methods=['POST'])
def store_login():
    ans_dict = {}
    data = request.get_json()
    if not data:
        ans_dict["error"] = "empty data"
        return jsonify(ans_dict), 400
    try:
        store_id = data["store_id"]
        password = data["password"]
        store = Store.query.get(store_id)
        if store and store.password_valid(password):
            access_token = create_access_token(identity=f'store {store_id}', expires_delta=datetime.timedelta(365))
        else:
            ans_dict['error'] = "Bad store_id or password"
            return jsonify(ans_dict), 401
        ans_dict['access_token'] = access_token
    except KeyError:
        ans_dict['error'] = 'invalid data'
        return jsonify(ans_dict), 400
    except Exception as e:
        ans_dict['error'] = INTERNAL_SERVER_ERROR_MSG
        print(e)  # здесь надо бы писать в лог эту ошибку
        return jsonify(ans_dict), 500
    return jsonify(ans_dict), 200


@app.route('/stores/', methods=['GET'])
@jwt_required
def get_stores_user():
    identity_role, identity_id = get_jwt_identity().split()
    identity_id = int(identity_id)
    identity_card = Card.query.get(identity_id)
    if identity_role != 'user' or identity_card is None:
        return jsonify({'error': INVALID_TOKEN_MSG}), 401
    stores = Store.query.order_by(Store.name).all()
    return jsonify(StoreSchema(many=True).dump(stores)), 200


@app.route('/cards/<int:card_id>/', methods=['GET'])
@jwt_required
def get_card_info_user(card_id):
    identity_role, identity_id = get_jwt_identity().split()
    identity_id = int(identity_id)
    identity_card = Card.query.get(identity_id)
    if identity_role != 'user' or identity_card is None:
        return jsonify({'error': INVALID_TOKEN_MSG}), 401
    if identity_id != card_id:
        return jsonify({'error': "sorry, it's not you card"})
    card = Card.query.get(card_id)
    if card:
        return jsonify(CardSchema().dump(card)), 200
    return jsonify(), 404


@app.route('/purchases/', methods=['GET'])
@jwt_required
def get_purchases_user():
    identity_role, identity_id = get_jwt_identity().split()
    identity_id = int(identity_id)
    identity_card = Card.query.get(identity_id)
    if identity_role != 'user' or identity_card is None:
        return jsonify({'error': INVALID_TOKEN_MSG}), 401
    purchases = Purchase.query.filter(Purchase.card_id == identity_id).order_by(Purchase.date.desc())
    return jsonify(PurchaseSchema(many=True).dump(purchases)), 200


@app.route('/users/<int:user_id>/', methods=['GET'])
@jwt_required
def get_users(user_id):
    identity_role, identity_id = get_jwt_identity().split()
    identity_id = int(identity_id)
    identity_card = Card.query.get(identity_id)
    if identity_role != 'user' or identity_card is None:
        return jsonify({'error': INVALID_TOKEN_MSG}), 401
    if identity_card.user_id != user_id:
        return jsonify({'error': 'sorry, you can get only you profile info'})
    user = User.query.get(user_id)
    if user:
        return jsonify(UserSchema().dump(user)), 200
    return jsonify(), 404


@app.route('/purchases/<int:purchase_id>/', methods=['GET'])
@jwt_required
def get_purchase_user(purchase_id):
    identity_role, identity_id = get_jwt_identity().split()
    identity_id = int(identity_id)
    identity_card = Card.query.get(identity_id)
    if identity_role != 'user' or identity_card is None:
        return jsonify({'error': INVALID_TOKEN_MSG}), 401
    purchase = Purchase.query.get(purchase_id)
    if purchase and purchase.card_id == identity_id:
        return jsonify(PurchaseSchema().dump(purchase)), 200
    return jsonify(), 404


@app.route('/cards/', methods=['POST'])
@jwt_required
def post_card_store():
    identity_role, identity_id = get_jwt_identity().split()
    identity_id = int(identity_id)
    identity_store = Store.query.get(identity_id)
    if identity_role != 'store' or identity_store is None:
        return jsonify({'error': INVALID_TOKEN_MSG}), 401
    ans_dict = {}
    data = request.get_json()
    if not data:
        ans_dict['error'] = 'empty data'
        return jsonify(ans_dict), 400
    try:
        password = generate_random_password()
        user = User(name=data['full_name'], password=password)
        db.session.add(user)
        db.session.commit()
        user_card = Card(user_id=user.id)
        db.session.add(user_card)
        db.session.commit()
    except KeyError:
        ans_dict['error'] = 'invalid data'
        return jsonify(ans_dict), 400
    except Exception as e:
        ans_dict['error'] = INTERNAL_SERVER_ERROR_MSG
        print(e)  # здесь надо бы писать в лог эту ошибку
        return jsonify(ans_dict), 500
    ans_dict['user_id'] = user.id
    ans_dict['id'] = user_card.id
    ans_dict['password'] = password
    return jsonify(ans_dict), 201, {'Location': f'/cards/{user_card.id}/'}


@app.route('/purchase/', methods=['POST'])
@jwt_required
def post_purchase_store():
    identity_role, identity_id = get_jwt_identity().split()
    identity_id = int(identity_id)
    identity_store = Store.query.get(identity_id)
    if identity_role != 'store' or identity_store is None:
        return jsonify({'error': INVALID_TOKEN_MSG}), 401
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
        ans_dict['error'] = INTERNAL_SERVER_ERROR_MSG
        return jsonify(ans_dict), 500
    ans_dict['id'] = purchase.id
    ans_dict['bonus_earned'] = bonus_earned
    return jsonify(ans_dict), 201, {'Location': f'/purchases/{purchase.id}/'}


def generate_random_password(length=8):
    low_letters = string.ascii_lowercase
    symbols = low_letters.upper() + low_letters + ''.join([str(i) for i in range(10)])
    return ''.join([random.choice(symbols) for i in range(length)])
