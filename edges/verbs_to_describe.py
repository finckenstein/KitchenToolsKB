import utility.apis.word_net_api as word_net
from edges.contains import get_top_three


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


class UsedFor:
    def __init__(self):
        self.to_verbs_dic = {}
        self.all_data = []
    #     {Container or Util or Food: [(Verb, occurrence_counter)]}

    def append_single_verb(self, verb, key):
        if key is None:
            return

        if key not in self.to_verbs_dic:
            self.to_verbs_dic[key] = [(verb, 1)]
            return

        for verb_tuple in self.to_verbs_dic[key]:
            if verb == verb_tuple[0]:
                index = self.to_verbs_dic[key].index(verb_tuple)
                self.to_verbs_dic[key][index] = (verb, verb_tuple[1] + 1)
                return

        self.to_verbs_dic[key].append((verb, 1))

    def append_list_of_verbs(self, foods_in_sentence, verbs_in_sentence):
        for food in foods_in_sentence:
            if food in self.to_verbs_dic:
                for verb in verbs_in_sentence:
                    print(verb)
                    verbs_without_occurrence = get_verbs_without_occurrence(self.to_verbs_dic[food])
                    if verb in verbs_without_occurrence:
                        index = get_index(self.to_verbs_dic, food, verb)
                        verb_counter = self.to_verbs_dic[food][index][1] + 1
                        self.to_verbs_dic[food][index] = (verb, verb_counter)
                    else:
                        self.to_verbs_dic[food].append((verb, 1))
            else:
                self.to_verbs_dic[food] = []
                for v in verbs_in_sentence:
                    verbs_without_occurrence = get_verbs_without_occurrence(self.to_verbs_dic[food])
                    if v in verbs_without_occurrence:
                        index = get_index(self.to_verbs_dic, food, v)
                        verb_counter = self.to_verbs_dic[food][index][1] + 1
                        self.to_verbs_dic[food][index] = (v, verb_counter)
                    else:
                        self.to_verbs_dic[food].append((v, 1))

    def analyze_and_convert_data(self, util_or_container):
        for tool in self.to_verbs_dic:
            top_three_verbs = get_top_three(self.to_verbs_dic[tool])
            self.all_data.append({util_or_container: tool,
                                  "Verbs": self.to_verbs_dic[tool],
                                  "Top 3 Verbs": top_three_verbs,
                                  "Antonyms": word_net.get_antonyms(self.to_verbs_dic[tool]),
                                  "Antonyms of Top 3": word_net.antonyms_of_top_three(top_three_verbs)})



