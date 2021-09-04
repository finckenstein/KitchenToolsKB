from utility.track_kitchenware.kitchenware import Kitchenware
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
    def __init__(self, kitchenware_from_db):
        self.kitchenware = Kitchenware(kitchenware_from_db)
        self.contains = {}

        for key in synonymous_kitchenware:
            self.contains[key] = {}
        print(self.contains)

        self.all_data = []

    def append_data(self, concept_food, word):
        if self.kitchenware.cur_kitchenware is None:
            return
        for dic in self.contains[self.kitchenware.cur_kitchenware]:
            for concept_key in dic:
                if concept_key == concept_food:
                    self.append_new_food_to_existing_concept(concept_key, word)
                    return

        print("[append_data] for kitchenware: ", self.kitchenware.cur_kitchenware,
              " created new concept key: ", concept_food, " and added new word: ", word)
        self.contains[self.kitchenware.cur_kitchenware][concept_food] = [(word, 1)]

    def append_new_food_to_existing_concept(self, concept_key, word):
        if self.kitchenware.cur_kitchenware is not None:
            print("[append_new_food_to_existing_concept] for kitchenware: ", self.kitchenware.cur_kitchenware,
                  " appended: ", word, " to existing concept: ", concept_key)
            self.contains[self.kitchenware.cur_kitchenware][concept_key].append(word, 1)

    def is_word_stored(self, word):
        for kitchenware in self.contains:
            for concept_key in self.contains[kitchenware]:
                index = 0
                for food_tuple in self.contains[kitchenware][concept_key]:
                    if food_tuple[0] == word:
                        self.increment_occurrence_of_word(kitchenware, concept_key, index, word)
                        print("[is_word_stored] for kitchenware: ", kitchenware,
                              " incremented occurrence of word: ", word, " to: ",
                              self.contains[kitchenware][concept_key][index][1])
                        return True
                    index += 1
        return False

    def increment_occurrence_of_word(self, kitchenware, concept_key, index, word):
        counter = self.contains[kitchenware][concept_key][index][1] + 1
        self.contains[kitchenware][concept_key][index] = (word, counter)

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
