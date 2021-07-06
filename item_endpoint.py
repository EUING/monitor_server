from flask import Flask, jsonify, request, render_template

def create_endpoint(app, item_service):
    @app.route("/")
    def root_index():
        root_contain_list = item_service.get_folder_contain_list()
        current_url = request.base_url[:-1]
        return render_template("index.html", data_list = root_contain_list, current_url = current_url)

    @app.route("/<path:folder_name>")
    def folder_index(folder_name):
        folder_contain_list = item_service.get_folder_contain_list(folder_name)
        if folder_contain_list is None:
            return "{} is missing.".format(folder_name), 404
        current_url = request.base_url
        return render_template("index.html", data_list = folder_contain_list, current_url = current_url)

    @app.route("/item/name/<path:item_name>", methods=["PATCH"])
    def rename_item_info(item_name):
        change_name_info = request.json
        change_name_info["old_name"] = item_name

        count = item_service.change_item_name(change_name_info)
        if count == 0:
            return "{} is missing.".format(item_name), 404

        return "", 200

    @app.route("/item/info/<path:item_name>", methods=["DELETE"])
    def delete_file_info(item_name):
        count = item_service.delete_item_info(item_name)
        if count == 0:
            return "{} is missing.".format(item_name), 200

        return "", 204

    @app.route("/file/info/<path:file_name>", methods=["GET"]) 
    def get_file_info(file_name):
        file_info = item_service.get_file_info(file_name)
        if file_info is None:
            return "{} is missing.".format(file_name), 404

        return jsonify(file_info), 200

    @app.route("/file/info/<path:file_name>", methods=["PUT"])
    def insert_file_info(file_name):
        find_file = item_service.get_file_info(file_name)
        if find_file is not None:
            return "{} already exists.".format(file_name), 200

        file_info = request.json
        file_info["name"] = file_name

        count = item_service.insert_file_info(file_info)
        if count == 0:
            return "", 400

        return "", 201

    @app.route("/file/info/<path:file_name>", methods=["PATCH"])
    def modify_file_info(file_name):
        file_info = request.json
        file_info["name"] = file_name

        count = item_service.modify_file_info(file_info)
        if count == 0:
            return "{} is missing.".format(file_name), 404

        return "", 200

    @app.route("/folder/contain", methods=["GET"])
    def get_root_contain_list():
        root_contain_list = item_service.get_folder_contain_list()
        return jsonify(root_contain_list), 200

    @app.route("/folder/contain/<path:folder_name>", methods=["GET"])
    def get_folder_contain_list(folder_name):
        folder_contain_list = item_service.get_folder_contain_list(folder_name)
        
        if folder_contain_list is None:
            return "{} is missing.".format(folder_name), 404

        return jsonify(folder_contain_list), 200

    @app.route("/folder/info/<path:folder_name>", methods=["GET"]) 
    def get_folder_info(folder_name):
        folder_info = item_service.get_folder_info(folder_name)
        if folder_info is None:
            return "{} is missing.".format(folder_name), 404

        return jsonify(folder_info), 200

    @app.route("/folder/info/<path:folder_name>", methods=["PUT"])
    def insert_folder_info(folder_name):
        find_folder = item_service.get_folder_info(folder_name)
        if find_folder is not None:
            return "{} already exists.".format(folder_name), 200

        folder_info = request.json
        folder_info["name"] = folder_name

        count = item_service.insert_folder_info(folder_info)
        if count == 0:
            return "", 400

        return "", 201
