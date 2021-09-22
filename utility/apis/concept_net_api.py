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
        self.food_to_concepts = {}
        self.foods_in_sentence = {}
        self.csv_data = []

    def get_concepts_for_noun(self, noun):
        if noun in self.noun_to_concepts:
            self.noun_to_concepts[noun]['Counter'] += 1
            return self.noun_to_concepts[noun]['Concepts']
        else:
            return None

    def update_tracking(self, noun, concepts):
        assert noun not in self.noun_to_concepts, "noun should not yet be in noun_to_concepts"
        self.noun_to_concepts[noun] = {'Concepts': concepts, 'Counter': 1}

        if len(concepts) > 0:
            for concept in concepts:
                if concept in self.food_to_concepts:
                    self.food_to_concepts[concept]['Ingredient'].append(noun)
                    self.food_to_concepts[concept]['Counter'] += 1
                else:
                    self.food_to_concepts[concept] = {'Ingredient': [noun], 'Counter': 1}

    def update_concepts_in_sentence(self, noun, concepts):
        if noun not in self.foods_in_sentence:
            self.foods_in_sentence[noun] = concepts

    def analyze_and_prepare_data(self):
        sorted_concepts = dict(sorted(self.food_to_concepts.items(), key=lambda item: item[1]['Counter'], reverse=True))
        for concept in sorted_concepts:
            self.csv_data.append({'Concept': concept,
                                  'Occurrences': sorted_concepts[concept]['Counter'],
                                  'Ingredient': sorted_concepts[concept]['Ingredient']})
