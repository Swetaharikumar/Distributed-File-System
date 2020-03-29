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

clientService = Flask('clientServer')  # Creating the client servcie web server
commandService = Flask('commandServer')  # Creating the command web server

# storagePath = None

def startClientService():
    logging.info("Starting client service")
    clientService.run(host='localhost', port=sys.argv[1])

def startCommandService():
    logging.info("Starting command service")
    register()
    prune (sys.argv[4])
    commandService.run(host='localhost', port=sys.argv[2])


# call naming server's register api
def register ():
    constant.namingServerPort = sys.argv[3]
    storagePath = sys.argv[4]

    url = constant.namingServerUrl + constant.namingServerPort + constant.namingServerRegister
    data = {"storage_ip": constant.myip,
            "client_port": sys.argv[1],
            "command_port" : sys.argv[2],
            "files" : get_file_paths(storagePath)}

    headers = {'Content-type': 'application/json'}
    r = requests.post(url=url, data=json.dumps(data), headers=headers)
    res = r.json()

    remove_files (res['files'], storagePath)


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
                logging.info(prune_path)
                # os.rmdir(name)
                shutil.rmtree(prune_path)
            # file_paths.append(os.path.join(root, name))



def remove_files(filepaths, storagePath):
    for fp in filepaths:
        path = storagePath + fp
        if os.path.isfile(path):
            logging.info(path)
            os.remove(path)
        elif os.path.isdir(path):
            logging.info(path)
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
