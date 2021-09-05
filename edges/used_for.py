import utility.apis.word_net_api as word_net
from edges.contains import get_top_three


class UsedFor:
    def __init__(self):
        self.tool_to_verbs_dic = {}
        self.all_data = []
    #     {Container or Util: [Verb]}

    def append_single_verb(self, verb, key):
        if key not in self.tool_to_verbs_dic:
            self.tool_to_verbs_dic[key] = [(verb, 1)]
            return

        index = 0
        for verb_tuple in self.tool_to_verbs_dic[key]:
            if verb == verb_tuple[0]:
                occurrence_counter = verb_tuple[1] + 1
                self.tool_to_verbs_dic[key][index] = (verb, occurrence_counter)
                return
            index += 1

        self.tool_to_verbs_dic[key].append((verb, 1))

    def analyze_and_convert_data(self, util_or_container):
        for tool in self.tool_to_verbs_dic:
            self.all_data.append({util_or_container: tool,
                                  "Verbs": self.tool_to_verbs_dic[tool],
                                  "Top 3 Verbs": get_top_three(self.tool_to_verbs_dic[tool]),
                                  "Antonyms": word_net.get_antonyms(self.tool_to_verbs_dic[tool])})



