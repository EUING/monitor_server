from sqlalchemy import text

class FileDao:
    def __init__(self, database):
        self.db = database

    def get_total_file_info(self):
        rows = self.db.execute(text("""
            SELECT
                name,
                size,
                creation_time,
                last_modified_time
            FROM files
        """)).fetchall()

        return [{
                    "name": row["name"], 
                    "size": row["size"], 
                    "creation_time": row["creation_time"],
                    "last_modified_time": row["last_modified_time"]
                } for row in rows] if rows else None

    def get_file_info(self, file_name):
        row = self.db.execute(text("""
            SELECT
                name,
                size,
                creation_time,
                last_modified_time
            FROM files
            WHERE name = :name
        """), {"name": file_name}).fetchone()

        return {"name": row["name"], "size": row["size"], 
                "creation_time": row["creation_time"], 
                "last_modified_time": row["last_modified_time"]} if row else None

    def insert_file_info(self, file_info):
        return self.db.execute(text("""
        INSERT INTO files (
            name,
            size,
            creation_time,
            last_modified_time
        ) VALUES (
            :name,
            :size,
            :creation_time,
            :last_modified_time
        )"""), file_info)

    def modify_file_info(self, file_info):
        return self.db.execute(text("""
            UPDATE files
            SET size = :size, last_modified_time = :last_modified_time
            WHERE name = :name
        """), file_info)

    def change_file_name(self, change_name_info):
        return self.db.execute(text("""
            UPDATE files
            SET name = :new_name
            WHERE name = :old_name
        """), change_name_info) 

    def delete_file_info(self, file_name):
        return self.db.execute(text("""
            DELETE FROM files
            WHERE name = :name
        """), {"name": file_name})

