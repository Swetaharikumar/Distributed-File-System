"""
APIs and their helpers for naming server
Uses Flask module for REST API framework
"""
import consts as constant
from flask import Flask, request, jsonify
from threading import Thread
import json
import sys
from file_system_tree import File, FileSystem
import requests
import logging
import random


namingService = Flask('namingServer')  # Creating the Service web server
namingRegister = Flask('namingRegister')  # Creating the Registration web server
fs = FileSystem()

def startNamingService():
    namingService.run(host='localhost', port=sys.argv[1], threaded=True)

def startNamingRegister():
    namingRegister.run(host='localhost', port=sys.argv[2])


def make_response(content, status_code):
    """
    Helper to form response of naming service
    :param content: str
    :param status_code: int
    :return: object
    """
    response = namingService.response_class(
        response=content,
        status=status_code,
        mimetype='application/json'
    )
    return response

def make_register_response(content, status_code):
    """
    Helper to form response of naming server's register service
    :param content: str
    :param status_code: int
    :return: object
    """
    response = namingRegister.response_class(
        response=content,
        status=status_code,
        mimetype='application/json'
    )
    return response

def create_url_helper (server_ip, server_port, api):
    """
    Helper to form url given ip, port and api path
    :param server_ip: str
    :param server_port: int
    :param api: str
    :return: str
    """
    url = "http://" + server_ip + ":" + str(server_port) + api
    return url

@namingService.route('/is_valid_path', methods=['POST'])
def isValidPath():
    """
    Handler for is_valid_path api
    :return: object
    """
    pathJson = request.get_json()
    path = pathJson["path"]

    constant.boolReturn["success"] = True
    # three cases where input is invalid
    if not path or ':' in path or path[0] != '/':
        constant.boolReturn["success"] = False

    content = json.dumps(constant.boolReturn)
    response = make_response(content, 200)
    return response


@namingService.route('/getstorage', methods=['POST'])
def getStorage():
    """
    Handler for /getstorage api
    :return: object
    """
    pathJson = request.get_json()
    path = pathJson["path"]

    # Not a valid path
    if not isValidPathHelper (path):
        constant.exceptionReturn["exception_type"] = "IllegalArgumentException"
        constant.exceptionReturn["exception_info"] = "[getstorage] given path is invalid"
        content =  json.dumps(constant.exceptionReturn)
        response = make_response(content, 404)
        return response

    # Non-existent file and reject directory
    node  = fs.get(path)
    if not node or not node.isFile:
        constant.exceptionReturn["exception_type"] = "FileNotFoundException"
        constant.exceptionReturn["exception_info"] = "[getstorage] File/path cannot be found."
        content =  json.dumps(constant.exceptionReturn)
        response = make_response(content, 404)
        return response

    getStorageReturn = {"server_ip": node.ip, "server_port": node.clientport}
    content = json.dumps(getStorageReturn)
    response = make_response(content, 200)
    return response


@namingService.route('/list', methods=['POST'])
def list():
    """
    Handler for /list api
    :return: object
    """
    pathJson = request.get_json()
    path = pathJson["path"]

    # Not a valid path
    if not isValidPathHelper (path):
        constant.exceptionReturn["exception_type"] = "IllegalArgumentException"
        constant.exceptionReturn["exception_info"] = "given path is invalid"
        content =  json.dumps(constant.exceptionReturn)
        response = make_response(content, 404)
        return response

    # File not found
    node  = fs.get(path)
    if not node or node.isFile:
        constant.exceptionReturn["exception_type"] = "FileNotFoundException"
        constant.exceptionReturn["exception_info"] = "given path does not refer to a directory."
        content =  json.dumps(constant.exceptionReturn)
        response = make_response(content, 404)
        return response

    filesReturn = {"files" : []}

    for k,v in node.map.items():
        if k not in filesReturn['files']:
            filesReturn['files'].append(k)

    content = json.dumps(filesReturn)
    response = make_response(content, 200)
    return response


@namingService.route('/is_directory', methods=['POST'])
def isDirectory():
    """
    Handler for /is_directory api
    :return: object
    """
    pathJson = request.get_json()
    path = pathJson["path"]

    if not isValidPathHelper(path):
        constant.exceptionReturn["exception_type"] = "IllegalArgumentException"
        constant.exceptionReturn["exception_info"] = "[is_directory] given path is invalid"
        content =  json.dumps(constant.exceptionReturn)
        response = make_response(content, 404)
        return response

    node = fs.get(path)
    if not node:
        constant.exceptionReturn["exception_type"] = "FileNotFoundException"
        constant.exceptionReturn["exception_info"] = "[is_directory] File/path cannot be found."
        content =  json.dumps(constant.exceptionReturn)
        response = make_response(content, 404)
        return response

    constant.boolReturn["success"] = not node.isFile
    content = json.dumps(constant.boolReturn)
    response = make_response(content, 200)
    return response


@namingService.route('/create_file', methods=['POST'])
def createFile():
    """
    Handler for /create_file api
    :return: object
    """
    pathJson = request.get_json()
    path = pathJson["path"]
    if not isValidPathHelper(path):
        constant.exceptionReturn["exception_type"] = "IllegalArgumentException"
        constant.exceptionReturn["exception_info"] = "[create_file / create_directory] given path is invalid"
        content =  json.dumps(constant.exceptionReturn)
        response = make_response(content, 404)
        return response

    parent_path = path.rsplit('/', 1)[0]
    parent_node = fs.get(parent_path)
    # Reject when parent directory does not exist | parent dir is a file
    if not parent_node or parent_node.isFile:
        constant.exceptionReturn["exception_type"] = "FileNotFoundException"
        constant.exceptionReturn["exception_info"] = "[create_file / create_directory] File/path cannot be found."
        content =  json.dumps(constant.exceptionReturn)
        response = make_response(content, 404)
        return response

    # Return false when file already exists
    cur_node = fs.get(path)
    if cur_node:
        constant.boolReturn["success"] = False
        content = json.dumps(constant.boolReturn)
        response = make_response(content, 200)
        return response

    fs.insert(path)
    constant.boolReturn["success"] = True
    content = json.dumps(constant.boolReturn)
    response = make_response(content, 200)

    server_id = random.randint(0, len(constant.storageServers) - 1);
    ip = constant.storageServers[server_id]['storage_ip']
    port = constant.storageServers[server_id]['command_port']
    url = create_url_helper (ip, port, "/storage_create")
    headers = {'Content-type': 'application/json'}
    data = {"path" : path}
    requests.post(url=url, data=json.dumps(data), headers=headers) #check result ??

    return response


@namingService.route('/create_directory', methods=['POST'])
def createDir():
    """
    Handler for /create_directory. Creates new directory at the
    given path.
    :return: object
    """
    pathJson = request.get_json()
    path = pathJson["path"]

    if not isValidPathHelper(path):
        constant.exceptionReturn["exception_type"] = "IllegalArgumentException"
        constant.exceptionReturn["exception_info"] = "[create_file / create_directory] given path is invalid"
        content =  json.dumps(constant.exceptionReturn)
        response = make_response(content, 404)
        return response

    parent_path = path.rsplit('/', 1)[0]
    parent_node = fs.get(parent_path)
    # Reject when parent directory does not exist | parent dir is a file
    if not parent_node or parent_node.isFile:
        constant.exceptionReturn["exception_type"] = "FileNotFoundException"
        constant.exceptionReturn["exception_info"] = "[create_file / create_directory] File/path cannot be found."
        content =  json.dumps(constant.exceptionReturn)
        response = make_response(content, 404)
        return response

    # Return false when file already exists
    cur_node = fs.get(path)
    if cur_node:
        constant.boolReturn["success"] = False
        content = json.dumps(constant.boolReturn)
        response = make_response(content, 200)
        return response

    fs.insert(path)
    node = fs.get(path)
    node.isFile = False

    constant.boolReturn["success"] = True
    content = json.dumps(constant.boolReturn)
    response = make_response(content, 200)
    return response



@namingService.route('/delete', methods=['POST'])
def deleteFiles():
    """
    Handler for /delete api. Deletes all replicas of given file.
    :return: object
    """
    pathJson = request.get_json()
    path = pathJson["path"]

    if not isValidPathHelper(path):
        constant.exceptionReturn["exception_type"] = "IllegalArgumentException"
        constant.exceptionReturn["exception_info"] = "[delete file] given path is invalid"
        content =  json.dumps(constant.exceptionReturn)
        response = make_response(content, 404)
        return response
    node  = fs.get(path)
    if not node:
        constant.exceptionReturn["exception_type"] = "FileNotFoundException"
        constant.exceptionReturn["exception_info"] = "[delete_file] path cannot be found"
        content =  json.dumps(constant.exceptionReturn)
        response = make_response(content, 404)
        return response


    if (path == "/" or path == "//"):
        data = {"success" : False}
        content =  json.dumps(data)
        response = make_response(content, 200)
        return response


    if path in constant.ReplicatedFiles:
        deleteFiles = {'path' : None}
        deleteFiles['path'] = path
        url = create_url_helper (constant.ReplicatedFiles[path]['ip'], constant.ReplicatedFiles[path]['port'], "/storage_delete" )
        headers = {'Content-type': 'application/json'}
        requests.post(url=url, data=json.dumps(deleteFiles), headers=headers)

    owners = fs.returnFileOwner(path)
    for owner in owners:
        host_ip, host_clientport, host_commandport = owner["ip"], owner["clientport"], owner["commandport"]
        url = create_url_helper (host_ip, host_commandport, "/storage_delete")
        headers = {'Content-type': 'application/json'}
        data = {"path" : path}
        requests.post(url=url, data=json.dumps(data), headers=headers)

    data = {"success" : True}
    content =  json.dumps(data)
    response = make_response(content, 200)
    return response


@namingService.route('/lock', methods=['POST'])
def lockPath():
    """
    Handler for /lock api. Locks the given file.
    :return: object
    """
    pathJson = request.get_json()
    path = pathJson["path"]

    if not isValidPathHelper(path):
        constant.exceptionReturn["exception_type"] = "IllegalArgumentException"
        constant.exceptionReturn["exception_info"] = "Given path is invalid(isValidPath failed)"
        content =  json.dumps(constant.exceptionReturn)
        response = make_response(content, 404)
        return response

    node  = fs.get(path)
    if not node:
        constant.exceptionReturn["exception_type"] = "FileNotFoundException"
        constant.exceptionReturn["exception_info"] = "path cannot be found"
        content =  json.dumps(constant.exceptionReturn)
        response = make_response(content, 404)
        return response

    exclusive = pathJson["exclusive"]

    if exclusive == False:
        if path not in constant.AccessCount:
            constant.AccessCount[path] = 0
        constant.AccessCount[path]+=1
        if constant.AccessCount[path] == 20:
            constant.AccessCount[path] = 0
            if path not in constant.ReplicatedFiles:
                constant.ReplicatedFiles[path] = dict()

            #Call copy from here
            owners = fs.returnFileOwner(path)
            host_ip, host_clientport, host_commandport = owners[0]["ip"], owners[0]["clientport"], owners[0]["commandport"]
            ip = None
            port = None
            for server in constant.storageServers:
                if server['storage_ip'] != host_ip or server['command_port'] != host_commandport:
                    ip = server['storage_ip']
                    port = server['command_port']
                    constant.ReplicatedFiles[path]['ip'] = server['storage_ip']
                    constant.ReplicatedFiles[path]['port'] = server['command_port']

            for owner in owners:
                host_ip, host_clientport, host_commandport = owner["ip"], owner["clientport"], owner["commandport"]
                url = create_url_helper (host_ip ,port, "/storage_copy")
                headers = {'Content-type': 'application/json'}
                data = {"path" : path, "server_ip": host_ip, "server_port": host_clientport}
                requests.post(url=url, data=json.dumps(data), headers=headers)

    constant.lockId +=1
    constant.q.put(constant.lockId) 
    
    success = fs.lockPath(path, exclusive, constant.lockId)
    
    if exclusive == True and path in constant.ReplicatedFiles:
        deleteFiles = {'path' : None}
        deleteFiles['path'] = path
        url = create_url_helper (constant.ReplicatedFiles[path]['ip'], constant.ReplicatedFiles[path]['port'], "/storage_delete")
        # del constant.ReplicatedFiles[path]
        headers = {'Content-type': 'application/json'}
        requests.post(url=url, data=json.dumps(deleteFiles), headers=headers)

    
    if success == False:
        logging.info("UNABLE TO LOCK")

    if success == True:
        response = make_response(None, 200)
        return response

    constant.exceptionReturn["exception_type"] = "IllegalArgumentException"
    constant.exceptionReturn["exception_info"] = "Lock failed because of conflict"
    content =  json.dumps(constant.exceptionReturn)
    response = make_response(content, 404)
    return response


@namingService.route('/unlock', methods=['POST'])
def unlockPath():
    """
    Handler for /unlock api. Unlocks the file given filepath
    :return: object
    """
    pathJson = request.get_json()
    path = pathJson["path"]

    if not isValidPathHelper(path):
        constant.exceptionReturn["exception_type"] = "IllegalArgumentException"
        constant.exceptionReturn["exception_info"] = "Given path is invalid(isValidPath failed)"
        content =  json.dumps(constant.exceptionReturn)
        response = make_response(content, 404)
        return response

    node  = fs.get(path)
    if not node:
        constant.exceptionReturn["exception_type"] = "IllegalArgumentException"
        constant.exceptionReturn["exception_info"] = "Bad path given"
        content =  json.dumps(constant.exceptionReturn)
        response = make_response(content, 404)
        return response

    exclusive = pathJson["exclusive"]
    success = fs.unlockPath(path, exclusive)
    if success == True:
        response = make_response(None, 200)
        return response

    constant.exceptionReturn["exception_type"] = "IllegalArgumentException"
    constant.exceptionReturn["exception_info"] = "Unlock failed because of conflict"
    content =  json.dumps(constant.exceptionReturn)
    response = make_response(content, 404)
    return response


def isValidPathHelper (path):
    """
    Helper for validating path.
    :param path: str
    :return: bool
    """
    if not path or ':' in path or path[0] != '/':
        return False
    else:
        return True


@namingRegister.route('/register', methods = ['POST'])
def register():
    """
    Handler for registering storage server.
    Called by storage servers to register themselves.
    :return: object
    """
    ssReq = request.get_json()
    storageServerEntry = {"storage_ip": ssReq['storage_ip'],
                          "client_port": ssReq['client_port'],
                          "command_port" : ssReq['command_port'],
                          "files" : []}

    logging.info("New storage server " + str(ssReq['command_port']))
    deleteFiles = {'files' : []}


    for item in constant.storageServers:
        if ssReq['storage_ip'] == item['storage_ip'] and ssReq['client_port'] == item['client_port'] \
                and ssReq['command_port'] == item['command_port']:
            constant.exceptionReturn["exception_type"] = "IllegalStateException"
            constant.exceptionReturn["exception_info"] = "This storage client already registered."

            content =  json.dumps(constant.exceptionReturn)
            response = make_register_response(content, 409)
            return response

    for reqFile in ssReq['files']:
        if reqFile == '/':
            continue

        node = fs.get(reqFile)

        if node:
            deleteFiles['files'].append(reqFile)
        else:
            fs.insert(reqFile, ssReq['storage_ip'], ssReq['client_port'], ssReq['command_port'])
            storageServerEntry['files'].append(reqFile)


    constant.storageServers.append(storageServerEntry)
    content = json.dumps(deleteFiles)
    response = make_register_response(content, 200)
    return response



if __name__ == "__main__":
    logging.basicConfig(filename='example_naming.log',level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    Thread(target=startNamingRegister).start()
    startNamingService()






