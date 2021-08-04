from flask import Flask, jsonify, request, render_template
import json

def create_endpoint(app, item_service):
    @app.route("/")
    def root_index():
        ret, root_contain_list = item_service.get_folder_contain_list()
        if ret is False:
            return "", 500
        
        return render_template("index.html", data_list = root_contain_list, current_url = request.base_url[:-1])

    @app.route("/<path:folder_name>")
    def folder_index(folder_name):
        ret, folder_contain_list = item_service.get_folder_contain_list(folder_name)
        if ret is False:
            return "", 500

        if folder_contain_list is None:
            return "{} is missing or not folder.".format(folder_name), 404

        return render_template("index.html", data_list = folder_contain_list, current_url = request.base_url)

    @app.route("/item/info/<path:item_name>", methods=["PATCH"])
    def rename_item_info(item_name):
        change_name_info = request.json
        change_name_info["old_name"] = item_name

        ret, count = item_service.change_item_name(change_name_info)
        if ret is False:
            return "", 500

        if 0 == count:
            return "{} is missing.".format(item_name), 404

        if hasattr(app, "broadcast"):
            change_name_info["event"] = "rename"
            app.broadcast(json.dumps(change_name_info))

        return "", 200

    @app.route("/item/info/<path:item_name>", methods=["DELETE"])
    def delete_item_info(item_name):
        ret, count = item_service.delete_item_info(item_name)
        if ret is False:
            return "", 500

        if 0 == count:
            return "{} is missing.".format(item_name), 200

        if hasattr(app, "broadcast"):
            app.broadcast(json.dumps({"event":"remove", "name": item_name}))

        return "", 204

    @app.route("/item/info/<path:item_name>", methods=["GET"])
    def get_item_info(item_name):
        ret, item_info = item_service.get_item_info(item_name)
        if ret is False:
            return "", 500

        if item_info is None:
            return "{} is missing.".format(item_name), 404

        return jsonify(item_info), 200

    @app.route("/item/info/<path:item_name>", methods=["PUT"])
    def insert_item_info(item_name):
        ret, find_item = item_service.get_item_info(item_name)
        if ret is False:
            return "", 500

        item_info = request.json
        item_info["name"] = item_name

        if find_item is not None:
            ret, count = item_service.modify_item_info(item_info)
            if ret is False:
                return "", 500

            response_code = 200
        else:
            ret, count = item_service.insert_item_info(item_info)
            if ret is False:
                return "", 500

            response_code = 201

        if hasattr(app, "broadcast"):
            item_info["event"] = "download"
            app.broadcast(json.dumps(item_info))
        
        return "", response_code

    @app.route("/item/contain", methods=["GET"])
    def get_root_contain_list():
        ret, root_contain_list = item_service.get_folder_contain_list()
        if ret is False:
            return "", 500

        return jsonify(root_contain_list), 200

    @app.route("/item/contain/<path:folder_name>", methods=["GET"])
    def get_folder_contain_list(folder_name):
        ret, folder_contain_list = item_service.get_folder_contain_list(folder_name)
        if ret is False:
            return "", 500

        if folder_contain_list is None:
            return "{} is missing or not folder.".format(folder_name), 404

        return jsonify(folder_contain_list), 200