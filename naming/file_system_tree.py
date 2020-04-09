from collections import defaultdict
import logging
import sys
import consts as constant
sys.stdout = open("debugFileTree.txt", 'w')

class File(object):
    def __init__(self, name, ip=None, clientport=None, commandport=None):
        """
        File class constructor
        :param name: str
        :param ip: str
        :param clientport: int
        :param commandport: int
        """
        self.map = defaultdict(File)
        self.name = name
        self.isFile = True
        self.value = -1
        self.owners = []
        self.clientport = clientport
        self.commandport = commandport
        self.owners.append({"ip": ip, "clientport" : clientport, "commandport" : commandport})
        self.ip = ip
        self.locked = False
        self.exclusive = False

    def to_string(self):
        """
        Helper to print file object as string
        :return: str
        """
        out = ""
        for k, v in self.map.items():
            out = out + v.name + "  "
        return "name:  " + self.name + " | isFile: " + str(self.isFile) + " | children: " + out

class FileSystem(object):

    def __init__(self):
        """
        Construtor for FileSystem object. This is a trie data structure
        """
        self.root = File("/")
        self.root.isFile = False

    def search(selfself, path):
        """
        Searches the trie for the given path
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
        Inserts a new entry into FileSystem trie
        :param path: str
        :param ip: str
        :param clientport: int
        :param commandport: int
        :return:
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
            else:
                cur.map[name].owners.append({"ip": ip, "clientport" : clientport, "commandport" : commandport})
            cur = cur.map[name]
        return


    def get(self, path):
        """
        Given path, searches the FileSystem trie and returns the File object
        :param path: str
        :return: object
        """
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
        """
        Gicen the path, returns the list of owners of that file
        :param path: str
        :return: list
        """
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
        return cur.owners


    def lockPath(self, path, exclusive, timestamp):
        """
        Locks the given path
        :param path: str
        :param exclusive: bool
        :param timestamp: int
        :return: bool
        """
        cur = self.root
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
            cur.locked = True
            cur.exclusive = False
        cur.exclusive = exclusive
        constant.q.get()
        return True


    def unlockPath(self, path, exclusive):
        """
        Unlocks the given path
        :param path: str
        :param exclusive: bool
        :return: bool
        """
        cur = self.root

        if (path == "/" or path == "//"):
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
            
