from sqlalchemy import text

class ItemDao:
    def __init__(self, database):
        self.db = database

    def get_item_id(self, item_name, parent_id):
        row = self.db.execute(text("""
            SELECT
                id
            FROM items
            WHERE parent_id = :parent_id and name = :name
        """), {"parent_id": parent_id, "name": item_name}).fetchone()

        return row["id"] if row else None

    def change_item_name(self, change_name_info):
        return self.db.execute(text("""
            UPDATE items
            SET name = :new_name
            WHERE name = :old_name and parent_id = :parent_id
        """), change_name_info).rowcount 

    def delete_item_info(self, item_name, parent_id):
        return self.db.execute(text("""
            DELETE FROM items
            WHERE name = :name and parent_id = :parent_id
        """), {"name": item_name, "parent_id": parent_id}).rowcount

    def get_file_info(self, file_name, parent_id):
        row = self.db.execute(text("""
            SELECT
                name,
                size,
                creation_time,
                last_modified_time
            FROM items
            WHERE name = :name and parent_id = :parent_id
        """), {"name": file_name, "parent_id": parent_id}).fetchone()

        return {"parent_id": parent_id, "name": row["name"], "size": row["size"], 
                "creation_time": row["creation_time"], 
                "last_modified_time": row["last_modified_time"]} if row else None

    def insert_file_info(self, file_info):
        return self.db.execute(text("""
        INSERT INTO items (
            parent_id,
            name,
            size,
            creation_time,
            last_modified_time
        ) VALUES (
            :parent_id,
            :name,
            :size,
            :creation_time,
            :last_modified_time
        )"""), file_info).rowcount

    def modify_file_info(self, file_info):
        return self.db.execute(text("""
            UPDATE items
            SET size = :size, last_modified_time = :last_modified_time
            WHERE name = :name and parent_id = :parent_id
        """), file_info).rowcount

    def get_folder_info(self, folder_name, parent_id):
        row = self.db.execute(text("""
            SELECT
                creation_time
            FROM items
            WHERE parent_id = :parent_id and name = :name
        """), {"parent_id": parent_id, "name": folder_name}).fetchone()

        return {"parent_id": parent_id, "name": folder_name, "creation_time": row["creation_time"]} if row else None

    def get_folder_contain_list(self, parent_id):
        rows = self.db.execute(text("""
            SELECT
                name,
                size,
                creation_time,
                last_modified_time
            FROM items
            WHERE parent_id = :parent_id
        """), {"parent_id": parent_id}).fetchall()

        return [{"parent_id": parent_id, 
            "name": row["name"], 
            "size": row["size"], 
            "creation_time": row["creation_time"],
            "last_modified_time": row["last_modified_time"]} for row in rows]

    def insert_folder_info(self, folder_info):
        return self.db.execute(text("""
            INSERT INTO items (
                parent_id,
                name,
                creation_time
            ) VALUES (
                :parent_id,
                :name,
                :creation_time
        )"""), folder_info).rowcount
