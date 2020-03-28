from collections import defaultdict


class File(object):
    def __init__(self, name, ip=None, port=None):
        self.map = defaultdict(File)
        self.name = name
        self.isFile = True
        self.value = -1
        self.ip = ip
        self.port = port

    def to_string(self):
        out = ""
        for k, v in self.map.items():
            out = out + v.name + "  "
        return "name:  " + self.name + " | isFile: " + str(self.isFile) + " | children: " + out

class FileSystem(object):

    def __init__(self):
        self.root = File("/")
        self.root.isFile = False

    def search(selfself, path):
        """
        :type path: str
        :rtype: bool
        """
        array = path.split("/")
        cur = self.root
        for i in range(0, len(array)):
            name = array[i]
            if name == '':
                continue
            if name not in cur.map:
                return False

            cur = cur.map[name]
        return True


    def insert(self, path, ip=None, port=None):
        """
        :type path: str
        :rtype: void
        """
        array = path.split("/")
        cur = self.root
        for i in range(0, len(array)):
            name = array[i]
            if name == '':
                continue
            if name not in cur.map:
                cur.map[name] = File(name, ip, port)
                cur.isFile = False

            cur = cur.map[name]
        return

    # Returns the File object
    def get(self, path):
        cur = self.root
        if (path == "/" or path == "//" or path == ''):
            return cur

        array = path.split("/")
        for i in range(0, len(array)):
            name = array[i]
            if name == '':
                continue
            if name not in cur.map:
                return None
            cur = cur.map[name]
        return cur