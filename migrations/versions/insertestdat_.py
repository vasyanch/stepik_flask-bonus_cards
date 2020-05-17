import csv

from app import db
from models import User, Store, Card


def insert_test_data():
    all_objects = []
    with open('test_data/users.csv', encoding='utf8') as user_file:
        users = csv.reader(user_file, delimiter=',')
        users_obj = []
        for i, row in enumerate(users):
            if i == 0:
                continue
            users_obj.append(User(id=int(row[0]), name=row[1], password_hash=row[2]))
    all_objects.extend(users_obj)

    with open('test_data/stores.csv', encoding='utf8') as stores_file:
        stores = csv.reader(stores_file, delimiter=',')
        stores_obj = []
        for i, row in enumerate(stores):
            if i == 0:
                continue
            stores_obj.append(Store(id=int(row[0]), name=row[1], address=row[2], password_hash=row[3]))
    all_objects.extend(stores_obj)

    with open('test_data/cards.csv', encoding='utf8') as cards_file:
        cards = csv.reader(cards_file, delimiter=',')
        cards_obj = []
        for i, row in enumerate(cards):
            if i == 0:
                continue
            cards_obj.append(Card(id=int(row[0]), bonus=int(row[1]), level=int(row[2]), user_id=int(row[3])))
    all_objects.extend(cards_obj)

    db.session.add_all(all_objects)
    db.session.commit()


revision = 'insertestdat'
down_revision = 'b6b76a3abe46'
branch_labels = None
depends_on = None


def upgrade():
    insert_test_data()


def downgrade():
    pass
