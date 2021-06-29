import json
import datetime
import pytest
from item_dao import ItemDao

from sqlalchemy import create_engine, text

with open("config.json") as json_file:
    json_data = json.load(json_file)

database = create_engine(json_data["test_config"]["DB_URL"], encoding = "utf-8", max_overflow = 0)

@pytest.fixture
def item_dao():
    return ItemDao(database)

def setup_function():
    new_files = [
            {
                "parent_id": 0,
                "name": "새 텍스트 파일.txt",
                "size": 10,
                "creation_time": "2021-06-24 17:54:30",
                "last_modified_time": "2021-06-24 17:54:30"
            },
            {
                "parent_id": 0,
                "name": "새 폴더",
                "size": None,
                "creation_time": "2021-06-28 16:30:00",
                "last_modified_time": None
            },
            {
                "parent_id": 2,
                "name": "test.jpg",
                "size": 5000,
                "creation_time": "2021-06-24 17:54:30",
                "last_modified_time": "2021-06-24 17:54:30"
            },
            {
                "parent_id": 2,
                "name": "새 텍스트 파일.txt",
                "size": 10,
                "creation_time": "2021-06-24 17:54:30",
                "last_modified_time": "2021-06-24 17:54:30"
            }]

    database.execute(text("""
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
    )"""), new_files)

def teardown_function():
    database.execute(text("TRUNCATE items"))
    database.execute(text("ALTER TABLE items AUTO_INCREMENT=1"))

def test_get_file_info(item_dao):
    file_info = item_dao.get_file_info("새 텍스트 파일.txt", 0)
    assert file_info == {
                "parent_id": 0,
                "name": "새 텍스트 파일.txt",
                "size": 10,
                "creation_time": datetime.datetime.strptime("2021-06-24 17:54:30", "%Y-%m-%d %H:%M:%S"),
                "last_modified_time": datetime.datetime.strptime("2021-06-24 17:54:30", "%Y-%m-%d %H:%M:%S")
                }

def test_insert_file_info(item_dao):
    file_info = {
            "parent_id": 0,
            "name": "system.dll", "size": 123456, 
            "creation_time": "2021-06-24 17:54:30",
            "last_modified_time": "2021-06-24 17:54:30"
            }

    count = item_dao.insert_file_info(file_info)
    assert count == 1

    file_info = {
                "parent_id": 0,
                "name": "system.dll",
                "size": 123456,
                "creation_time": datetime.datetime.strptime("2021-06-24 17:54:30", "%Y-%m-%d %H:%M:%S"),
                "last_modified_time": datetime.datetime.strptime("2021-06-24 17:54:30", "%Y-%m-%d %H:%M:%S")}

    new_file_info = item_dao.get_file_info("system.dll", 0)

    assert file_info == new_file_info

def test_modify_file_info(item_dao):
    file_info = {
            "parent_id": 0,
            "name": "새 텍스트 파일.txt", "size": 100, 
            "last_modified_time": "2021-06-24 18:10:15"
            }

    count = item_dao.modify_file_info(file_info)
    assert count == 1

    file_info["creation_time"] = datetime.datetime.strptime("2021-06-24 17:54:30", "%Y-%m-%d %H:%M:%S")
    file_info["last_modified_time"] = datetime.datetime.strptime("2021-06-24 18:10:15", "%Y-%m-%d %H:%M:%S")

    modify_file_info = item_dao.get_file_info("새 텍스트 파일.txt", 0)

    assert file_info == modify_file_info

def test_modify_file_same_info(item_dao):
    same_info = { "parent_id": 2, "name": "test.jpg", "size": 5000, 
            "creation_time": "2021-06-24 17:54:30", "last_modified_time": "2021-06-24 17:54:30"}

    count = item_dao.modify_file_info(same_info)
    assert count == 1

def test_change_file_name(item_dao):
    change_name_info = {"old_name": "test.jpg", "new_name": "test.bmp", "parent_id": 2}

    count = item_dao.change_item_name(change_name_info)
    assert count == 1

    file_info = {
                "parent_id": 2,
                "name": "test.bmp",
                "size": 5000,
                "creation_time": "2021-06-24 17:54:30",
                "last_modified_time": "2021-06-24 17:54:30"
                }

    change_file_info = item_dao.get_file_info("test.bmp", 2)

    file_info["creation_time"] = datetime.datetime.strptime("2021-06-24 17:54:30", "%Y-%m-%d %H:%M:%S")
    file_info["last_modified_time"] = datetime.datetime.strptime("2021-06-24 17:54:30", "%Y-%m-%d %H:%M:%S")

    assert file_info == change_file_info

def test_change_wrong_file_name(item_dao):
    change_name_info = {"old_name": "test1.jpg", "new_name": "test.bmp", "parent_id": 2}

    count = item_dao.change_item_name(change_name_info)
    assert count == 0

def test_delete_file_info(item_dao):
    count = item_dao.delete_item_info("새 텍스트 파일.txt", 2)
    assert count == 1

    file_info = item_dao.get_file_info("새 텍스트 파일.txt", 2)

    assert file_info == None

    file_info = item_dao.get_file_info("새 텍스트 파일.txt", 0)
    assert file_info != None

def test_delete_wrong_file_info(item_dao):
    count = item_dao.delete_item_info("새 텍스트 파일.txt", 1)
    assert count == 0

def test_get_folder_info(item_dao):
    folder_info = item_dao.get_folder_info("새 폴더", 0)

    assert folder_info == {"parent_id": 0, "name": "새 폴더", 
            "creation_time": datetime.datetime.strptime("2021-06-28 16:30:00", "%Y-%m-%d %H:%M:%S")}

def test_get_folder_contain_list(item_dao):
    folder_contain_list = item_dao.get_folder_contain_list(2)

    assert folder_contain_list == [{
                "parent_id": 2,
                "name": "test.jpg",
                "size": 5000,
                "creation_time": datetime.datetime.strptime("2021-06-24 17:54:30", "%Y-%m-%d %H:%M:%S"),
                "last_modified_time": datetime.datetime.strptime("2021-06-24 17:54:30", "%Y-%m-%d %H:%M:%S")
            },
            {
                "parent_id": 2,
                "name": "새 텍스트 파일.txt",
                "size": 10,
                "creation_time": datetime.datetime.strptime("2021-06-24 17:54:30", "%Y-%m-%d %H:%M:%S"),
                "last_modified_time": datetime.datetime.strptime("2021-06-24 17:54:30", "%Y-%m-%d %H:%M:%S")
            }]

def test_insert_folder_info(item_dao):
    folder_info = {"parent_id": 0, "name": "testtest", 
            "creation_time": "2021-06-28 16:30:00"}

    count = item_dao.insert_folder_info(folder_info)
    assert count == 1
    
    result_info = item_dao.get_folder_info("testtest", 0)
    folder_info["creation_time"] = datetime.datetime.strptime("2021-06-28 16:30:00", "%Y-%m-%d %H:%M:%S")

    assert result_info == folder_info
