import json
import pytest
from file_service import FileService
from file_dao import FileDao

from app import create_app
from sqlalchemy import create_engine, text

with open("config.json") as json_file:
    json_data = json.load(json_file)

database = create_engine(json_data["test_config"]["DB_URL"], encoding = "utf-8", max_overflow = 0)

@pytest.fixture
def api():
    app = create_app(True)
    app.config["TEST"] = True
    api = app.test_client()
    return api

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

def test_get_total_file_info(api):
    files = [
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

    resp = api.get("/files")
    file_info_list = json.loads(resp.data.decode("utf-8"))

    assert resp.status_code == 200
    assert file_info_list == files

def test_get_file_info(api):
    resp = api.get("/files/새 텍스트 파일.txt")
    file_info = json.loads(resp.data.decode("utf-8"))

    assert resp.status_code == 200
    assert file_info == {
                "name": "새 텍스트 파일.txt",
                "size": 10,
                "creation_time": "2021-06-24 17:54:30",
                "last_modified_time": "2021-06-24 17:54:30"
            }

def test_insert_file_info(api):
    file_info = {"name": "test.dll", "size": 5000000000000, 
            "creation_time": "2021-06-24 21:00:00", "last_modified_time": "2021-06-24 21:00:05"}
    resp = api.post("/files", data = json.dumps(file_info), content_type = "application/json")
    assert resp.status_code == 201

def test_modify_file_info(api):
    file_info = {"name": "test.jpg", "size": 1000000, "last_modified_time": "2021-06-24 21:35:00"}
    resp = api.patch("/files/test.jpg", data = json.dumps(file_info), content_type = "application/json")

    assert resp.status_code == 200
    file_info["creation_time"] = "2021-06-24 17:54:30"

    resp = api.get("/files/test.jpg")
    modify_file_info = json.loads(resp.data.decode("utf-8"))
    
    assert resp.status_code == 200
    assert file_info == modify_file_info

def test_change_file_name(api):
    change_name_info = {"old_name": "새 텍스트 파일.txt", "new_name": "텍스트.txt"}
    resp = api.patch("/files/새 텍스트 파일.txt/name", 
            data = json.dumps(change_name_info), 
            content_type = "application/json")

    assert resp.status_code == 200
    
    resp = api.get("files/텍스트.txt")
    assert resp.status_code == 200
    assert json.loads(resp.data.decode("utf-8")) is not None

def test_delete_file_info(api):
    resp = api.delete("/files/새 텍스트 파일.txt")
    assert resp.status_code == 202
    
    resp = api.get("/files")
    file_info_list = json.loads(resp.data.decode("utf-8"))
    assert resp.status_code == 200
    assert file_info_list == [
            {
                "name": "test.jpg",
                "size": 5000,
                "creation_time": "2021-06-24 17:54:30",
                "last_modified_time": "2021-06-24 17:54:30"
            }]
