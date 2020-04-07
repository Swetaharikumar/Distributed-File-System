from collections import defaultdict
import logging
import sys
import consts as constant
sys.stdout = open("debugFileTree.txt", 'w')

class File(object):
    def __init__(self, name, ip=None, clientport=None, commandport=None):
        self.map = defaultdict(File)
        self.name = name
        self.isFile = True
        self.value = -1
        self.ip = ip
        self.clientport = clientport
        self.commandport = commandport
        self.locked = False
        self.exclusive = False

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


    def insert(self, path, ip=None, clientport=None, commandport = None):
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
                cur.map[name] = File(name, ip, clientport, commandport)
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

    def returnFileOwner(self, path):
        cur = self.root
        if (path == "/" or path == "//" or path == ''):
            return cur.ip,cur.port

        array = path.split("/")
        for i in range(0, len(array)):
            name = array[i]
            if name == '':
                continue
            if name not in cur.map:
                return None
            cur = cur.map[name]
        return cur.ip, cur.clientport, cur.commandport

    def lockPath(self, path, exclusive, timestamp):
        cur = self.root
        # if (path == "/" or path == "//" or path == ''):
        while timestamp != constant.q.queue[0]:
            continue
        while cur.exclusive == True:
            continue
        while cur.locked == True and exclusive == True and (path == "/" or path == "//" or path == ''):
           continue

        logging.info("locked" + cur.name)
        cur.locked = True
        cur.exclusive = False
        if (path == "/" or path == "//" or path == ''):
            cur.exclusive = exclusive
            constant.q.get()
            return True

        array = path.split("/")
        for i in range(0, len(array)):
            name = array[i]
            if name == '':
                continue
            cur = cur.map[name]
            # if cur.exclusive == True:
            #     return False
            logging.info("locked" + cur.name)
            cur.locked = True
            cur.exclusive = False
        cur.exclusive = exclusive
        constant.q.get()
        return True


    def unlockPath(self, path, exclusive):
        cur = self.root

        if (path == "/" or path == "//"):
            # if cur.exclusive != exclusive:
            #     return False
            logging.info("unlocked" + cur.name)
            cur.locked = False
            cur.exclusive = False

        cur.locked = False
        cur.exclusive = False

        array = path.split("/")
        for i in range(0, len(array)):
            name = array[i]
            if name == '':
                continue
            cur = cur.map[name]
            logging.info("unlocked" + cur.name)
            cur.locked = False
            cur.exclusive = False

        return True 
            
