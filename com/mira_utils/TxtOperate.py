class TxtOperate(object):
    def __init__(self):
        self.encoding = "utf-8"

    def read_file_2_list(self, path_name, islower=True, encoding="utf-8"):
        list_name = []
        if islower is True:
            with open(path_name, 'r', encoding=encoding) as f:
                for line in f:
                    list_name.append(line.lower().strip())
        else:
            with open(path_name, 'r', encoding=encoding) as f:
                for line in f:
                    list_name.append(line.strip())
        return list_name

    def save_list_2_file(self, path_name, list_name, encoding="utf-8"):
        file_object = open(path_name, 'w', encoding=encoding)
        for i in list_name:
            file_object.write(str(i))
            file_object.write('\n')
        file_object.close()
