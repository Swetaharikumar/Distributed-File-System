from flask import Flask, request, jsonify
from threading import Thread
import json
import sys
import requests
import consts as constant
import glob
import os


clientService = Flask('clientServer')  # Creating the client servcie web server
commandService = Flask('commandServer')  # Creating the command web server

# storagePath =

def startClientService():
    print("Starting client service")
    clientService.run(host='localhost', port=sys.argv[1])

def startCommandService():
    print("Starting command service")
    print(glob.glob(str(sys.argv[4])))
    register()
    commandService.run(host='localhost', port=sys.argv[2])


# call naming server's register api
def register ():
    constant.namingServerPort = sys.argv[3]


    url = constant.namingServerUrl + constant.namingServerPort + constant.namingServerRegister
    data = {"storage_ip": constant.myip,
            "client_port": sys.argv[1],
            "command_port" : sys.argv[2],
            "files" : get_file_paths(sys.argv[4])}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url=url, data=json.dumps(data), headers=headers)
    print("response from naming server: ", r.json())

def get_file_paths(path):
    file_paths = []
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            file_paths.append(os.path.join(root, name)[len(path):])
        # for name in dirs:
        #     file_paths.append(os.path.join(root, name)[len(path):])
    return file_paths


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


@commandService.route('/storage_delete', methods=['POST'])
def storageDelete():
    pathJson = request.get_json()
    path = pathJson["path"]





if __name__ == "__main__":
    Thread(target=startClientService).start()
    startCommandService()
