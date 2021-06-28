import json
from flask import Flask
from sqlalchemy import create_engine

from item_dao import ItemDao
from item_service import ItemService
from endpoint import create_endpoint

def create_app(test_mode = False):
    app = Flask(__name__)

    with open("config.json") as json_file:
        json_data = json.load(json_file)

    if test_mode is False:
        app.config.update(json_data["config"])
    else:
        app.config.update(json_data["test_config"])

    database = create_engine(app.config["DB_URL"], encoding = "utf-8", max_overflow = 0)

    item_service = ItemService(ItemDao(database))

    create_endpoint(app, item_service)

    return app
