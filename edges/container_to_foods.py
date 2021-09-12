from utility.partition_tools import synonymous_kitchenware
from edges.to_verbs import get_top_5


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


class ContainerToFoods:
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
            sorted_foods = dict(sorted(foods.items(), key=lambda item: item[1]['Counter'], reverse=True))

            concepts = get_concepts(self.contains[kitchenware])
            sorted_concepts = dict(sorted(concepts.items(), key=lambda item: item[1]['Counter'], reverse=True))
            self.csv_data.append({'Container': kitchenware,
                                  'Foods': sorted_foods,
                                  'Top 5 Foods': get_top_5(sorted_foods, 'Counter'),
                                  'Number of Foods Contained': get_sum(foods),
                                  'ConceptFoods': sorted_concepts,
                                  'Top 5 ConceptFoods': get_top_5(sorted_concepts, 'Counter'),
                                  'Number of ConceptFoods Contained': get_sum(concepts)})
