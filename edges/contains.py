from utility.partition_tools import synonymous_kitchenware
from edges.used_to_prepare import get_5_most


def get_concepts(dic):
    tmp = {}
    for food in dic:
        concepts = dic[food]['ConceptFoods']
        for concept in concepts:
            if concept in tmp:
                tmp[concept]['Foods'].append(food)
                tmp[concept]['Counter'] += dic[food]['Counter']
            else:
                tmp[concept] = {}
                tmp[concept]['Foods'] = [food]
                tmp[concept]['Counter'] = dic[food]['Counter']

    return tmp


def get_sum(dic):
    summation = 0
    for key in dic:
        summation += dic[key]['Counter']
    return summation


class Contains:
    def __init__(self):
        self.contains = {}
        # {container: {food: {'ConceptFood': [], 'Counter': 1}}}
        for key in synonymous_kitchenware:
            self.contains[key] = {}

        self.csv_data = []

    def append_food(self, food, concepts, container):
        if container is None:
            return
        assert container in self.contains, "container from txt is given illegal key"
        if food in self.contains[container]:
            self.contains[container][food]['Counter'] += 1
        else:
            self.contains[container][food] = {}
            self.contains[container][food]['ConceptFoods'] = concepts
            self.contains[container][food]['Counter'] = 1

    def analyze_and_convert_data(self):
        for kitchenware in self.contains:
            foods = self.contains[kitchenware]
            concepts = get_concepts(self.contains[kitchenware])
            self.csv_data.append({'Container': kitchenware,
                                  'Foods': foods,
                                  'Top 5 Foods': get_5_most(foods, 'Counter', 'Food'),
                                  'Number of Foods Contained': get_sum(foods),
                                  'ConceptFoods': concepts,
                                  'Top 5 ConceptFoods': get_5_most(foods, 'Counter', 'ConceptFoods'),
                                  'Number of ConceptFoods Contained': get_sum(concepts)})
