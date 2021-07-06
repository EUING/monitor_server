import json
import datetime
import pytest
from item_dao import ItemDao
from item_service import ItemService

from sqlalchemy import create_engine, text

with open("config.json") as json_file:
    json_data = json.load(json_file)

database = create_engine(json_data["test_config"]["DB_URL"], encoding = "utf-8", max_overflow = 0)

@pytest.fixture
def item_service():
    return ItemService(ItemDao(database))

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
            },
            {
                "parent_id": 2,
                "name": "새 폴더",
                "size": -1,
                "hash": ""
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

def test_get_parent_id(item_service):
    ret, parent_id = item_service.get_parent_id("새 폴더")
    assert True == ret
    assert parent_id == 0

    ret, parent_id = item_service.get_parent_id("새 폴더/test.jpg")
    assert True == ret
    assert parent_id == 2

    ret, parent_id = item_service.get_parent_id("없는 폴더/없는 파일.txt")
    assert True == ret
    assert parent_id == None

def test_change_item_name(item_service):
    wrong_item_info = {"old_name": "새 폴더2", "new_name": "테스트 폴더"}
    ret, count = item_service.change_item_name(wrong_item_info)
    assert True == ret
    assert count == 0

    change_item_info = {"old_name": "새 폴더", "new_name": "테스트 폴더"}
    ret, count = item_service.change_item_name(change_item_info)
    assert True == ret
    assert count == 1

    ret, item_info = item_service.get_item_info("테스트 폴더")
    assert True == ret
    assert item_info == {"parent_id": 0, "name": "테스트 폴더", "size": -1, "hash": ""}

def test_get_item_info(item_service):
    ret, item_info = item_service.get_item_info("새 폴더/없는 파일.txt")
    assert True == ret
    assert item_info == None

    ret, item_info = item_service.get_item_info("새 폴더/새 텍스트 파일.txt")
    assert True == ret
    assert item_info == {"parent_id": 2, "name": "새 텍스트 파일.txt", "size": 10, "hash": "hash"}

    ret, item_info = item_service.get_item_info("새 텍스트 파일.txt")
    assert True == ret
    assert item_info == {"parent_id": 0, "name": "새 텍스트 파일.txt", "size": 10, "hash": "hash"}

def test_insert_item_info(item_service):
    wrong_item_info = { "name": "테스트 파일", "size": 1000}
    ret, count = item_service.insert_item_info(wrong_item_info)
    assert False == ret
    assert count == -1

    item_info = { "name": "테스트 파일", "size": 1000,  "hash": "hash"}
    ret, count = item_service.insert_item_info(item_info)
    assert True == ret
    assert count == 1

    ret, result_info = item_service.get_item_info("테스트 파일")
    assert True == ret
    item_info["parent_id"] = 0
    assert item_info == result_info

def test_modify_item_info(item_service):
    wrong_item_info = {"name": "새 폴더/새 텍스트 파일.txt", "hash": "hash2"}
    ret, count = item_service.modify_item_info(wrong_item_info)
    assert False == ret
    assert count == -1

    item_info = {"name": "새 폴더/새 텍스트 파일.txt", "size": 20000, "hash": "hash2"}
    ret, count = item_service.modify_item_info(item_info)
    assert True == ret
    assert count == 1

    item_info["name"] = "새 텍스트 파일.txt"
    item_info["parent_id"] = 2

    ret, result_info = item_service.get_item_info("새 폴더/새 텍스트 파일.txt")
    assert True == ret
    assert result_info == item_info

def test_get_folder_contain_list(item_service):
    ret, folder_contain_list = item_service.get_folder_contain_list("새 폴더2")
    assert True == ret
    assert folder_contain_list == None

    ret, folder_contain_list = item_service.get_folder_contain_list("새 폴더/새 텍스트 파일.txt")
    assert True == ret
    assert folder_contain_list == None

    ret, folder_contain_list = item_service.get_folder_contain_list("새 폴더")
    assert True == ret
    assert folder_contain_list == [{
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
            },
            {
                "parent_id": 2,
                "name": "새 폴더",
                "size": -1,
                "hash": ""
            }]

def test_delete_item_info(item_service):
    ret, count = item_service.delete_item_info("새 폴더/없는 폴더")
    assert True == ret
    assert count == 0

    ret, count = item_service.delete_item_info("새 폴더/새 폴더")
    assert True == ret
    assert count == 1 
    
    ret, folder_contain_list = item_service.get_folder_contain_list()
    assert True == ret
    assert folder_contain_list == [{
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
            }]

    ret, count = item_service.delete_item_info("새 폴더")
    assert True == ret
    assert count == 3
