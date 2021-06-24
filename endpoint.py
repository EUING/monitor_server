from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/files", methods=["POST"])
def add_file():
    add_file = request.json
    return jsonify(add_file), 201

@app.route("/files/<string:file_name>", methods=["PATCH"])
def modify_file(file_name):
    modify_file = request.json
    print(modify_file)
    return jsonify(modify_file), 200

@app.route("/files/<string:file_name>", methods=["DELETE"])
def remove_file(file_name):
    print(file_name)
    return "", 202

@app.route("/files/<string:file_name>/name", methods=["PATCH"])
def rename_file(file_name):
    rename_file = request.json
    print(rename_file)
    return jsonify(rename_file), 200

app.run(host="0.0.0.0", port=56380)
