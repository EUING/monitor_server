import boto3
import json
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

with open("../config.json") as json_file:
    json_data = json.load(json_file)

database = create_engine(json_data["config"]["DB_URL"], encoding = "utf-8", max_overflow = 0)

session = boto3.session.Session()

s3_client = session.client(
    service_name='s3',
    aws_access_key_id='chlguddnjs',
    aws_secret_access_key='Rladmdgur!',
    endpoint_url="http://ggulmo.iptime.org:56390"
)

def isHashExist(key):
    try:
        row = database.execute(text("""
            SELECT
                hash
            FROM items
            WHERE hash = :hash
        """), {"hash": key}).fetchall()

        if not row:
            return False

        return True
    except SQLAlchemyError:
        print(key, "query fail!")
        return True

def deleteS3Object(key):
    print("delete", key)
    response = s3_client.delete_object(
        Bucket="keh-bucket",
        Key=key
    )

    print(response)

object_list = s3_client.list_objects(
    Bucket="keh-bucket"
)

for v in object_list["Contents"]:
    key = v["Key"]
    if not isHashExist(key):
        deleteS3Object(key)