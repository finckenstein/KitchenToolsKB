from utility.partition_tools import synonymous_kitchenware


def get_top_three(list_of_tuples):
    maxi = sec_maxi = third_maxi = (None, -1)
    for tmp_tuple in list_of_tuples:
        if tmp_tuple[1] > maxi[1]:
            third_maxi = sec_maxi
            sec_maxi = maxi
            maxi = tmp_tuple
        elif tmp_tuple[1] > sec_maxi[1]:
            third_maxi = sec_maxi
            sec_maxi = tmp_tuple
        elif tmp_tuple[1] > third_maxi[1]:
            third_maxi = tmp_tuple
    return [maxi, sec_maxi, third_maxi]


def get_total_sum(list_of_tuples):
    summation = 0
    for food_tuple in list_of_tuples:
        summation += food_tuple[1]
    return summation


class Contains:
    def __init__(self):
        self.contains = {}

        for key in synonymous_kitchenware:
            self.contains[key] = {}
        print(self.contains)

        self.all_data = []

    def append_concepts_sequentially(self, concepts, food, cur_kitchenware):
        for concept in concepts:
            self.append_data(concept, food, cur_kitchenware)

    def append_data(self, concept_food, word, cur_kitchenware):
        if cur_kitchenware is None:
            return

        for dic in self.contains[cur_kitchenware]:
            for concept_key in dic:
                if concept_key == concept_food:
                    self.concept_is_stored(cur_kitchenware, concept_key, word)
                    return

        self.contains[cur_kitchenware][concept_food] = [(word, 1)]

    def concept_is_stored(self, cur_kitchenware, concept_key, word):
        index = 0
        for food_tuple in self.contains[cur_kitchenware][concept_key]:
            if food_tuple[0] == word:
                food_counter = self.contains[cur_kitchenware][concept_key][index][1] + 1
                self.contains[cur_kitchenware][concept_key][index] = (word, food_counter)
                return
            index += 1

        self.contains[cur_kitchenware][concept_key].append_list_of_verbs(word, 1)

    def get_sum_food_occurrences_in_concept(self, k, c):
        summation = 0
        for food_tuple in self.contains[k][c]:
            summation += food_tuple[1]
        return summation

    def get_concepts_for(self, k):
        tmp = []
        for concepts in self.contains[k]:
            tmp.append((concepts, self.get_sum_food_occurrences_in_concept(k, concepts)))
        return tmp

    def get_foods_for(self, k):
        tmp = []
        for concepts in self.contains[k]:
            for food_tuple in self.contains[k][concepts]:
                tmp.append(food_tuple)
        return tmp

    def analyze_and_convert_data(self):
        for kitchenware in self.contains:
            concepts_in_kitchenware = self.get_concepts_for(kitchenware)
            foods_in_kitchenware = self.get_foods_for(kitchenware)

            self.all_data.append({'Container': kitchenware,
                                  'Concepts in Kitchenware': concepts_in_kitchenware,
                                  'Top 3 concepts': get_top_three(concepts_in_kitchenware),
                                  'Number of Unique Concepts': len(concepts_in_kitchenware),
                                  'Foods in Kitchenware': foods_in_kitchenware,
                                  'Top 3 Foods': get_top_three(foods_in_kitchenware),
                                  'Number of Unique Foods': len(foods_in_kitchenware),
                                  'Total Number of Food and Concepts': get_total_sum(foods_in_kitchenware),
                                  'Raw Data Collected': self.contains[kitchenware]})
