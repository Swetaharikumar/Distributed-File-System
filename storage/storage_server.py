from flask import Flask, request, jsonify
from threading import Thread
import json
import sys
import requests
import consts as constant
import glob
import os
import shutil
import logging
import base64
import errno

clientService = Flask('clientServer')  # Creating the client servcie web server
commandService = Flask('commandServer')  # Creating the command web server

# storagePath = None

def startClientService():
    logging.info("Starting client service")
    # clientService.debug = True
    clientService.run(host='localhost', port=sys.argv[1])

def startCommandService():
    logging.info("Starting command service")
    # commandService.debug = True
    register()
    prune (sys.argv[4])

    commandService.run(host='localhost', port=sys.argv[2])


# call naming server's register api
def register ():
    constant.namingServerPort = sys.argv[3]
    storagePath = sys.argv[4]

    url = constant.namingServerUrl + constant.namingServerPort + constant.namingServerRegisterApi
    logging.info ("register url : " + url)
    data = {"storage_ip": constant.myip,
            "client_port": sys.argv[1],
            "command_port" : sys.argv[2],
            "files" : get_file_paths(storagePath)}

    # headers = {'Content-type': 'application/json'}
    # r = requests.post(url=url, data=json.dumps(data), headers=headers)
    # res = r.json()
    res = call_other_server (url, data)
    remove_files (res['files'], storagePath)

def call_other_server (url, data):
    headers = {'Content-type': 'application/json'}
    r = requests.post(url=url, data=json.dumps(data), headers=headers)
    res = r.json()
    return res


def get_file_paths(path):
    file_paths = []
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            file_paths.append(os.path.join(root, name)[len(path):])
    return file_paths

def prune(path):
    file_paths = []
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            file_paths.append(os.path.join(root, name)[len(path):])
        for name in dirs:
            file_paths.append(os.path.join(root, name)[len(path):])


    for root, dirs, files in os.walk(path, topdown=False):
        for name in dirs:
            prune_path = os.path.join(root, name)
            if os.path.isdir(prune_path) and not os.listdir(prune_path):
                # logging.info(prune_path)
                shutil.rmtree(prune_path)



def remove_files(filepaths, storagePath):
    for fp in filepaths:
        path = storagePath + fp
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)


def make_client_response(content, status_code):
    response = clientService.response_class(
        response=content,
        status=status_code,
        mimetype='application/json'
    )
    return response

def make_command_response(content, status_code):
    response = commandService.response_class(
        response=content,
        status=status_code,
        mimetype='application/json'
    )
    return response

def isValidPathHelper (path):
    if not path or ':' in path or path[0] != '/':
        return False
    else:
        return True


@commandService.route('/storage_delete', methods=['POST'])
def storageDelete():
    pathJson = request.get_json()
    path = pathJson["path"]
    storage_path = sys.argv[4]

    if not isValidPathHelper(path):
        constant.exceptionReturn["exception_type"] = "IllegalArgumentException"
        constant.exceptionReturn["exception_info"] = "[storage_delete] given path is invalid"
        content =  json.dumps(constant.exceptionReturn)
        response = make_command_response(content, 404)
        return response

    filepath = storage_path + path
    if path == "/" or not (os.path.isfile(filepath) or os.path.isdir(filepath)):
        constant.boolReturn["success"] = False
        response = make_command_response(json.dumps(constant.boolReturn), 200)
        return response


    filepaths = [path]
    remove_files(filepaths, storage_path)
    constant.boolReturn["success"] = True
    response = make_command_response(json.dumps(constant.boolReturn), 200)
    return response

@commandService.route('/storage_create', methods=['POST'])
def storageCreate():
    pathJson = request.get_json()
    path = pathJson["path"]
    storagePath = sys.argv[4]

    if not isValidPathHelper(path):
        constant.exceptionReturn["exception_type"] = "IllegalArgumentException"
        constant.exceptionReturn["exception_info"] = "[storage_create] given path is invalid"
        content =  json.dumps(constant.exceptionReturn)
        response = make_command_response(content, 404)
        return response

    filepath = storagePath + path
    if path == "/" or os.path.isfile(filepath) or os.path.isdir(filepath):
        constant.boolReturn["success"] = False
        response = make_command_response(json.dumps(constant.boolReturn), 200)
        return response

    try:
        path_arr = filepath.rsplit('/', 1)
        dir_path = path_arr[0]
        os.makedirs(dir_path, exist_ok=True)
        f = open(filepath, 'w+')
        f.close()
        constant.boolReturn["success"] = True
    except:
        constant.boolReturn["success"] = False

    response = make_command_response(json.dumps(constant.boolReturn), 200)
    return response


@commandService.route('/storage_copy', methods=['POST'])
def storageCopy():
    pathJson = request.get_json()
    path = pathJson["path"]
    server_ip = pathJson["server_ip"]
    server_port = pathJson["server_port"]

    if not isValidPathHelper(path):
        constant.exceptionReturn["exception_type"] = "IllegalArgumentException"
        constant.exceptionReturn["exception_info"] = "[storage_copy] given path is invalid"
        content =  json.dumps(constant.exceptionReturn)
        response = make_command_response(content, 404)
        return response

    url = create_url_helper (server_ip, server_port, constant.storage_size_api)
    data = {"path": path}
    size_res = call_other_server (url, data)


    if ('exception_type' in size_res and size_res['exception_type'] == "FileNotFoundException") or \
            ('success' in size_res and size_res['success'] == False):
        constant.exceptionReturn["exception_type"] = "FileNotFoundException"
        constant.exceptionReturn["exception_info"] = "[storage_copy] given path is directory / doesn't exist"
        content =  json.dumps(constant.exceptionReturn)
        response = make_command_response(content, 404)
        return response

    offset = 0
    url = create_url_helper (server_ip, server_port, constant.storage_read_api)
    data = {"path": path,
            "offset" : offset,
            "length": size_res["size"]}
    read_res = call_other_server (url, data)


    encoded_data = read_res["data"]
    storage_path = sys.argv[4]
    filepath = storage_path + path

    logging.info ("done with storage read")
    logging.info (filepath)

    try :
        path_arr = filepath.rsplit('/', 1)
        dir_path = path_arr[0]
        os.makedirs(dir_path, exist_ok=True)

        data = base64.b64decode(encoded_data)
        f = open(filepath, 'wb')
        f.seek(offset, offset)
        f.write(data)
        f.close()

        constant.boolReturn["success"] = True
        response = make_command_response (json.dumps(constant.boolReturn), 200)
    except:
        constant.exceptionReturn["exception_type"] = "IOException"
        constant.exceptionReturn["exception_info"] = "[storage_copy] IOException"
        content =  json.dumps(constant.exceptionReturn)
        response = make_command_response (content, 404)

    return response

def create_url_helper (server_ip, server_port, api):
    url = "http://" + server_ip + ":" + str(server_port) + api
    return url


@clientService.route('/storage_size', methods=['POST'])
def storageSize():
    pathJson = request.get_json()
    path = pathJson["path"]
    storagePath = sys.argv[4]
    if not isValidPathHelper(path):
        constant.exceptionReturn["exception_type"] = "IllegalArgumentException"
        constant.exceptionReturn["exception_info"] = "[storage_size] given path is invalid"
        content =  json.dumps(constant.exceptionReturn)
        response = make_client_response(content, 404)
        return response

    filepath = storagePath + path
    if not os.path.isfile(filepath) or os.path.isdir(filepath):
        constant.exceptionReturn["exception_type"] = "FileNotFoundException"
        constant.exceptionReturn["exception_info"] = "[storage_size] given path is absent or a directory"
        content =  json.dumps(constant.exceptionReturn)
        response = make_client_response(content, 404)
        return response

    filepath = storagePath + path
    content = {"size" : os.path.getsize(filepath)}
    response = make_client_response(json.dumps(content), 200);
    return response


@clientService.route('/storage_read', methods=['POST'])
def storageRead():
    pathJson = request.get_json()
    path = pathJson["path"]
    offset = pathJson["offset"]
    length = pathJson["length"]

    storagePath = sys.argv[4]
    if not isValidPathHelper(path):
        constant.exceptionReturn["exception_type"] = "IllegalArgumentException"
        constant.exceptionReturn["exception_info"] = "[storage_read] given path is invalid"
        content =  json.dumps(constant.exceptionReturn)
        response = make_client_response(content, 404)
        return response

    filepath = storagePath + path
    if not os.path.isfile(filepath) or os.path.isdir(filepath):
        constant.exceptionReturn["exception_type"] = "FileNotFoundException"
        constant.exceptionReturn["exception_info"] = "[storage_read] given path is absent or a directory"
        content =  json.dumps(constant.exceptionReturn)
        response = make_client_response(content, 404)
        return response

    filesize = os.path.getsize(filepath)
    if offset < 0 or length < 0 or  length > filesize or (filesize != 0 and offset >= filesize):
        constant.exceptionReturn["exception_type"] = "IndexOutOfBoundsException"
        constant.exceptionReturn["exception_info"] = "[storage_read] Negative offset/length | Length exceeded filesize"
        content =  json.dumps(constant.exceptionReturn)
        response = make_client_response(content, 404)
        return response

    try :
        f = open(filepath,"rb")
        f.seek(offset, 0)
        # allow_length = min(length, os.path.getsize(filepath))
        data = f.read(length)
        f.close()

        encoded_data = base64.b64encode(data).decode('ascii')
        content = {"data" : encoded_data}
        response = make_client_response(json.dumps(content), 200)
    except:
        constant.exceptionReturn["exception_type"] = "IOException"
        constant.exceptionReturn["exception_info"] = "[storage_read] IOException"
        content =  json.dumps(constant.exceptionReturn)
        response = make_client_response(content, 404)

    return response



@clientService.route('/storage_write', methods=['POST'])
def storageWrite():
    pathJson = request.get_json()
    path = pathJson["path"]
    offset = pathJson["offset"]
    encoded_data = pathJson["data"]

    storagePath = sys.argv[4]
    if not isValidPathHelper(path):
        constant.exceptionReturn["exception_type"] = "IllegalArgumentException"
        constant.exceptionReturn["exception_info"] = "[storage_write] given path is invalid"
        content =  json.dumps(constant.exceptionReturn)
        response = make_client_response(content, 404)
        return response

    filepath = storagePath + path
    if not os.path.isfile(filepath) or os.path.isdir(filepath):
        constant.exceptionReturn["exception_type"] = "FileNotFoundException"
        constant.exceptionReturn["exception_info"] = "[storage_write] given path is absent or a directory"
        content =  json.dumps(constant.exceptionReturn)
        response = make_client_response(content, 404)
        return response

    if offset < 0 :
        constant.exceptionReturn["exception_type"] = "IndexOutOfBoundsException"
        constant.exceptionReturn["exception_info"] = "[storage_write] Negative offset"
        content =  json.dumps(constant.exceptionReturn)
        response = make_client_response(content, 404)
        return response


    try :
        data = base64.b64decode(encoded_data)
        f = open(filepath,"wb")
        f.seek(offset, 0)
        f.write(data)
        f.close()

        constant.boolReturn["success"] = True
        response = make_client_response(json.dumps(constant.boolReturn), 200)
    except:
        constant.exceptionReturn["exception_type"] = "IOException"
        constant.exceptionReturn["exception_info"] = "[storage_read] IOException"
        content =  json.dumps(constant.exceptionReturn)
        response = make_client_response(content, 404)

    return response



if __name__ == "__main__":
    logging.basicConfig(filename='example.log',level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    logging.info("check info")
    logging.error("check error")
    logging.debug("check debug")
    Thread(target=startClientService).start()
    startCommandService()
