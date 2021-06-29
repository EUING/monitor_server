from flask import Flask, jsonify, request, render_template

def create_endpoint(app, item_service):
    @app.route("/")
    def root_index():
        root_contain_list = item_service.get_folder_contain_list()
        return render_template("index.html", data_list = root_contain_list)

    @app.route("/<path:folder_name>")
    def folder_index(folder_name):
        folder_contain_list = item_service.get_folder_contain_list(folder_name)
        return render_template("index.html", data_list = folder_contain_list)

    @app.route("/item/name/<path:item_name>", methods=["PATCH"])
    def rename_item_info(item_name):
        change_name_info = request.json
        count = item_service.change_item_name(change_name_info)
        if count == 0:
            return jsonify(change_name_info), 404

        return "", 200

    @app.route("/item/info/<path:item_name>", methods=["DELETE"])
    def delete_file_info(item_name):
        count = item_service.delete_item_info(item_name)
        if count == 0:
            return jsonify(file_name), 404

        return "", 204

    @app.route("/file/info/<path:file_name>", methods=["GET"]) 
    def get_file_info(file_name):
        file_info = item_service.get_file_info(file_name)
        if file_info is None:
            return jsonify(file_name), 404

        return jsonify(file_info), 200

    @app.route("/file/info", methods=["POST"])
    def insert_file_info():
        file_info = request.json
        count = item_service.insert_file_info(file_info)
        if count == 0:
            return jsonify(file_info), 404

        return "", 201

    @app.route("/file/info/<path:file_name>", methods=["PATCH"])
    def modify_file_info(file_name):
        file_info = request.json
        count = item_service.modify_file_info(file_info)
        if count == 0:
            return jsonify(file_name), 404

        return "", 200

    @app.route("/folder/contain", methods=["GET"])
    def get_root_contain_list():
        root_contain_list = item_service.get_folder_contain_list()
        return jsonify(root_contain_list), 200

    @app.route("/folder/contain/<path:folder_name>", methods=["GET"])
    def get_folder_contain_list(folder_name):
        folder_contain_list = item_service.get_folder_contain_list(folder_name)
        return jsonify(folder_contain_list), 200

    @app.route("/folder/info/<path:folder_name>", methods=["GET"]) 
    def get_folder_info(folder_name):
        folder_info = item_service.get_folder_info(folder_name)
        if folder_info is None:
            return jsonify(folder_name), 404

        return jsonify(folder_info), 200

    @app.route("/folder/info", methods=["POST"])
    def insert_folder_info():
        folder_info = request.json
        count = item_service.insert_folder_info(folder_info)
        if count == 0:
            return jsonify(folder_info), 404

        return "", 201
