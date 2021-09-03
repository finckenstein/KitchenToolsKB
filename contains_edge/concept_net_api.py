import requests
import time


def query_concept_net(uri):
    obj = requests.get(uri).json()
    obj.keys()
    time.sleep(1)
    return obj['edges']


def get_concept(noun):
    uri = "http://api.conceptnet.io/query?start=/c/en/" + str(noun) + "/n/wn/food&rel=/r/IsA"
    edges = query_concept_net(uri)

    tmp = []
    print("labels for word: ", noun)
    for edge in edges:
        tmp.append(edge['end']['label'])
        print(edge['end']['label'])
    return tmp
