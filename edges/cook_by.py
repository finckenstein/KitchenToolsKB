from edges.contains import get_top_three
from utility.apis.word_net_api import get_antonyms


def get_index(dic, ky, verb):
    index = 0
    for v in dic[ky]:
        if v[0] == verb:
            return index
        index += 1
    return None


def get_verbs_without_occurrence(verb_tuple):
    tmp = []
    for verb_tuple in verb_tuple:
        tmp.append(verb_tuple[0])
    return tmp


class CookBy:
    def __init__(self):
        self.food_to_verbs = {}
        # {Food or Concept: [Verbs]}
        self.all_data = []

    def append_list_of_verbs(self, foods_in_sentence, verbs_in_sentence):
        print("\n\n\n[append_list_of_verbs] foods in sentence: ", foods_in_sentence)
        print("[append_list_of_verbs] verbs in sentence: ", verbs_in_sentence)

        for food in foods_in_sentence:
            print(food)
            if food in self.food_to_verbs:
                print("food is in list")
                for verb in verbs_in_sentence:
                    print(verb)
                    verbs_without_occurrence = get_verbs_without_occurrence(self.food_to_verbs[food])
                    if verb in verbs_without_occurrence:
                        print("verb: ", verb, " is in verb list: ", self.food_to_verbs[food])
                        index = get_index(self.food_to_verbs, food, verb)
                        verb_counter = self.food_to_verbs[food][index][1] + 1
                        self.food_to_verbs[food][index] = (verb, verb_counter)
                    else:
                        print("verb: ", verb, " is not in verb list: ", self.food_to_verbs[food])
                        self.food_to_verbs[food].append((verb, 1))
            else:
                self.food_to_verbs[food] = []
                print("food is not in list")
                for v in verbs_in_sentence:
                    verbs_without_occurrence = get_verbs_without_occurrence(self.food_to_verbs[food])
                    if v in verbs_without_occurrence:
                        index = get_index(self.food_to_verbs, food, v)
                        verb_counter = self.food_to_verbs[food][index][1] + 1
                        self.food_to_verbs[food][index] = (v, verb_counter)
                    else:
                        self.food_to_verbs[food].append((v, 1))

    def analyze_and_convert_data(self, food_or_concept):
        for food in self.food_to_verbs:
            self.all_data.append({food_or_concept: food,
                                  "Verbs": self.food_to_verbs[food],
                                  "Top 3 Verbs": get_top_three(self.food_to_verbs[food]),
                                  "Antonyms": get_antonyms(self.food_to_verbs[food])})
