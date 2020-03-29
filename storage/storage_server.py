from flask import Flask, request, jsonify
from threading import Thread
import json
import sys
import requests


clientService = Flask('clientServer')  # Creating the client servcie web server
commandService = Flask('commandServer')  # Creating the command web server
namingServerUrl = "localhost:"

def startClientService():
    print("Starting client service")
    clientService.run(host='localhost', port=sys.argv[1])

def startCommandService():
    print("Starting command service")

    # call naming server's register api
    # r = requests.get(url = URL, params = PARAMS)
    # data = r.json()

    commandService.run(host='localhost', port=sys.argv[2])


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
