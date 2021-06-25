def change_time(time):
    return time.strftime("%Y-%m-%d %H:%M:%S")

class FileService:
    def __init__(self, file_dao):
        self.file_dao = file_dao

    def get_total_file_info(self):
        file_info_list = self.file_dao.get_total_file_info()

        if file_info_list:
            for file_info in file_info_list:
                file_info["creation_time"] = change_time(file_info["creation_time"])
                file_info["last_modified_time"] = change_time(file_info["last_modified_time"])

        return file_info_list if file_info_list else list()

    def get_file_info(self, file_name):
        file_info = self.file_dao.get_file_info(file_name)

        if file_info:
            file_info["creation_time"] = change_time(file_info["creation_time"])
            file_info["last_modified_time"] = change_time(file_info["last_modified_time"])

        return file_info

    def insert_file_info(self, file_info):
        return self.file_dao.insert_file_info(file_info)

    def modify_file_info(self, file_info):
        return self.file_dao.modify_file_info(file_info)

    def change_file_name(self, change_file_info):
        return self.file_dao.change_file_name(change_file_info)

    def delete_file_info(self, file_name):
        return self.file_dao.delete_file_info(file_name)
