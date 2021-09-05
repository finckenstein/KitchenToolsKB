from database_query import KitchenwareI
from utility.partition_tools import synonymous_kitchenware
import utility.partition_tools as pt


def filter_out_none_kitchenware_tools_tuple(list_of_overlapping_tools):
    tmp = {}

    for quad in list_of_overlapping_tools:
        if pt.is_tool_kitchenware(quad[0]) and pt.is_tool_util(quad[2]):
            tmp[quad[0]] = quad[2]
        elif pt.is_tool_kitchenware(quad[2]) and pt.is_tool_util(quad[0]):
            tmp[quad[2]] = quad[0]

    return tmp


class Kitchenware:
    def __init__(self, kitchenware_from_db):
        self.cur_kitchenware = None
        self.entire_kitchenware_kb = kitchenware_from_db
        self.all_kitchenware = []

        for key in synonymous_kitchenware:
            self.all_kitchenware.append(key)
            for synonym in synonymous_kitchenware[key]:
                self.all_kitchenware.append(synonym)

        print(self.all_kitchenware)

    def pre_parse_sentence_to_find_kitchenware(self, sentence):
        sen_i = 0
        did_change = False
        while sen_i < len(sentence):
            token = sentence[sen_i]
            word = sentence[sen_i].lemma_.lower()
            if token.pos_ == "NOUN" and self.check_explicit_change_in_kitchenware(token, word, sentence, sen_i):
                did_change = True
            sen_i += 1
        return did_change

    def check_verb_to_verify_implied_kitchenware(self, verb):
        for kb_row in self.entire_kitchenware_kb:
            if kb_row[KitchenwareI.VERB] == verb:
                list_of_kb_kitchenware = kb_row[KitchenwareI.KITCHENWARE].split(", ")
                if self.cur_kitchenware is None or self.cur_kitchenware not in list_of_kb_kitchenware:
                    self.cur_kitchenware = kb_row[KitchenwareI.DEFAULT]
                    return True
        return False

    def match_noun_to_kitchenware(self, noun):
        if noun in self.all_kitchenware:
            self.find_synonym_of_kitchenware(noun)
            return True
        return False

    def check_explicit_change_in_kitchenware(self, token, token_text, sentence, index):
        if token.dep_ == "compound" and index + 1 < len(sentence):
            return self.match_noun_to_kitchenware(token_text + " " + sentence[index + 1].text.lower())
        else:
            return self.match_noun_to_kitchenware(token_text)

    def find_synonym_of_kitchenware(self, kitchenware):
        for key in synonymous_kitchenware:
            if key == kitchenware:
                self.cur_kitchenware = key
            else:
                for synonym in synonymous_kitchenware[key]:
                    if synonym == kitchenware:
                        self.cur_kitchenware = key
