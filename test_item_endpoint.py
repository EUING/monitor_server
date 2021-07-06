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

def test_change_item_name(api):
    change_name_info = {"new_name": "새 폴더/test.bmp"}
    resp = api.patch("/item/info/새 폴더/없는 파일.jpg", 
            data = json.dumps(change_name_info), 
            content_type = "application/json")

    assert resp.status_code == 404

    change_name_info = {"new_name": "새 폴더/test.bmp"}
    resp = api.patch("/item/info/새 폴더/test.jpg", 
            data = json.dumps(change_name_info), 
            content_type = "application/json")

    assert resp.status_code == 200
    
    resp = api.get("/item/info/새 폴더/test.bmp")
    assert resp.status_code == 200
    assert json.loads(resp.data.decode("utf-8")) is not None

def test_get_item_info(api):
    resp = api.get("/item/info/새 폴더/없는 파일.txt")
    assert resp.status_code == 404

    resp = api.get("/item/info/새 폴더/test.jpg")
    assert resp.status_code == 200

    item_info = json.loads(resp.data.decode("utf-8"))
    assert {"parent_id": 2, "name": "test.jpg", "size": 5000, "hash": "hash"} == item_info

def test_insert_item_info(api):
    item_info = {"size": 5000000000000, "hash": "hashhash"}
    resp = api.put("/item/info/test.dll", data = json.dumps(item_info), content_type = "application/json")
    assert resp.status_code == 201

    resp = api.get("/item/info/test.dll")
    assert resp.status_code == 200

    item_info["name"] = "test.dll"
    item_info["parent_id"] = 0

    result_info = json.loads(resp.data.decode("utf-8"))
    assert item_info == result_info

def test_modify_item_info(api):
    item_info = {"size": 1000000, "hash": "hashhash"}
    resp = api.put("/item/info/새 폴더/test.jpg", data = json.dumps(item_info), content_type = "application/json")

    assert resp.status_code == 200
    item_info["name"] = "test.jpg"
    item_info["parent_id"] = 2

    resp = api.get("/item/info/새 폴더/test.jpg")
    modify_item_info = json.loads(resp.data.decode("utf-8"))
    
    assert resp.status_code == 200
    assert item_info == modify_item_info

def test_delete_item_info(api):
    resp = api.delete("/item/info/새 텍스트 파일.txt")
    assert resp.status_code == 204
    
    resp = api.get("/item/info/새 텍스트 파일.txt")
    assert resp.status_code == 404

    resp = api.delete("/item/info/새 폴더")
    assert resp.status_code == 204

    resp = api.get("item/contain")
    assert resp.status_code == 200

    result = json.loads(resp.data.decode("utf-8"))
    assert [] == result

def test_root_contain_list(api):
    resp = api.get("/item/contain")
    assert resp.status_code == 200
    
    contain_list = json.loads(resp.data.decode("utf-8"))
    assert [{"parent_id": 0, "name": "새 텍스트 파일.txt", "size": 10, "hash": "hash"},
    {"parent_id": 0, "name": "새 폴더", "size": -1, "hash": ""}] == contain_list

def test_folder_contain_list(api):
    resp = api.get("/item/contain/새 폴더")
    assert resp.status_code == 200

    contain_list = json.loads(resp.data.decode("utf-8"))
    assert [{"parent_id": 2, "name": "test.jpg", "size": 5000, "hash": "hash"},
    {"parent_id": 2, "name": "새 텍스트 파일.txt", "size": 10, "hash": "hash"},
    {"parent_id": 2, "name": "새 폴더", "size": -1, "hash": ""}] == contain_list