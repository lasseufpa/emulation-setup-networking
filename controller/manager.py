import time
import os
import requests

######################################### Global Variables ###################################################

# Static Hosts
hosts = ["10.0.0.0/24"] + ["10.0.0.%d" % i for i in range(1, 256)]

# IP and ARP codes
ip_code, arp_code = 2048, 2054

# URL's
add_uri = 'http://localhost:8080/stats/flowentry/add'
del_uri = 'http://localhost:8080/stats/flowentry/delete'
mod_uri = 'http://localhost:8080/stats/flowentry/modify'

port_desc_uri = 'http://localhost:8080/stats/portdesc/'
number_of_switch = 'http://localhost:8080/stats/switches'

class Manager(object):
    def __init__(self):
        self.high_priority = 500
        self.low_priority = 0

        self.switches = {}
        
    def reset(self):
        self.switches = {}

    def manage_switch_traffic(self, type_request, switch, iface_port, delay=0, limit=0, rate=0, loss=0):
        if type_request == 'delay':
            subprocess.run(['sudo', 'tc','qdisc','change','dev',
                f's{switch}-eth{iface_port}', 'handle', '10:', 'netem', 'delay', f'{delay}ms'])
        elif type_request == 'rate':
            subprocess.run(['sudo', 'tc','qdisc','replace','dev',
                f's{switch}-eth{iface_port}', 'root', 'netem', 'delay', 
                f'{delay}ms', 'rate', f'{rate}','limit', f'{limit}'])
        elif type_request == 'loss':
            subprocess.run(['sudo', 'tc','qdisc','change','dev',
                f's{switch}-eth{iface_port}', 'handle', '10:', 'netem', 'loss', f'{loss}'])
            
    def change_switch_route(self, switch, portOut, portIn, hostOrigin, hostDestiny):
        if switch not in self.switches:
            self.clean_all_flow_entry(del_uri, switch, 1, self.high_priority)
            self.clean_all_flow_entry(del_uri, switch, 2, self.high_priority)

            self.change_table_entry(add_uri, switch, 0, self.high_priority, hosts[0], ip_code, 1)
            self.change_table_entry(add_uri, switch, 0, self.high_priority, hosts[0], arp_code, 2)

            self.switches[switch] = True

        self.add_flow_entry(add_uri, switch, 1, self.high_priority, portIn, hosts[hostDestiny], ip_code, out_port=portOut)
        self.add_flow_entry(add_uri, switch, 2, self.low_priority, portIn, hosts[hostDestiny], arp_code, out_port=portOut)

    def change_table_entry(self, url, switch_id, table_id, priority, host, net_code, go_to_table_id):
        if net_code == 2048:
            change_table = {
                    "dpid": switch_id,
                    "table_id": table_id,
                    "priority": priority,
                    "flags": 1,
                    "match": {
                        "ipv4_dst": host,
                        "eth_type": net_code,

                    },
                    "actions": [
                        {
                            "type": "GOTO_TABLE",
                            "table_id": go_to_table_id
                        }
                    ]
            }
        else:
            change_table = {
                    "dpid": switch_id,
                    "table_id": table_id,
                    "priority": priority,
                    "flags": 1,
                    "match": {
                        "arp_tpa": host,
                        "eth_type": net_code,

                    },
                    "actions": [
                        {
                            "type": "GOTO_TABLE",
                            "table_id": go_to_table_id
                        }
                    ]
            }

        r = requests.post(url=url, json=change_table)
        return r

    def add_flow_entry(self, url, switch_id, table_id, priority, in_port, host, net_code, out_port):
        ip_type = "ipv4_dst"
        if net_code == 2054:
            ip_type = "arp_tpa"

        adding_flow = {
                "dpid": switch_id,
                "table_id": table_id,
                "priority": priority,
                "flags": 1,
                "match": {
                    "in_port": in_port,
                    ip_type: host,
                    "eth_type": net_code,

                },
                "actions": [
                    {
                        "type": "OUTPUT",
                        "port": out_port
                    }
                ]
        }

        r = requests.post(url=url, json=adding_flow)
        return r

    def clean_all_flow_entry(self, url, switch_id, table_id, priority):
        clean_flows = {"dpid": switch_id,
            "table_id": table_id, "priority": priority, "flags": 1}
        r = requests.post(url=url, json=clean_flows)
        return r
