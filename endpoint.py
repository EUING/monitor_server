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
        item_service.change_item_name(change_name_info)
        return "", 200

    @app.route("/file/info/<path:file_name>", methods=["GET"]) 
    def get_file_info(file_name):
        file_info = item_service.get_file_info(file_name)
        return jsonify(file_info), 200

    @app.route("/file/info", methods=["POST"])
    def insert_file_info():
        file_info = request.json
        item_service.insert_file_info(file_info)
        return "", 201

    @app.route("/file/info/<path:file_name>", methods=["PATCH"])
    def modify_file_info(file_name):
        file_info = request.json
        item_service.modify_file_info(file_info)
        return "", 200

    @app.route("/file/info/<path:file_name>", methods=["DELETE"])
    def delete_file_info(file_name):
        item_service.delete_file_info(file_name)
        return "", 202

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
        return jsonify(folder_info), 200

    @app.route("/folder/info", methods=["POST"])
    def insert_folder_info():
        folder_info = request.json
        item_service.insert_folder_info(folder_info)
        return "", 201

    @app.route("/folder/info/<path:folder_name>", methods=["DELETE"])
    def delete_folder_info(folder_name):
        item_service.delete_folder_info(folder_name)
        return "", 202
