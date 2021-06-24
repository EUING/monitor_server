import json
from flask import Flask
from sqlalchemy import create_engine

from file_dao import FileDao
from file_service import FileService
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

    file_service = FileService(FileDao(database))

    create_endpoint(app, file_service)

    return app
