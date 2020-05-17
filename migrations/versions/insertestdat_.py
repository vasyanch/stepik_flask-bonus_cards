import csv

from alembic import op


def get_all_sql():
    all_objects = []
    with open('test_data/users.csv', encoding='utf8') as user_file:
        users = csv.reader(user_file, delimiter=',')
        users_obj = []
        for i, row in enumerate(users):
            if i == 0:
                continue
            users_obj.append(
                f"INSERT INTO users (id, name, password_hash) VALUES ({row[0]}, '{row[1]}', '{row[2]}')"
            )
    all_objects.extend(users_obj)

    with open('test_data/stores.csv', encoding='utf8') as stores_file:
        stores = csv.reader(stores_file, delimiter=',')
        stores_obj = []
        for i, row in enumerate(stores):
            if i == 0:
                continue
            stores_obj.append(
                f"INSERT INTO stores (id, name, address, password_hash) VALUES ({row[0]}, '{row[1]}', '{row[2]}', '{row[3]}')"
            )
    all_objects.extend(stores_obj)

    with open('test_data/cards.csv', encoding='utf8') as cards_file:
        cards = csv.reader(cards_file, delimiter=',')
        cards_obj = []
        for i, row in enumerate(cards):
            if i == 0:
                continue
            cards_obj.append(
                f'INSERT INTO cards (id, bonus, level, user_id) VALUES ({row[0]}, {row[1]}, {row[2]}, {row[3]})'
            )
    all_objects.extend(cards_obj)
    return all_objects


revision = 'insertestdat'
down_revision = 'b6b76a3abe46'
branch_labels = None
depends_on = None


def upgrade():
    for sql in get_all_sql():
        op.execute(sql)


def downgrade():
    pass
