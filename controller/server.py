import json
import requests
import sys
import os
import time
import shlex, subprocess

from flask import Flask, jsonify, request, render_template
from flask import request

import manager

SECRET_KEY = os.urandom(32)

app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY

# Switches manager
manager = manager.Manager()

@app.route("/manage_switch_traffic", methods=["POST"]) 
def change_mininet_switch_traffic():
    req = request.json

    if req['type'] == 'delay':
        manager.manage_switch_traffic(req['type'], req['switchId'], req['ifacePort'], delay=req['value'])
    elif req['type'] == 'rate':
        manager.manage_switch_traffic(req['type'], req['switchId'], req['ifacePort'], rate=req['value'])
    elif req['type'] == 'loss':
        manager.manage_switch_traffic(req['type'], req['switchId'], req['ifacePort'], loss=req['value'])

    return req

@app.route("/route", methods=["POST"])
def change_switch_flow():
    req = request.json

    manager.change_switch_route(req['switchId'], req['portOut'], req['portIn'], req['hostOrigin'], req['hostDestiny'])
    
    return req

@app.route("/reset", methods=["POST"])
def reset():
    req = request.json
    manager.reset()
    
    return req

@app.route("/switch_info", methods=["POST"])
def switch_info():
    req = request.json

    return subprocess.check_output(
        f"sudo tc -p -s -d  qdisc show dev s{req['switch']}-eth{req['iface_port']}",
        stdin=None,
        stderr=None,
        shell=True,
        universal_newlines=False).split(b'\n')[0].decode('utf-8')

if __name__ == "__main__":
    app.run(debug=True)
