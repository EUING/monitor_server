import pathlib
import os
import queue
import copy

def change_time(time):
    return time.strftime("%Y-%m-%d %H:%M:%S")

class ItemService:
    def __init__(self, item_dao):
        self.item_dao = item_dao

    def get_parent_id(self, relative_path):
        relative_path = os.path.join(os.pardir, relative_path)
        dir_path, file_name = os.path.split(relative_path)
        sep_list = dir_path.split(os.path.sep)
        
        parent_id = -1
        for folder_name in sep_list:
            if os.pardir == folder_name:
                parent_id = 0
                continue

            parent_id = self.item_dao.get_item_id(folder_name, parent_id)

        return parent_id

    def change_item_name(self, change_name_info):
        old_posix_path = pathlib.PureWindowsPath(change_name_info["old_name"]).as_posix()
        new_posix_path = pathlib.PureWindowsPath(change_name_info["new_name"]).as_posix()
        parent_id = self.get_parent_id(old_posix_path)
        if parent_id is None:
            return 0

        param = copy.deepcopy(change_name_info)
        param["parent_id"] = parent_id
        param["old_name"] = os.path.basename(old_posix_path)
        param["new_name"] = os.path.basename(new_posix_path)

        return self.item_dao.change_item_name(param)

    def get_file_info(self, file_name):
        posix_path = pathlib.PureWindowsPath(file_name).as_posix()
        parent_id = self.get_parent_id(posix_path)
        if parent_id is None:
            return 0

        file_name = os.path.basename(posix_path)
        file_info = self.item_dao.get_file_info(file_name, parent_id)

        if file_info:
            file_info["creation_time"] = change_time(file_info["creation_time"])
            file_info["last_modified_time"] = change_time(file_info["last_modified_time"])

        return file_info

    def insert_file_info(self, file_info):
        posix_path = pathlib.PureWindowsPath(file_info["name"]).as_posix()
        parent_id = self.get_parent_id(posix_path)
        if parent_id is None:
            return 0
        
        param = copy.deepcopy(file_info)
        param["parent_id"] = parent_id
        param["name"] = os.path.basename(posix_path)

        return self.item_dao.insert_file_info(param)

    def modify_file_info(self, file_info):
        posix_path = pathlib.PureWindowsPath(file_info["name"]).as_posix()
        parent_id = self.get_parent_id(posix_path)
        if parent_id is None:
            return 0
        
        param = copy.deepcopy(file_info)
        param["parent_id"] = parent_id
        param["name"] = os.path.basename(posix_path)

        return self.item_dao.modify_file_info(param)

    def get_folder_info(self, folder_name):
        posix_path = pathlib.PureWindowsPath(folder_name).as_posix()
        parent_id = self.get_parent_id(posix_path)
        if parent_id is None:
            return 0

        folder_name = os.path.basename(posix_path)
        folder_info = self.item_dao.get_folder_info(folder_name, parent_id)

        if folder_info:
            folder_info["creation_time"] = change_time(folder_info["creation_time"])

        return folder_info

    def get_folder_contain_list(self, folder_name=None):
        if folder_name is None:
            item_id = 0
        else:
            posix_path = pathlib.PureWindowsPath(folder_name).as_posix()
            parent_id = self.get_parent_id(posix_path)
            folder_name = os.path.basename(posix_path)
            item_id = self.item_dao.get_item_id(folder_name, parent_id)

        folder_contain_list = self.item_dao.get_folder_contain_list(item_id)

        for contain_info in folder_contain_list:
            contain_info["creation_time"] = change_time(contain_info["creation_time"])
            if contain_info["last_modified_time"] is not None:
                contain_info["last_modified_time"] = change_time(contain_info["last_modified_time"])

        return folder_contain_list

    def insert_folder_info(self, folder_info):
        posix_path = pathlib.PureWindowsPath(folder_info["name"]).as_posix()
        parent_id = self.get_parent_id(posix_path)
        if parent_id is None:
            return 0

        param = copy.deepcopy(folder_info)
        param["parent_id"] = parent_id
        param["name"] = os.path.basename(posix_path)

        return self.item_dao.insert_folder_info(param)

    def delete_item_info(self, item_path):
        delete_list = list()
        posix_path = pathlib.PureWindowsPath(item_path).as_posix()
        parent_id = self.get_parent_id(posix_path)
        folder_name = os.path.basename(posix_path)
        
        folder_list = queue.Queue()
        folder_list.put({"name": folder_name, "parent_id": parent_id})
        delete_list.append({"item_name": folder_name, "parent_id": parent_id})

        while folder_list.qsize() > 0:
            folder_info = folder_list.get()
            item_id = self.item_dao.get_item_id(folder_info["name"], folder_info["parent_id"])

            folder_contain_list = self.item_dao.get_folder_contain_list(item_id)

            for contain_info in folder_contain_list:
                delete_list.append({"item_name": contain_info["name"], "parent_id": contain_info["parent_id"]})
                if contain_info["last_modified_time"] is None:
                    folder_list.put({"name": contain_info["name"], "parent_id": contain_info["parent_id"]})

        count = 0
        for delete in delete_list:
            count += self.item_dao.delete_item_info(delete["item_name"], delete["parent_id"])

        return count
