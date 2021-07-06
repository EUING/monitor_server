from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

class ItemDao:
    def __init__(self, database):
        self.db = database

    def get_item_id(self, item_name, parent_id):
        try:
            row = self.db.execute(text("""
                SELECT
                    id
                FROM items
                WHERE parent_id = :parent_id and name = :name
            """), {"parent_id": parent_id, "name": item_name}).fetchone()

            id = row["id"] if row else None
            return True, id
        except SQLAlchemyError:
            return False, None

    def change_item_name(self, change_name_info):
        try:
            count =  self.db.execute(text("""
                UPDATE items
                SET name = :new_name
                WHERE name = :old_name and parent_id = :parent_id
            """), change_name_info).rowcount

            return True, count
        except SQLAlchemyError:
            return False, -1

    def delete_item_info(self, item_name, parent_id):
        try:
            count = self.db.execute(text("""
                DELETE FROM items
                WHERE name = :name and parent_id = :parent_id
            """), {"name": item_name, "parent_id": parent_id}).rowcount

            return True, count
        except SQLAlchemyError:
            return False, -1

    def get_item_info(self, item_name, parent_id):
        try:
            row = self.db.execute(text("""
                SELECT
                    name,
                    size,
                    hash
                FROM items
                WHERE name = :name and parent_id = :parent_id
            """), {"name": item_name, "parent_id": parent_id}).fetchone()

            info = {"parent_id": parent_id, "name": row["name"], "size": row["size"], "hash": row["hash"]} if row else None
            return True, info
        except SQLAlchemyError:
            return False, None

    def insert_item_info(self, item_info):
        try:
            count = self.db.execute(text("""
            INSERT INTO items (
                parent_id,
                name,
                size,
                hash
            ) VALUES (
                :parent_id,
                :name,
                :size,
                :hash
            )"""), item_info).rowcount

            return True, count
        except SQLAlchemyError:
            return False, -1

    def modify_item_info(self, item_info):
        try:
            count = self.db.execute(text("""
                UPDATE items
                SET size = :size, hash = :hash
                WHERE name = :name and parent_id = :parent_id
            """), item_info).rowcount

            return True, count
        except SQLAlchemyError:
            return False, -1

    def get_folder_contain_list(self, parent_id):
        try:
            rows = self.db.execute(text("""
                SELECT
                    name,
                    size,
                    hash
                FROM items
                WHERE parent_id = :parent_id
            """), {"parent_id": parent_id}).fetchall()

            folder_list = [{"parent_id": parent_id, "name": row["name"], "size": row["size"], "hash": row["hash"]} for row in rows]
            return True, folder_list
        except SQLAlchemyError:
            return False, None