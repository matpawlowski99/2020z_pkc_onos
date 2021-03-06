import requests
import json

class Graph(): 
    def __init__(self): 
        self.V = [] 
        self.E = []    
   
    def add_node(self, node):
        self.V.append(node)

    def add_link(self, src, dst):
        for edge in self.E:
            if edge[0] == src and edge[1] == dst:
                return
        self.E.append([src,dst])
        self.E.append([dst,src])

    def remove_link(self, src, dst):
        if [src,dst] in self.E:
            self.E.remove([src,dst])
            self.E.remove([dst,src])

    def shortest(self, src, dst): 
        dist = {}
        prev = {}
        done = {}
        for node in self.V:
            dist[node] = len(self.V)
            prev[node] = None
            done[node] = False
        dist[src] = 0   

        for cout in range(len(self.V)):
            current = None
            for node in self.V:
                if done[node] == False and (current == None or dist[node] < dist[current]):
                    current = node            
            for edge in self.E:
                if edge[0] == current and dist[edge[1]] > dist[edge[0]] + 1:
                    dist[edge[1]] = dist[edge[0]] + 1
                    prev[edge[1]] = edge[0]
            done[current] = True
   
        res = []
        current = dst
        while current != src:
            res.append(current)
            current = prev[current]
        res.append(src)
        res.reverse()
        return res

def get_links():
    url = "http://127.0.0.1:8181/onos/v1/links"
    payload = ""
    headers = {
        'Authorization': "Basic b25vczpyb2Nrcw==",
        'cache-control': "no-cache",
        'Postman-Token': "1f7f1048-a6cc-4185-adb2-02d333b05365"
        }
    response = requests.request("GET", url, data=payload, headers=headers)
    info = json.loads(response.text)

    for i in range(len(info['links'])):
        list_of_links.append(tuple((info['links'][i]['src']['device'], info['links'][i]['dst']['device'])))

    for j in range(len(list_of_hosts)):
        list_of_links.append(tuple((list_of_hosts[j][0], list_of_hosts[j][1])))

def get_hosts():
    url = "http://127.0.0.1:8181/onos/v1/hosts"
    payload = ""
    headers = {
        'Authorization': "Basic b25vczpyb2Nrcw==",
        'cache-control': "no-cache",
        'Postman-Token': "43ce1a21-dc80-4050-b1fb-e78b126fa993"
        }
    response = requests.request("GET", url, data=payload, headers=headers)
    info = json.loads(response.text)

    for i in range(len(info['hosts'])):
        list_of_hosts.append(tuple((info['hosts'][i]['id'], info['hosts'][i]['locations'][0]['elementId'], info['hosts'][i]['ipAddresses'][0])))
        dictionary_of_hosts[list_of_hosts[i][2]] = list_of_hosts[i][0]

def get_switches():
    url = "http://127.0.0.1:8181/onos/v1/devices"
    payload = ""
    headers = {
        'Authorization': "Basic b25vczpyb2Nrcw==",
        'cache-control': "no-cache",
        'Postman-Token': "5ba6b5bc-91a0-4427-aded-769a04a9d30c"
        }
    response = requests.request("GET", url, data=payload, headers=headers)
    info = json.loads(response.text)

    for i in range(len(info['devices'])):
        list_of_switches.append(info['devices'][i]['id'])

def get_monitored_intents():
    url = "http://127.0.0.1:8181/onos/v1/imr/imr/monitoredIntents"
    payload = ""
    headers = {
        'Authorization': "Basic b25vczpyb2Nrcw==",
        'cache-control': "no-cache",
        'Postman-Token': "0b2463de-8de8-41e3-a276-6b595819939d"
        }
    response = requests.request("GET", url, data=payload, headers=headers)
    info = json.loads(response.text)

    for i in range(len(info['response'][0]['intents'])):
        list_of_monitored_intents.append(tuple((info['response'][0]['intents'][i]['inElements'][0], info['response'][0]['intents'][i]['outElements'][0])))

def set_paths(path_value):
    url = "http://127.0.0.1:8181/onos/v1/imr/imr/reRouteIntents"
    properties = {
        "routingList": [{
            "paths": [{
                "path": path_value,
                "weight": 1.0
            }],
            "key": path_value[0] + path_value[-1],
            "appId": {
                "id": 184,
                "name": "org.onosproject.ifwd"
            }
        }, {
            "paths": [{
                "path": path_value[::-1],
                "weight": 1.0
            }],
            "key": path_value[-1] + path_value[0],
            "appId": {
                "id": 184,
                "name": "org.onosproject.ifwd"
            }
        }]
    }
    payload = str(json.dumps(properties))
    headers = {
        'Content-Type': "application/json",
        'Authorization': "Basic b25vczpyb2Nrcw==",
        'cache-control': "no-cache",
        'Postman-Token': "2ebf7528-7b70-4641-985d-9a8efb0a4b2f"
        }
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)

def create_network():
    _graph = Graph()

    for i in range(len(list_of_hosts)):
        _graph.add_node(list_of_hosts[i][0])
    for j in range(len(list_of_switches)):
        _graph.add_node(list_of_switches[j])

    for k in range(len(list_of_links)):
        _graph.add_link(list_of_links[k][0], list_of_links[k][1])

    return _graph

def priority_shortest_and_others(net, srcIP, dstIP):
    priority_path = net.shortest(dictionary_of_hosts[srcIP], dictionary_of_hosts[dstIP])
    print("??cie??ka priorytetowa: " + str(priority_path))
    
    set_paths(priority_path)
    print("")

    list_of_monitored_intents.remove((priority_path[0], priority_path[-1]))
    list_of_monitored_intents.remove((priority_path[-1], priority_path[0]))

    for i in range(len(priority_path)-1):
        if (i == 0 or i+1 == len(priority_path)-1):
            continue
        net.remove_link(priority_path[i], priority_path[i+1])

    for iterator in range(len(list_of_monitored_intents)):
        nonpriority_path = network.shortest(list_of_monitored_intents[iterator][0], list_of_monitored_intents[iterator][1])
        print("??cie??ka niepriorytetowa nr " + str(iterator + 1) + ": " + str(nonpriority_path))
        set_paths(nonpriority_path)
        print("")  


##########################################======GRAF======##########################################
##########################################================##########################################
##########################################=H3          H2=##########################################
##########################################=  \        /  =##########################################
##########################################=  S3--S6--S2  =##########################################
##########################################=    \/  \/    =##########################################
##########################################=    S7  S5    =##########################################
##########################################=    /\  /\    =##########################################
##########################################=  S4--S8--S1  =##########################################
##########################################=  /        \  =##########################################
##########################################=H4          H1=##########################################
##########################################================##########################################
##########################################======GRAF======##########################################

list_of_hosts = []
dictionary_of_hosts = {}
list_of_switches = []
list_of_links = []
list_of_monitored_intents = []

get_hosts()
get_switches()
get_links()
get_monitored_intents()

network = create_network()

priority_shortest_and_others(network, '10.0.0.4', '10.0.0.2')