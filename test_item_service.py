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
            },
            {
                "parent_id": 2,
                "name": "새 폴더",
                "size": None,
                "creation_time": "2021-06-28 19:00:00",
                "last_modified_time": None
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

def test_get_parent_id(item_service):
    parent_id = item_service.get_parent_id("새 폴더")

    assert parent_id == 0
    parent_id = item_service.get_parent_id("새 폴더/test.jpg")
    assert parent_id == 2

def test_change_item_name(item_service):
    change_item_info = {"old_name": "새 폴더", "new_name": "테스트 폴더"}
    count = item_service.change_item_name(change_item_info)
    assert count == 1

    folder_info = item_service.get_folder_info("테스트 폴더")
    assert folder_info == {"parent_id": 0, "name": "테스트 폴더", "creation_time": "2021-06-28 16:30:00"}

def test_delete_file_info(item_service):
    file_name = "새 폴더/새 텍스트 파일.txt"
    count = item_service.delete_item_info(file_name)
    assert count == 1

    file_info = item_service.get_file_info("새 폴더/새 텍스트 파일.txt")
    assert file_info == None

    file_info = item_service.get_file_info("새 텍스트 파일.txt")
    assert file_info == {
                "parent_id": 0,
                "name": "새 텍스트 파일.txt",
                "size": 10,
                "creation_time": "2021-06-24 17:54:30",
                "last_modified_time": "2021-06-24 17:54:30"
            }

def test_get_file_info(item_service):
    file_info = item_service.get_file_info("새 폴더/새 텍스트 파일.txt")
    assert file_info == {
                "parent_id": 2,
                "name": "새 텍스트 파일.txt",
                "size": 10,
                "creation_time": "2021-06-24 17:54:30",
                "last_modified_time": "2021-06-24 17:54:30"
            }

    file_info = item_service.get_file_info("새 텍스트 파일.txt")
    assert file_info == {
            "parent_id": 0,
            "name": "새 텍스트 파일.txt",
            "size": 10,
            "creation_time": "2021-06-24 17:54:30",
            "last_modified_time": "2021-06-24 17:54:30"
            }

def test_insert_file_info(item_service):
    file_info = {
            "name": "테스트 파일", "size": 1000, 
            "creation_time": "2021-06-24 17:54:30",
            "last_modified_time": "2021-06-24 17:54:30"}

    count = item_service.insert_file_info(file_info)
    assert count == 1

    result_info = item_service.get_file_info("테스트 파일")
    file_info["parent_id"] = 0
    assert file_info == result_info 

def test_modify_file_info(item_service):
    file_info = {
            "name": "새 폴더/새 텍스트 파일.txt",
            "size": 20000,
            "last_modified_time": "2021-06-28 19:00:00"
            }

    count = item_service.modify_file_info(file_info)
    assert count == 1

    file_info["name"] = "새 텍스트 파일.txt"
    file_info["parent_id"] = 2
    file_info["creation_time"] = "2021-06-24 17:54:30"

    result_info = item_service.get_file_info("새 폴더/새 텍스트 파일.txt")

    assert result_info == file_info

def test_get_folder_info(item_service):
    folder_info = item_service.get_folder_info("새 폴더")

    assert folder_info == {"parent_id": 0, "name": "새 폴더", "creation_time": "2021-06-28 16:30:00"}

    folder_info = item_service.get_folder_info("새 폴더/새 폴더")

    assert folder_info == {"parent_id": 2, "name": "새 폴더", "creation_time": "2021-06-28 19:00:00"}

def test_get_folder_contain_list(item_service):
    folder_contain_list = item_service.get_folder_contain_list("새 폴더2")
    assert folder_contain_list == []

    folder_contain_list = item_service.get_folder_contain_list("새 폴더")
    assert folder_contain_list == [{
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
            },
            {
                "parent_id": 2,
                "name": "새 폴더",
                "size": None,
                "creation_time": "2021-06-28 19:00:00",
                "last_modified_time": None
            }]

def test_insert_folder_info(item_service):
    folder_info = {"name": "새 폴더/new folder", "creation_time": "2021-06-28 19:25:00"}
    count = item_service.insert_folder_info(folder_info)
    assert count == 1

    result_info = item_service.get_folder_info("새 폴더/new folder")
    folder_info["name"] = "new folder"
    folder_info["parent_id"] = 2

    assert folder_info == result_info

def test_insert_wrong_folder_info(item_service):
    wrong_folder_info = {"name": "없는 폴더/new folder", "creation_time": "2021-06-29 10:30:00"}
    count = item_service.insert_folder_info(wrong_folder_info)
    assert count == 0

def test_delete_folder_info(item_service):
    count = item_service.delete_item_info("새 폴더/새 폴더")
    assert count == 1 
    
    folder_contain_list = item_service.get_folder_contain_list()

    assert folder_contain_list == [{
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
            }]

    count = item_service.delete_item_info("새 폴더")
    assert count == 3

def test_delete_wrong_folder_info(item_service):
    count = item_service.delete_item_info("새 폴더/없는 폴더")
    assert count == 0

def test_delete_item_info(item_service):
    count = item_service.delete_item_info("새 텍스트 파일.txt")
    assert count == 1
