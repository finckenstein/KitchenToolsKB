import utility.apis.word_net_api as word_net


def get_top_5(sorted_v, score_to_use):
    if len(sorted_v) == 0:
        return

    if score_to_use == 'Counter':
        assert sorted_v == dict(sorted(sorted_v.items(), key=lambda item: item[1]['Counter'], reverse=True))
        maxi = list(sorted_v.values())[0]['Counter']
    else:
        assert sorted_v == dict(sorted(sorted_v.items(), key=lambda item: item[1], reverse=True))
        maxi = max(sorted_v.values())

    counter = 0
    top_5_dict = {}

    for elem in sorted_v:
        if score_to_use == 'Counter':
            score = sorted_v[elem]['Counter']
        else:
            score = sorted_v[elem]

        if maxi != score:
            counter += 1
            maxi = sorted_v[elem]

        if counter == 5:
            break
        else:
            top_5_dict[elem] = sorted_v[elem]
    return top_5_dict


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
            sorted_verbs = dict(sorted(verbs.items(), key=lambda item: item[1], reverse=True))
            top_5_verbs = get_top_5(sorted_verbs, '')
            print("\n\n Top 5 verbs: ", top_5_verbs)
            self.csv_data.append({util_or_container: tool,
                                  "Verbs": sorted_verbs,
                                  "Top 5 Verbs": top_5_verbs,
                                  "Antonyms": word_net.get_antonyms_from_dic(verbs, False),
                                  "Top 5 Antonyms": word_net.get_antonyms_from_dic(top_5_verbs, False)})



