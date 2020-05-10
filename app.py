from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


from config import Config
from models import db

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

from views import get_stores_user, get_card_info_user, get_purchases_user, post_card_store, post_purchase_store

if __name__ == "__main__":
    app.run()
