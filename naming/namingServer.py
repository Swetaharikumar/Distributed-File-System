import consts as constant
from flask import Flask, request, jsonify
from threading import Thread
import json
import sys
from FileSystemTree import File, FileSystem

namingService = Flask('namingServer')  # Creating the Service web server
namingRegister = Flask('namingRegister')  # Creating the Registration web server
fs = FileSystem()

def startNamingService():
    print("Starting naming service")
    namingService.run(host='localhost', port=sys.argv[1])

def startNamingRegister():
    print("Starting naming Registration")
    namingRegister.run(host='localhost', port=sys.argv[2])


def make_response(content, status_code):
    response = namingService.response_class(
        response=content,
        status=status_code,
        mimetype='application/json'
    )
    return response


@namingService.route('/is_valid_path', methods=['POST'])
def isValidPath():
    pathJson = request.get_json()
    path = pathJson["path"]

    constant.boolReturn["success"] = True
    # three cases where input is invalid
    if not path or ':' in path or path[0] != '/':
        constant.boolReturn["success"] = False

    content = json.dumps(constant.boolReturn)
    response = make_response(content, 200)
    return response



@namingService.route('/list', methods=['POST'])
def list():
    pathJson = request.get_json()
    path = pathJson["path"]
    if path == '//':
        path = '/'

    if not isValidPathHelper (path):
        constant.exceptionReturn["exception_type"] = "IllegalArgumentException"
        constant.exceptionReturn["exception_info"] = "given path is invalid"
        content =  json.dumps(constant.exceptionReturn)
        response = make_response(content, 404)
        return response

    node  = fs.get(path)
    if not node or node.isFile:
        constant.exceptionReturn["exception_type"] = "FileNotFoundException"
        constant.exceptionReturn["exception_info"] = "given path does not refer to a directory."
        content =  json.dumps(constant.exceptionReturn)
        response = make_response(content, 404)
        return response


    for k,v in node.map.items():
        constant.filesReturn['files'].append(v.name)

    print (constant.filesReturn['files'])
    # constant.filesReturn['files'] = list(set(constant.filesReturn['files']))
    content = json.dumps(constant.filesReturn)
    response = make_response(content, 200)
    return response


@namingService.route('/is_directory', methods=['POST'])
def isDirectory():
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
        constant.boolReturn["success"] = False
        constant.exceptionReturn["exception_type"] = "FileNotFoundException"
        constant.exceptionReturn["exception_info"] = "[is_directory] File/path cannot be found."
        content =  json.dumps(constant.exceptionReturn)
        response = make_response(content, 404)
        return response

    constant.boolReturn["success"] = not node.isFile
    content = json.dumps(constant.boolReturn)
    response = make_response(content, 200)
    return response


def isValidPathHelper (path):
    if not path or ':' in path or path[0] != '/':
        return False
    else:
        return True


def isDirectoryHelper(path):
    valid = False
    for file in constant.filesDict.keys():
        if file.startswith (path + '/') or path == '/':
            valid = True
            break
    return valid


@namingRegister.route('/register', methods = ['POST'])
def register():
    ssReq = request.get_json()
    storageServerEntry = {"storage_ip": ssReq['storage_ip'],
                          "client_port": ssReq['client_port'],
                          "command_port" : ssReq['command_port'],
                          "files" : []}

    deleteFiles = {'files' : []}

    for item in constant.storageServers:
        if ssReq['storage_ip'] == item['storage_ip'] and ssReq['client_port'] == item['client_port'] \
                and ssReq['command_port'] == item['command_port']:
            constant.exceptionReturn["exception_type"] = "IllegalStateException"
            constant.exceptionReturn["exception_info"] = "This storage client already registered."

            content =  json.dumps(constant.exceptionReturn)
            response = make_response(content, 409)
            return response

    for reqFile in ssReq['files']:
        if reqFile == '/':
            continue

        node = fs.get(reqFile)
        if node:
            deleteFiles['files'].append(reqFile)
        else:
            fs.insert(reqFile)
            storageServerEntry['files'].append(reqFile)

    # For now simple append, later look at files and send delete command for duplicates
    constant.storageServers.append(storageServerEntry)
    content = json.dumps(deleteFiles)
    response = make_response(content, 200);
    return response;



if __name__ == "__main__":
    Thread(target=startNamingRegister).start()
    startNamingService()






