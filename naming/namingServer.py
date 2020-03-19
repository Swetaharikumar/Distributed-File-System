import consts as constant
from flask import Flask, request, jsonify
from threading import Thread
import json
import sys


namingService = Flask('namingServer')  # Creating the Service web server


def startNamingService():
    print("Starting naming service")
    namingService.run(host='localhost', port=sys.argv[1])


def make_response(content, status_code):
    response = manager.response_class(
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


namingRegister = Flask('namingRegister')  # Creating the Registration web server


def startNamingRegister():
    print("Starting naming Registration")
    namingRegister.run(host='localhost', port=sys.argv[2])


@namingRegister.route('/register', methods = ['POST'])
def register():

    storageServerInfo = request.get_json()

    for item in constant.storageServers:
        if storageServerInfo['storage_ip'] == item['storage_ip'] and storageServerInfo['client_port'] == item['client_port'] and storageServerInfo['command_port'] == item['storage_ip']:









if __name__ == "__main__":
    Thread(target=startNamingRegister).start()
    startNamingService()






