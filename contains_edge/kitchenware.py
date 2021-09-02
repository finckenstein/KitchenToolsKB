from database_query import KitchenwareI


class Kitchenware:
    def __init__(self, kitchenware_from_db):
        self.cur_kitchenware = None

        self.entire_kitchenware_kb = kitchenware_from_db
        self.all_kitchenware = []

        for row in self.entire_kitchenware_kb:
            for tmp_kitchenware in row[KitchenwareI.KITCHENWARE].split(", "):
                if tmp_kitchenware not in self.all_kitchenware:
                    self.all_kitchenware.append(tmp_kitchenware)

    def pre_parse_sentence_to_find_kitchenware(self, sentence):
        sen_i = 0
        did_change = False
        while sen_i < len(sentence):
            token = sentence[sen_i]
            word = sentence[sen_i].lemma_.lower()
            if token.pos_ == "NOUN":
                if self.check_explicit_change_in_kitchenware(token, word, sentence, sen_i):
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
                elif self.cur_kitchenware in list_of_kb_kitchenware:
                    return True
        return False

    def match_noun_to_kitchenware(self, noun):
        if noun in self.all_kitchenware:
            self.cur_kitchenware = noun
            return True
        return False

    def check_explicit_change_in_kitchenware(self, token, token_text, sentence, index):
        if token.dep_ == "compound":
            return self.match_noun_to_kitchenware(token_text + " " + sentence[index + 1].text.lower())
        else:
            return self.match_noun_to_kitchenware(token_text)
