from collections import defaultdict


class File(object):
    def __init__(self, name):
        self.map = defaultdict(File)
        self.name = name
        self.isFile = True
        self.value = -1

class FileSystem(object):

    def __init__(self):
        self.root = File("/")
        self.root.isFile = False

    def insert(self, path):
        """
        :type path: str
        :rtype: bool
        """
        array = path.split("/")
        cur = self.root
        for i in range(1, len(array)):
            name = array[i]
            if name not in cur.map:
                if i == len(array)-1:
                    cur.map[name] = File(name)
                    cur.isFile = False
                else:
                    return False
            cur = cur.map[name]
        return True

    # Returns the File object
    def get(self, path):
        print("in get")
        cur = self.root
        if (path == "/" or path == "//"):
            return cur

        array = path.split("/")
        for i in range(1, len(array)):
            name = array[i]
            if name not in cur.map:
                return None
            cur = cur.map[name]
        return cur