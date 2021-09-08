import utility.apis.word_net_api as word_net
from edges.used_to_prepare import get_5_most


class ToVerbs:
    def __init__(self):
        self.to_verbs_dic = {}
        self.csv_data = []
    #     {Container or Util or Food: {Verb: occurrence_counter}}

    def append_single_verb(self, verb, key):
        if key is None:
            return

        if key not in self.to_verbs_dic:
            self.to_verbs_dic[key] = {}
            self.to_verbs_dic[key][verb] = 1
        elif verb not in self.to_verbs_dic[key]:
            self.to_verbs_dic[key][verb] = 1
        else:
            self.to_verbs_dic[key][verb] += 1

    def append_list_of_verbs(self, foods_in_sentence, verbs_in_sentence):
        for food in foods_in_sentence:
            if food in self.to_verbs_dic:
                for verb in verbs_in_sentence:
                    if verb in self.to_verbs_dic[food]:
                        self.to_verbs_dic[food][verb] += 1
                    else:
                        self.to_verbs_dic[food][verb] = 1
            else:
                self.to_verbs_dic[food] = {}
                for verb in verbs_in_sentence:
                    self.to_verbs_dic[food][verb] = 1

    def analyze_and_convert_data(self, util_or_container):
        for tool in self.to_verbs_dic:
            verbs = self.to_verbs_dic[tool]
            top_5_verbs = get_5_most(verbs, None, 'Verb')
            self.csv_data.append({util_or_container: tool,
                                  "Verbs": verbs,
                                  "Top 5 Verbs": top_5_verbs,
                                  "Antonyms": word_net.get_antonyms_from_dic(verbs, False),
                                  "Top 5 Antonyms": word_net.get_antonyms_from_dic(top_5_verbs, False)})



