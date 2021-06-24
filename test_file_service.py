import json
import pytest
from file_service import FileService
from file_dao import FileDao

from sqlalchemy import create_engine, text

with open("config.json") as json_file:
    json_data = json.load(json_file)

database = create_engine(json_data["test_config"]["DB_URL"], encoding = "utf-8", max_overflow = 0)

@pytest.fixture
def file_service():
    return FileService(FileDao(database))

def setup_function():
    new_files = [
            {
                "name": "새 텍스트 파일.txt",
                "size": 10,
                "creation_time": "2021-06-24 17:54:30",
                "last_modified_time": "2021-06-24 17:54:30"
            },
            {
                "name": "test.jpg",
                "size": 5000,
                "creation_time": "2021-06-24 17:54:30",
                "last_modified_time": "2021-06-24 17:54:30"
            }]

    database.execute(text("""
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
    )"""), new_files)

def teardown_function():
    database.execute(text("TRUNCATE files"))

def test_get_total_file_info(file_service):
    new_files = [
            {
                "name": "test.jpg",
                "size": 5000,
                "creation_time": "2021-06-24 17:54:30",
                "last_modified_time": "2021-06-24 17:54:30"

            },
            {
                "name": "새 텍스트 파일.txt",
                "size": 10,
                "creation_time": "2021-06-24 17:54:30",
                "last_modified_time": "2021-06-24 17:54:30"

            }]

    file_info_list = file_service.get_total_file_info()
    assert new_files == file_info_list

def test_get_file_info(file_service):
    file_info = file_service.get_file_info("새 텍스트 파일.txt")
    assert file_info == {
                "name": "새 텍스트 파일.txt",
                "size": 10,
                "creation_time": "2021-06-24 17:54:30",
                "last_modified_time": "2021-06-24 17:54:30"
                }

def test_insert_file_info(file_service):
    file_info = {
            "name": "system.dll", "size": 123456, 
            "creation_time": "2021-06-24 17:54:30",
            "last_modified_time": "2021-06-24 17:54:30"
            }

    file_service.insert_file_info(file_info)
    new_file_info = file_service.get_file_info("system.dll")
    assert file_info == new_file_info

def test_modify_file_info(file_service):
    file_info = {
            "name": "새 텍스트 파일.txt", "size": 100, 
            "last_modified_time": "2021-06-24 18:10:15"
            }

    file_service.modify_file_info(file_info)
    file_info["creation_time"] = "2021-06-24 17:54:30"

    modify_file_info = file_service.get_file_info("새 텍스트 파일.txt")

    assert file_info == modify_file_info

def test_change_file_name(file_service):
    change_name_info = {"old_name": "test.jpg", "new_name": "test.bmp"}

    file_service.change_file_name(change_name_info)

    file_info = {
                "name": "test.bmp",
                "size": 5000,
                "creation_time": "2021-06-24 17:54:30",
                "last_modified_time": "2021-06-24 17:54:30"
                }

    change_file_info = file_service.get_file_info("test.bmp")

    assert file_info == change_file_info

def test_delete_file_info(file_service):
    file_service.delete_file_info("새 텍스트 파일.txt")

    file_info = file_service.get_file_info("새 텍스트 파일.txt")

    assert file_info == None


