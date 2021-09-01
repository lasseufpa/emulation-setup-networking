import requests
import networkx
import re

from src.routing.mininet_based.topology import Topology

class NameTrans(object):
    def __init__(self, *args, **kwargs):
        super(NameTrans, self).__init__(*args, **kwargs)
    
    def name_to_id(self, name):
        return int(re.sub("\D", "", name))

class BaseRouter(Topology, NameTrans):
    def __init__(self, *args, **kwargs):
        super(BaseRouter, self).__init__(*args, **kwargs)

    def reset(self):
        uri = 'http://127.0.0.1:5000/reset'
        requests.post(uri, json={})
        
    def install_path(self, path):
        if len(path) < 3:
            return False

        #print(path)

        uri = 'http://127.0.0.1:5000/route'
        data = {
            "switchId": 0,
            "portIn": 0,
            "portOut": 0,
            "hostOrigin": 0,
            "hostDestiny": 0
        }

        data['hostOrigin'] = self.name_to_id(path[0])
        data['hostDestiny'] = self.name_to_id(path[-1])

        for i in range(1, len(path) - 1):
            u, k, v = path[i - 1], path[i], path[i + 1]

            data['switchId'] = self.name_to_id(k)
            data['portIn'] = self.graph[k][u]['port']
            data['portOut'] = self.graph[k][v]['port']  

            requests.post(uri, json=data)

        return True

    def update_weights(self):
        pass

    def route(self):
        pass

class StaticRouter(BaseRouter):
    def __init__(self, *args, **kwargs):
        super(StaticRouter, self).__init__(*args, **kwargs)
        
    def update_weights(self, mode='unit'):
        for u, v in self.graph.edges():
            if mode == 'unit':
                w = 1
            else:
                w = self.graph[u][v][mode]
            self.graph[u][v]['w'] = w 
    
    def route(self, mode='unit', src=None, dst=None):
        self.update_weights(mode)
        if src == None:
            src = self.get_hosts()
        if dst == None:
            dst = self.get_hosts()
        
        installed = {u:{} for u in src + dst}

        for i in range(len(src)):
            paths = networkx.single_source_dijkstra_path(self.graph, src[i], weight='w')
            for j in range(len(dst)):
                if dst[j] not in installed[src[i]]:
                    self.install_path(paths[dst[j]])
                    installed[src[i]][dst[j]] = 1
                if src[i] not in installed[dst[j]]:
                    self.install_path(list(reversed(paths[dst[j]])))
                    installed[dst[j]][src[i]] = 1
                
if __name__ == '__main__':
    router = StaticRouter()
    router.route()