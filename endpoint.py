from flask import Flask, jsonify, request, render_template

def create_endpoint(app, file_service):
    @app.route("/")
    def index():
        file_info_list = file_service.get_total_file_info()
        return render_template("index.html", data_list = file_info_list)

    @app.route("/files", methods=["GET"])
    def get_total_file_info():
        file_info_list = file_service.get_total_file_info()
        return jsonify(file_info_list), 200
    
    @app.route("/files/<string:file_name>", methods=["GET"])
    def get_file_info(file_name):
        file_info = file_service.get_file_info(file_name)
        return jsonify(file_info), 200

    @app.route("/files", methods=["POST"])
    def insert_file_info():
        file_info = request.json
        file_service.insert_file_info(file_info)
        return "", 201

    @app.route("/files/<string:file_name>", methods=["PATCH"])
    def modify_file_info(file_name):
        file_info = request.json
        file_service.modify_file_info(file_info)
        return "", 200

    @app.route("/files/<string:file_name>", methods=["DELETE"])
    def delete_file_info(file_name):
        file_service.delete_file_info(file_name)
        return "", 202

    @app.route("/files/<string:file_name>/name", methods=["PATCH"])
    def rename_file_info(file_name):
        change_name_info = request.json
        file_service.change_file_name(change_name_info)
        return "", 200
