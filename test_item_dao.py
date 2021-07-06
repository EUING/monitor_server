import json
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
    new_items = [
            {
                "parent_id": 0,
                "name": "새 텍스트 파일.txt",
                "size": 10,
                "hash": "hash"
            },
            {
                "parent_id": 0,
                "name": "새 폴더",
                "size": -1,
                "hash": ""
            },
            {
                "parent_id": 2,
                "name": "test.jpg",
                "size": 5000,
                "hash": "hash"
            },
            {
                "parent_id": 2,
                "name": "새 텍스트 파일.txt",
                "size": 10,
                "hash": "hash"
            }]

    database.execute(text("""
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
    )"""), new_items)

def teardown_function():
    database.execute(text("TRUNCATE items"))
    database.execute(text("ALTER TABLE items AUTO_INCREMENT=1"))

def test_get_item_id(item_dao):
    ret, item_id = item_dao.get_item_id("새 폴더2", 0)
    assert True == ret
    assert item_id == None

def test_get_item_info(item_dao):
    ret, item_info = item_dao.get_item_info("새 텍스트 파일.txt", 3)
    assert True == ret
    assert None == item_info

    ret, item_info = item_dao.get_item_info("새 텍스트 파일.txt", 0)
    assert True == ret
    assert {"parent_id": 0, "name": "새 텍스트 파일.txt", "size": 10, "hash": "hash"} ==  item_info

def test_insert_item_info(item_dao):
    wrong_item_info = {"name": "system.dll", "size": 123456, "hash": "hash"}
    ret, count = item_dao.insert_item_info(wrong_item_info)
    assert False == ret
    assert -1 == count

    item_info = {"parent_id": 0, "name": "system.dll", "size": 123456, "hash": "hash"}
    ret, count = item_dao.insert_item_info(item_info)
    assert True == ret
    assert 1 == count

    ret, new_item_info = item_dao.get_item_info("system.dll", 0)
    assert True == ret
    assert item_info == new_item_info

def test_modify_item_info(item_dao):
    item_info = {"parent_id": 0, "name": "새 텍스트 파일.txt", "size": 100, "hash": "hash2"}
    ret, count = item_dao.modify_item_info(item_info)
    assert True == ret
    assert 1 == count

    ret, modify_item_info = item_dao.get_item_info("새 텍스트 파일.txt", 0)
    assert True == ret
    assert item_info == modify_item_info

def test_modify_item_same_info(item_dao):
    same_info = {"parent_id": 2, "name": "test.jpg", "size": 5000, "hash": "hash"}

    ret, count = item_dao.modify_item_info(same_info)
    assert True == ret
    assert 1 == count

def test_change_item_name(item_dao):
    wrong_info = {"old_name": "test1.jpg", "parent_id": 2}
    ret, count = item_dao.change_item_name(wrong_info)
    assert False == ret
    assert -1 == count

    wrong_name = {"old_name": "test1.jpg", "new_name": "test.bmp", "parent_id": 2}
    ret, count = item_dao.change_item_name(wrong_name)
    assert True == ret
    assert 0 == count

    change_name_info = {"old_name": "test.jpg", "new_name": "test.bmp", "parent_id": 2}
    ret, count = item_dao.change_item_name(change_name_info)
    assert True == ret
    assert 1 == count

    item_info = {"parent_id": 2, "name": "test.bmp", "size": 5000, "hash": "hash"}
    ret, change_item_info = item_dao.get_item_info("test.bmp", 2)
    assert True == ret
    assert item_info == change_item_info   

def test_delete_item_info(item_dao):
    ret, count = item_dao.delete_item_info("새 텍스트 파일.txt", 1)
    assert True == ret
    assert 0 == count

    ret, count = item_dao.delete_item_info("새 텍스트 파일.txt", 2)
    assert True == ret
    assert 1 == count

    ret, item_info = item_dao.get_item_info("새 텍스트 파일.txt", 2)
    assert True == ret
    assert None == item_info

    ret, item_info = item_dao.get_item_info("새 텍스트 파일.txt", 0)
    assert True == ret
    assert None != item_info

def test_get_folder_contain_list(item_dao):
    ret, folder_contain_list = item_dao.get_folder_contain_list(1)
    assert True == ret
    assert [] == folder_contain_list 

    ret, folder_contain_list = item_dao.get_folder_contain_list(2)
    assert True == ret
    assert [{"parent_id": 2, "name": "test.jpg", "size": 5000, "hash": "hash"}, 
    {"parent_id": 2,"name": "새 텍스트 파일.txt","size": 10,"hash": "hash"}] == folder_contain_list