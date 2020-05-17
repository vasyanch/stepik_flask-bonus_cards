from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    cards = fields.Nested("CardSchema", many=True)


class StoreSchema(Schema):
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    address = fields.String(required=True)


class CardSchema(Schema):
    id = fields.Integer(required=True)
    bonus = fields.Integer(required=True)
    level = fields.Integer(required=True)


class PurchaseSchema(Schema):
    id = fields.Integer(required=True)
    sum = fields.Integer(required=True)
    bonus_earned = fields.Integer(required=True)
    bonus_spent = fields.Integer(required=True)
    card_id = fields.Integer(required=True)
    store_id = fields.Integer(required=True)
    card = fields.Nested("CardSchema")
    store = fields.Nested("StoreSchema")

