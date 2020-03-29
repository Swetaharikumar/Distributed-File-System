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
    logging.error("original: ")
    logging.error(data['files'])

    logging.error ("To remove")
    logging.error(res)
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

    logging.info("Before prune")
    logging.info(file_paths)

    logging.info ("##############")
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


@commandService.route('/storage_delete', methods=['POST'])
def storageDelete():
    pathJson = request.get_json()
    path = pathJson["path"]


if __name__ == "__main__":
    logging.basicConfig(filename='example.log',level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    logging.info("check info")
    logging.error("check error")
    logging.debug("check debug")
    Thread(target=startClientService).start()
    startCommandService()
