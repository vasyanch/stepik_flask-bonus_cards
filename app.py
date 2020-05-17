from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from config import Config
from models import db

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

from views import get_stores_user, get_card_info_user, get_users, get_one_purchase_user, user_login, store_login, \
    post_card_store, post_purchase_store, get_purchases_user


if __name__ == "__main__":
    app.run()
