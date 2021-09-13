import utility.apis.word_net_api as word_net
from edges.to_verbs import get_top_5


def get_concepts(dic):
    tmp = {}
    for food in dic:
        concepts = dic[food]['ConceptFoods']
        for concept in concepts:
            if concept in tmp:
                tmp[concept]['Accuracy'] += dic[food]['Accuracy']
                tmp[concept]['Counter'] += dic[food]['Counter']
                tmp[concept]['Is CV in Sync With Text'] += dic[food]['Is CV in Sync With Text']
                tmp[concept]['Is Tool Meant'] += dic[food]['Is Tool Meant']
                tmp[concept]['Foods'].append(food)
            else:
                tmp[concept] = {}
                tmp[concept]['Accuracy'] = dic[food]['Accuracy']
                tmp[concept]['Counter'] = dic[food]['Counter']
                tmp[concept]['Is CV in Sync With Text'] = dic[food]['Is CV in Sync With Text']
                tmp[concept]['Is Tool Meant'] = dic[food]['Is Tool Meant']
                tmp[concept]['Foods'] = [food]

    for concept in tmp:
        acc = tmp[concept]['Accuracy']
        counter = tmp[concept]['Counter']
        tmp[concept]['Accuracy'] = acc / counter
        tmp[concept]['Reliability Score'] = tmp[concept]['Accuracy'] + tmp[concept]['Counter']
        tmp[concept]['Validity Score'] = ((tmp[concept]['Is CV in Sync With Text'] / tmp[concept]['Counter']) +
                                          tmp[concept]['Is Tool Meant'])

    return tmp


def calculate_validity_and_reliability_score(dic_of_utensil):
    tmp = {}
    for verb_or_food in dic_of_utensil:
        tmp[verb_or_food] = {'Accuracy': dic_of_utensil[verb_or_food]['Accuracy'],
                             'Is CV in Sync With Text': dic_of_utensil[verb_or_food]['Is CV in Sync With Text'],
                             'Is Tool Meant': dic_of_utensil[verb_or_food]['Is Tool Meant'],
                             'Counter': dic_of_utensil[verb_or_food]['Counter'],
                             'Reliability Score': (dic_of_utensil[verb_or_food]['Accuracy'] +
                                                   dic_of_utensil[verb_or_food]['Counter']),
                             'Validity Score': ((dic_of_utensil[verb_or_food]['Is CV in Sync With Text'] /
                                                 dic_of_utensil[verb_or_food]['Counter']) +
                                                dic_of_utensil[verb_or_food]['Is Tool Meant'])}
    return tmp


class UtensilsTo:
    def __init__(self):
        self.utensils_to = {}
        # {utensil: {Verb: {'Accuracy': 50, 'Is CV in Sync With Text': 0, 'Is Tool Meant': 0, 'Counter': 1}}}
        # {utensil: {Food: {'Accuracy': 50, 'Is CV in Sync With Text': 0, 'Is Tool Meant': 0, 'Counter': 1, ConceptFoods: []}}}
        self.utensils_in_sentence = {}
        # {utensil: {CV Container Matches Txt Container: 0, 'Overlaps': 0, 'Accuracy': 50, 'Counter': 1}}
        self.csv_data = []

    def append_utensils_found(self, cv_utensil):
        print("CV UTENSILS: ", cv_utensil)
        assert len(cv_utensil) > 0, "cv_utensil should be larger than 0"

        for utensil in cv_utensil:
            if utensil in self.utensils_in_sentence:
                self.utensils_in_sentence[utensil]['CV Container Matches Txt Container'] += cv_utensil[utensil][
                    'CV is in Sync with TXT']
                self.utensils_in_sentence[utensil]['Overlaps'] += cv_utensil[utensil]['Utensil is meant']
                self.utensils_in_sentence[utensil]['Accuracy'] += cv_utensil[utensil]['Accuracy']
                self.utensils_in_sentence[utensil]['Counter'] += 1
            else:
                self.utensils_in_sentence[utensil] = {}
                self.utensils_in_sentence[utensil]['CV Container Matches Txt Container'] = cv_utensil[utensil][
                    'CV is in Sync with TXT']
                self.utensils_in_sentence[utensil]['Overlaps'] = cv_utensil[utensil]['Utensil is meant']
                self.utensils_in_sentence[utensil]['Accuracy'] = cv_utensil[utensil]['Accuracy']
                self.utensils_in_sentence[utensil]['Counter'] = 1

    def increment_counter_in_dict(self, utensil, relation_with):
        self.utensils_to[utensil][relation_with]['Accuracy'] += self.utensils_in_sentence[utensil]['Accuracy']
        self.utensils_to[utensil][relation_with]['Counter'] += self.utensils_in_sentence[utensil]['Counter']
        self.utensils_to[utensil][relation_with]['Is CV in Sync With Text'] += \
            self.utensils_in_sentence[utensil]['CV Container Matches Txt Container']
        self.utensils_to[utensil][relation_with]['Is Tool Meant'] += self.utensils_in_sentence[utensil]['Overlaps']

    def initialize_dic_for_new_relation(self, utensil, relation_with):
        self.utensils_to[utensil][relation_with] = {}
        self.utensils_to[utensil][relation_with]['Accuracy'] = self.utensils_in_sentence[utensil]['Accuracy']
        self.utensils_to[utensil][relation_with]['Is CV in Sync With Text'] = \
            self.utensils_in_sentence[utensil]['CV Container Matches Txt Container']
        self.utensils_to[utensil][relation_with]['Is Tool Meant'] = self.utensils_in_sentence[utensil]['Overlaps']
        self.utensils_to[utensil][relation_with]['Counter'] = self.utensils_in_sentence[utensil]['Counter']

    def update_accuracy(self):
        for utensil in self.utensils_to:
            for rel in self.utensils_to[utensil]:
                accuracy = self.utensils_to[utensil][rel]['Accuracy']
                counter = self.utensils_to[utensil][rel]['Counter']
                self.utensils_to[utensil][rel]['Accuracy'] = accuracy / counter


class UtensilsToVerbs(UtensilsTo):
    def __init__(self):
        super().__init__()

    def append_verbs_to_utensils(self, verbs):
        for utensil in self.utensils_in_sentence:
            if utensil in self.utensils_to:
                for verb in verbs:
                    if verb in self.utensils_to[utensil]:
                        self.increment_counter_in_dict(utensil, verb)
                    else:
                        self.initialize_dic_for_new_relation(utensil, verb)
            else:
                self.utensils_to[utensil] = {}
                for verb in verbs:
                    self.initialize_dic_for_new_relation(utensil, verb)

    def analyze_verbs_and_convert_to_csv(self):
        self.update_accuracy()
        print("\n\n\n", self.utensils_to)
        for utensil in self.utensils_to:
            verbs = calculate_validity_and_reliability_score(self.utensils_to[utensil])
            sorted_verbs = dict(sorted(verbs.items(), key=lambda item: item[1]['Validity Score'], reverse=True))
            most_valid_verbs = get_top_5(sorted_verbs, 'Validity Score')
            most_reliable_verbs = get_top_5(sorted_verbs, 'Reliability Score')
            self.csv_data.append({'Utensil': utensil,
                                  'Verbs': sorted_verbs,
                                  'Top 5 most Valid Verbs': most_valid_verbs,
                                  'Top 5 most Reliable Verbs': most_reliable_verbs,
                                  'Antonyms': word_net.get_antonyms_from_dic(sorted_verbs, True),
                                  'Antonyms of Top 5 most Valid Verbs': word_net.get_antonyms_from_dic(
                                      most_valid_verbs, True),
                                  'Antonyms of Top 5 most Reliable Verbs': word_net.get_antonyms_from_dic(
                                      most_reliable_verbs, True)})


class UtensilsToFoods(UtensilsTo):
    def __init__(self):
        super().__init__()

    def append_foods_to_utensils(self, foods):
        for utensil in self.utensils_in_sentence:
            if utensil in self.utensils_to:
                for food_key_in_sentence in foods:
                    if food_key_in_sentence in self.utensils_to[utensil]:
                        self.increment_counter_in_dict(utensil, food_key_in_sentence)
                    else:
                        self.initialize_dic_for_new_relation(utensil, food_key_in_sentence)
                        self.utensils_to[utensil][food_key_in_sentence]['ConceptFoods'] = foods[food_key_in_sentence]
            else:
                self.utensils_to[utensil] = {}
                for food_key_in_sen in foods:
                    self.initialize_dic_for_new_relation(utensil, food_key_in_sen)
                    self.utensils_to[utensil][food_key_in_sen]['ConceptFoods'] = foods[food_key_in_sen]

    def analyze_foods_and_convert_to_csv(self):
        self.update_accuracy()
        print("\n\n\n", self.utensils_to)
        for utensil in self.utensils_to:
            foods = calculate_validity_and_reliability_score(self.utensils_to[utensil])
            sorted_foods = dict(sorted(foods.items(), key=lambda item: item[1]['Validity Score'], reverse=True))

            concepts = get_concepts(self.utensils_to[utensil])
            sorted_concepts = dict(sorted(concepts.items(), key=lambda item: item[1]['Validity Score'], reverse=True))

            self.csv_data.append({'Utensil': utensil,
                                  'Foods': sorted_foods,
                                  'Top 5 most Valid Foods': get_top_5(sorted_foods, 'Validity Score'),
                                  'Top 5 most Reliable Foods': get_top_5(sorted_foods, 'Reliability Score'),
                                  'ConceptFoods': sorted_concepts,
                                  'Top 5 most Valid ConceptFoods': get_top_5(concepts, 'Validity Score'),
                                  'Top 5 most Reliable ConceptFoods': get_top_5(concepts, 'Reliability Score')})
