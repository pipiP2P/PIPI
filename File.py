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


