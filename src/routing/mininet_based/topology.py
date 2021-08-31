import networkx
import requests
import json

import matplotlib.pyplot as plt

class Topology(object):
    def __init__(self, topo, *args, **kwargs):
        super(Topology, self).__init__(*args, **kwargs)
        self.topo = topo

        self.graph = networkx.DiGraph()
        self.discover_nodes()
        self.discover_edges()
    
    def discover_nodes(self):
        for switch in self.topo.switches():
            self.graph.add_node(switch)
        for host in self.topo.hosts():
            self.graph.add_node(host)

    def discover_edges(self):
        for u, v in self.topo.links():
            stats = self.topo.linkInfo(u, v)
            link_pr = {}
            if 'bw' in stats:
                link_pr['bw'] = stats['bw']
            if 'delay' in stats:
                link_pr['delay'] = stats['delay']

            self.graph.add_edge(u, v, port=stats['port1'], **link_pr) 
            self.graph.add_edge(v, u, port=stats['port2'], **link_pr)
    
    def get_hosts(self):
        return self.topo.hosts()

    def view(self):
        plt.plot()
        plt.tight_layout()
        networkx.draw(self.graph, with_labels=True, font_weight='bold', font_size=7)
        plt.show()

if __name__ == '__main__':
    pass
