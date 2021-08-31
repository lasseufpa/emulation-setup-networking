import json
import requests
import sys
import os
import time
import shlex, subprocess

from flask import Flask, jsonify, request, render_template
from flask import request

import manage_switch



SECRET_KEY = os.urandom(32)

app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY

# Change route
manager = manage_switch.changeSwitch()


@app.route("/switch_traffic_change", methods=["POST"]) 
def change_mininet_switch_traffic():
    req = request.json

    bash_cmd_output = None
    if req['type'] == 'delay':
        req['limit'], req['rate'], req['loss'] = 0,0,0
    elif req['type'] == 'rate':
        req['loss'] = 0
    elif req['type'] == 'loss':
        req['limit'], req['rate'], req['delay'] = 0,0,0
    elif req['type'] == 'list':
        req['limit'], req['rate'], req['delay'], req['loss'] = 0,0,0,0
        bash_cmd_output = subprocess.check_output(
                "sudo tc -p -s -d  qdisc show dev s{}-eth{}".format(req['switch'], req['iface_port']),
                stdin=None,
                stderr=None,
                shell=True,
                universal_newlines=False).split(b'\n')[0].decode('utf-8')

    if bash_cmd_output == None:
        bash_cmd_output = "Ok!"
        changeSwitch.manage_switch_traffic(req['switch'], req['iface_port'], req['delay'],
    req['limit'], req['rate'], req['loss'], req['type'])

    return bash_cmd_output
@app.route("/deploy", methods=["POST"])
def change_switch_flow():
    req = request.json
    manager.change_switch_route(req['switchId'], req['portOut'], req['portIn'], req['hostOrigin'], req['hostDestiny'])
    
    return req

@app.route("/reset", methods=["POST"])
def reset():
    req = request.json
    manager.reset()
    
    return req

if __name__ == "__main__":
    app.run(debug=True)
