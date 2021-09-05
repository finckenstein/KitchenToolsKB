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


class TrackConceptsFound:
    def __init__(self):
        self.noun_to_concepts = {}
        self.concepts_in_sentence = []
        self.foods_in_sentence = []

    def get_concepts_for_noun(self, noun):
        if noun in self.noun_to_concepts:
            return self.noun_to_concepts[noun]
        else:
            return None

    def update_tracking(self, noun, concepts):
        self.noun_to_concepts[noun] = concepts

    def append_food_concepts_to_sentence(self, concepts):
        for concept in concepts:
            self.concepts_in_sentence.append(concept)

    def append_food_to_sentence(self, food):
        self.foods_in_sentence.append(food)

