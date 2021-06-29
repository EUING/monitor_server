import json
import pytest

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

def test_change_item_name(api):
    change_name_info = {"new_name": "새 폴더/test.bmp"}
    resp = api.patch("/item/name/새 폴더/test.jpg", 
            data = json.dumps(change_name_info), 
            content_type = "application/json")

    assert resp.status_code == 200
    
    resp = api.get("/file/info/새 폴더/test.bmp")
    assert resp.status_code == 200
    assert json.loads(resp.data.decode("utf-8")) is not None

def test_get_file_info(api):
    resp = api.get("/file/info/새 폴더/test.jpg")
    assert resp.status_code == 200

    file_info = json.loads(resp.data.decode("utf-8"))
    assert file_info == {
                "parent_id": 2,
                "name": "test.jpg",
                "size": 5000,
                "creation_time": "2021-06-24 17:54:30",
                "last_modified_time": "2021-06-24 17:54:30"
                }

def test_insert_file_info(api):
    file_info = {"size": 5000000000000, 
            "creation_time": "2021-06-24 21:00:00", "last_modified_time": "2021-06-24 21:00:05"}
    resp = api.post("/file/info/test.dll", data = json.dumps(file_info), content_type = "application/json")
    assert resp.status_code == 201

    resp = api.get("/file/info/test.dll")
    assert resp.status_code == 200

    file_info["name"] = "test.dll"
    file_info["parent_id"] = 0

    result_info = json.loads(resp.data.decode("utf-8"))
    assert file_info == result_info

def test_modify_file_info(api):
    file_info = {"size": 1000000, "last_modified_time": "2021-06-24 21:35:00"}
    resp = api.patch("/file/info/새 폴더/test.jpg", data = json.dumps(file_info), content_type = "application/json")

    assert resp.status_code == 200
    file_info["name"] = "test.jpg"
    file_info["creation_time"] = "2021-06-24 17:54:30"
    file_info["parent_id"] = 2

    resp = api.get("/file/info/새 폴더/test.jpg")
    modify_file_info = json.loads(resp.data.decode("utf-8"))
    
    assert resp.status_code == 200
    assert file_info == modify_file_info

def test_delete_file_info(api):
    resp = api.delete("/item/info/새 텍스트 파일.txt")
    assert resp.status_code == 204
    
    resp = api.get("/file/info/새 텍스트 파일.txt")
    assert resp.status_code == 404

def test_root_contain_list(api):
    resp = api.get("/folder/contain")
    assert resp.status_code == 200
    
    contain_list = json.loads(resp.data.decode("utf-8"))
    assert contain_list == [
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
            }]

def test_folder_contain_list(api):
    resp = api.get("/folder/contain/새 폴더")
    assert resp.status_code == 200

    contain_list = json.loads(resp.data.decode("utf-8"))
    assert contain_list == [
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

def test_get_folder_info(api):
    resp = api.get("/folder/info/새 폴더")
    assert resp.status_code == 200

    result = json.loads(resp.data.decode("utf-8"))
    assert result == {"parent_id": 0, "name": "새 폴더", "creation_time": "2021-06-28 16:30:00"}

def test_insert_folder_info(api):
    folder_info = {"creation_time": "2021-06-28 23:00:00"}
    resp = api.post("/folder/info/testtest", data = json.dumps(folder_info), content_type = "application/json")

    assert resp.status_code == 201
    resp = api.get("/folder/info/testtest")

    folder_info["name"] = "testtest"
    folder_info["parent_id"] = 0

    assert resp.status_code == 200
    result = json.loads(resp.data.decode("utf-8"))

    assert result == folder_info 

def test_delete_folder_info(api):
    resp = api.delete("/item/info/새 폴더")
    assert resp.status_code == 204

    resp = api.get("folder/contain")
    assert resp.status_code == 200

    result = json.loads(resp.data.decode("utf-8"))
    assert result == [{
                "parent_id": 0,
                "name": "새 텍스트 파일.txt",
                "size": 10,
                "creation_time": "2021-06-24 17:54:30",
                "last_modified_time": "2021-06-24 17:54:30"
                }]
