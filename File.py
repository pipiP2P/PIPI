class File_Info:

    def __init__(self, name, description, size, num_of_parts, _hash):
        self.name = name
        self.description = description
        self.size = size
        self.num_of_parts = num_of_parts
        self._hash = _hash

    def to_string(self):
        return (self.name.encode("base64") + ";" + self.description.encode("base64") + ";" + str(self.size) + ";" +
                str(self.num_of_parts) + ";" + self._hash)

    def get_hash(self):
        return self._hash

    def get_name(self):
        return self.name

    def get_size(self):
        return self.size

    def get_file_content(self, part_number):
        # return the content of file at part number
        file_path = PATH + self.name
        file_object = file_path.open('rb')
        file_content = file_object.read()
        file_object.close()
        return file_content[0:10]

    def get_num_of_parts(self):
        return self.num_of_parts
