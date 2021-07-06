import os
import queue
import copy

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

            ret, parent_id = self.item_dao.get_item_id(folder_name, parent_id)
            if ret is False:
                return False, -1

        return True, parent_id

    def change_item_name(self, change_name_info):
        ret, parent_id = self.get_parent_id(change_name_info["old_name"])
        if ret is False:
            return False, -1

        param = copy.deepcopy(change_name_info)
        param["parent_id"] = parent_id
        param["old_name"] = os.path.basename(param["old_name"])
        param["new_name"] = os.path.basename(param["new_name"])

        return self.item_dao.change_item_name(param)

    def get_item_info(self, item_name):
        ret, parent_id = self.get_parent_id(item_name)
        if ret is False:
            return False, None

        item_name = os.path.basename(item_name)
        return self.item_dao.get_item_info(item_name, parent_id)

    def insert_item_info(self, item_info):
        ret, parent_id = self.get_parent_id(item_info["name"])
        if ret is False:
            return False, -1
        
        param = copy.deepcopy(item_info)
        param["parent_id"] = parent_id
        param["name"] = os.path.basename(param["name"])

        return self.item_dao.insert_item_info(param)

    def modify_item_info(self, item_info):
        ret, parent_id = self.get_parent_id(item_info["name"])
        if ret is False:
            return False, -1
        
        param = copy.deepcopy(item_info)
        param["parent_id"] = parent_id
        param["name"] = os.path.basename(param["name"])

        return self.item_dao.modify_item_info(param)

    def get_folder_contain_list(self, folder_name=None):
        if folder_name is None:
            item_id = 0
        else:
            ret, parent_id = self.get_parent_id(folder_name)
            if ret is False:
                return False, None

            if parent_id is None:
                return True, None

            folder_name = os.path.basename(folder_name)
            ret, item_info = self.item_dao.get_item_info(folder_name, parent_id)
            if ret is False:
                return False, None

            if item_info is None:
                return True, None

            if item_info["size"] >= 0:
                return True, None

            ret, item_id = self.item_dao.get_item_id(folder_name, parent_id)
            if ret is False:
                return False, None

        return self.item_dao.get_folder_contain_list(item_id)        

    def delete_item_info(self, item_path):
        delete_list = list()
        ret, parent_id = self.get_parent_id(item_path)
        if ret is False:
            return False, -1

        item_name = os.path.basename(item_path)
        folder_list = queue.Queue()
        folder_list.put({"name": item_name, "parent_id": parent_id})
        delete_list.append({"item_name": item_name, "parent_id": parent_id})

        while folder_list.qsize() > 0:
            folder_info = folder_list.get()
            ret, item_id = self.item_dao.get_item_id(folder_info["name"], folder_info["parent_id"])
            if ret is False:
                return False, -1

            ret, folder_contain_list = self.item_dao.get_folder_contain_list(item_id)
            if ret is False:
                return False, -1

            for contain_info in folder_contain_list:
                delete_list.append({"item_name": contain_info["name"], "parent_id": contain_info["parent_id"]})
                if contain_info["size"] < 0:
                    folder_list.put({"name": contain_info["name"], "parent_id": contain_info["parent_id"]})

        count = 0
        for delete in delete_list:
            ret, delete_count = self.item_dao.delete_item_info(delete["item_name"], delete["parent_id"])
            if ret is False:
                return False, -1

            count += delete_count

        return True, count
