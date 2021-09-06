import os
import sys
import heapq

import networkx as nx

from numpy.random import randint, seed

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.link import TCLink

def int_to_mac(macint):
    if type(macint) != int:
        raise ValueError('invalid integer')
    return ':'.join(['{}{}'.format(a, b)
                     for a, b
                     in zip(*[iter('{:012x}'.format(macint))]*2)])

class NSFNet(Topo):
    def build(self):
        self.G = nx.read_gml("src/topologies/gml/nsfnet.gml")
        self.switch = []
        self.host = []
        self.host_ip_map = {}
        
        self.ran = []
        self.ext = []
        for i, node in enumerate(self.G.nodes):
            switch_name = f's{i + 1}'
            self.switch.append(self.addSwitch(switch_name))

            if self.G.nodes[node]['type'] == 'user':
                self.ran.append(self.switch[-1])
            elif self.G.nodes[node]['type'] == 'server':
                self.ext.append(self.switch[-1])
            
        self.number_of_users = int(self.G.number_of_nodes() * 0.3) * 5

        for i in range(1, self.number_of_users + 1):
            host_name = 'h%d' % (i)
            host_ip = '10.0.0.%d' % (i)
            host_mac = int_to_mac(i)
            self.host.append(self.simpleCreateHost(host_name, host_ip, host_mac))

        self.server = self.simpleCreateHost('ext254', '10.0.0.254', '00:04:00:00:02:54')

        self.create_links()

    def linkSwitchToHost(self, host, switch, portHost, portSwitch, degradation):
        self.addLink(host, switch, portHost, portSwitch, **degradation)

    def linkSwitchToSwitch(self, sA, sB, degradation):
        self.addLink(sA, sB, **degradation)
    
    def simpleCreateHost(self, hostName, hostIp, hostMac):
        self.host_ip_map[hostName] = hostIp
        return self.addHost(hostName, ip=hostIp, mac=hostMac)

    def create_links(self):
        seed(1337)

        linkNoDeg = dict()
        links20Mbps = [
            dict(bw=20, delay='1ms'),
            dict(bw=20, delay='4ms'),
            dict(bw=20, delay='5ms'),
            dict(bw=20, delay='6ms'),
            dict(bw=20, delay='7ms'),
            dict(bw=20, delay='8ms'),
            dict(bw=20, delay='9ms'),
            dict(bw=20, delay='10ms'),
            dict(bw=20, delay='11ms'),
            dict(bw=20, delay='15ms')
        ]
        links200Mbps = [
            dict(bw=200, delay='1ms'),
            dict(bw=200, delay='12ms'),
            dict(bw=200, delay='15ms'),
            dict(bw=200, delay='18ms'),
            dict(bw=200, delay='20ms'),
            dict(bw=200, delay='23ms'),
            dict(bw=200, delay='25ms'),
            dict(bw=200, delay='30ms')
        ]

        # UE / Access
        for uid in range(self.number_of_users):
            sw = self.ran[uid // 5]
            port_sw = uid % 5 + 1
            self.linkSwitchToHost(self.host[uid], sw, 0, port_sw, linkNoDeg)

        # Internet
        self.linkSwitchToHost(self.server, self.ext[0], 1, 99, links200Mbps[-1])

        # Core
        coreLinkDeg = {e:links20Mbps[randint(0, len(links20Mbps))] for e in self.G.edges}
        for e in self.G.edges(self.ext):
            coreLinkDeg[e] = links200Mbps[randint(0, len(links200Mbps))]
        for e in self.G.edges:
            self.linkSwitchToSwitch(self.switch[int(e[0])], self.switch[int(e[1])], coreLinkDeg[e])

        
