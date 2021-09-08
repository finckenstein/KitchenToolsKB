import utility.apis.word_net_api as word_net


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

    return tmp


def get_parts_of_dict(whole_dict, food_key, score, score_name, verb_or_food):
    if score_name == 'Validity Score' or score_name == 'Reliability Score':
        return {verb_or_food: food_key,
                score_name: score,
                'Accuracy': whole_dict[food_key]['Accuracy'],
                'Counter': whole_dict[food_key]['Counter'],
                'Is CV in Sync With Text': whole_dict[food_key]['Is CV in Sync With Text'],
                'Is Tool Meant': whole_dict[food_key]['Is Tool Meant']}
    else:
        return {verb_or_food: food_key, score_name: score}


def convert_dict_structure(list_of_dicts, key_name, score_name):
    if score_name == 'Validity Score' or score_name == 'Reliability Score':
        tmp = {}
        for dic in list_of_dicts:
            tmp[dic[key_name]] = {score_name: dic[score_name], 'Accuracy': dic['Accuracy'], 'Counter': dic['Counter'],
                                  'Is CV in Sync With Text': dic['Is CV in Sync With Text'],
                                  'Is Tool Meant': dic['Is Tool Meant']}
        return tmp

    else:
        tmp = {}
        for dic in list_of_dicts:
            tmp[dic[key_name]] = dic[score_name]
        return tmp


def get_score(score_name, dict_vals):
    if score_name == 'Validity Score':
        score = (dict_vals['Is CV in Sync With Text'] / dict_vals['Counter'])
        score += dict_vals['Is Tool Meant']
        return score
    elif score_name == 'Reliability Score':
        return dict_vals['Accuracy'] + dict_vals['Counter']
    elif score_name == 'Counter':
        return dict_vals['Counter']
    else:
        return dict_vals


def initialize_empty_dict(score_name, verb_or_food):
    if score_name == 'Validity Score' or score_name == 'Reliability Score':
        return {verb_or_food: None, score_name: -1, 'Accuracy': -1, 'Counter': -1, 'Is CV in Sync With Text': -1,
                'Is Tool Meant': -1}
    else:
        return {verb_or_food: None, score_name: -1}


def get_5_most(verb_or_food_dic, score_name, verb_or_food):
    maxi = sec_maxi = third_maxi = four_maxi = fifth_maxi = initialize_empty_dict(score_name, verb_or_food)
    for verb_or_food_key in verb_or_food_dic:
        score = get_score(score_name, verb_or_food_dic[verb_or_food_key])

        if score > maxi[score_name]:
            fifth_maxi = four_maxi
            four_maxi = third_maxi
            third_maxi = sec_maxi
            sec_maxi = maxi
            maxi = get_parts_of_dict(verb_or_food_dic, verb_or_food_key, score, score_name, verb_or_food)
        elif score > sec_maxi[score_name]:
            fifth_maxi = four_maxi
            four_maxi = third_maxi
            third_maxi = sec_maxi
            sec_maxi = get_parts_of_dict(verb_or_food_dic, verb_or_food_key, score, score_name, verb_or_food)
        elif score > third_maxi[score_name]:
            fifth_maxi = four_maxi
            four_maxi = third_maxi
            third_maxi = get_parts_of_dict(verb_or_food_dic, verb_or_food_key, score, score_name, verb_or_food)
        elif score > four_maxi[score_name]:
            fifth_maxi = four_maxi
            four_maxi = get_parts_of_dict(verb_or_food_dic, verb_or_food_key, score, score_name, verb_or_food)
        elif score > fifth_maxi[score_name]:
            fifth_maxi = get_parts_of_dict(verb_or_food_dic, verb_or_food_key, score, score_name, verb_or_food)
    return convert_dict_structure([maxi, sec_maxi, third_maxi, four_maxi, fifth_maxi], verb_or_food, score_name)


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
            verbs = self.utensils_to[utensil]
            most_valid_verbs = get_5_most(verbs, 'Validity Score', 'Verb')
            most_reliable_verbs = get_5_most(verbs, 'Reliability Score', 'Verb')
            self.csv_data.append({'Utensil': utensil,
                                  'Verbs': verbs,
                                  'Top 5 most Valid Verbs': most_valid_verbs,
                                  'Top 5 most Reliable Verbs': most_reliable_verbs,
                                  'Antonyms': word_net.get_antonyms_from_dic(verbs, True),
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
            foods = self.utensils_to[utensil]
            concepts = get_concepts(self.utensils_to[utensil])
            self.csv_data.append({'Utensil': utensil,
                                  'Foods': foods,
                                  'Top 5 most Valid Foods': get_5_most(foods, 'Validity Score', 'Food'),
                                  'Top 5 most Reliable Foods': get_5_most(foods, 'Reliability Score', 'Food'),
                                  'ConceptFoods': concepts,
                                  'Top 5 most Valid ConceptFoods': get_5_most(concepts, 'Validity Score',
                                                                              'ConceptFoods'),
                                  'Top 5 most Reliable ConceptFoods': get_5_most(concepts, 'Reliability Score',
                                                                                 'ConceptFoods')})
