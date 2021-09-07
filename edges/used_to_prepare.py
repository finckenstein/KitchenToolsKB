import utility.apis.word_net_api as word_net


def get_top_three(dic, concept):
    maxi = sec_maxi = third_maxi = {concept: '', 'Counter': -1}
    print("\n\n", dic)
    for verb in dic:
        print("\n\n\nVerb: ", verb, "Counter: ", dic[verb], " type: ", type(dic[verb]))
        if dic[verb] > maxi['Counter']:
            third_maxi = sec_maxi
            sec_maxi = maxi
            maxi = {concept: verb, 'Counter': dic[verb]}
        elif dic[verb] > sec_maxi['Counter']:
            third_maxi = sec_maxi
            sec_maxi = {concept: verb, 'Counter': dic[verb]}
        elif dic[verb] > third_maxi['Counter']:
            third_maxi = {concept: verb, 'Counter': dic[verb]}

    return [maxi, sec_maxi, third_maxi]


def get_foods(dic):
    tmp = {}
    for key in dic:
        tmp[key] = dic[key]['Food Counter']
    return tmp


def get_concepts(dic):
    tmp = {}
    for key in dic:
        for concept in dic[key]['ConceptFoods']:
            if concept in tmp:
                tmp[concept] += 1
            else:
                tmp[concept] = dic[key]['Food Counter']

    return tmp


class Use:
    def __init__(self):
        self.utensils_to = {}
        self.utensils_in_sentence = {}
        self.csv_data = []

    def append_utensils_found(self, cv_utensil):
        print("CV UTENSILS: ", cv_utensil)
        assert len(cv_utensil) > 0, "cv_utensil should be larger than 0"

        for utensil in cv_utensil:
            if utensil in self.utensils_in_sentence:
                self.utensils_in_sentence[utensil]['CV Container Matches Txt Container'] += cv_utensil[utensil][0]
                self.utensils_in_sentence[utensil]['Overlaps'] += cv_utensil[utensil][1]
                self.utensils_in_sentence[utensil]['Accuracy'] += cv_utensil[utensil][2]
                self.utensils_in_sentence[utensil]['Counter'] += 1
            else:
                self.utensils_in_sentence[utensil] = {}
                self.utensils_in_sentence[utensil]['CV Container Matches Txt Container'] = cv_utensil[utensil][0]
                self.utensils_in_sentence[utensil]['Overlaps'] = cv_utensil[utensil][1]
                self.utensils_in_sentence[utensil]['Accuracy'] = cv_utensil[utensil][2]
                self.utensils_in_sentence[utensil]['Counter'] = 1

    def increment_counter_in_dict(self, utensil):
        self.utensils_to[utensil]['CV Container Matches Txt Container'] += self.utensils_in_sentence[utensil][
            'CV Container Matches Txt Container']
        self.utensils_to[utensil]['Overlaps'] += self.utensils_in_sentence[utensil]['Overlaps']
        self.utensils_to[utensil]['Accuracy'] += self.utensils_in_sentence[utensil]['Accuracy']
        self.utensils_to[utensil]['Counter'] += self.utensils_in_sentence[utensil]['Counter']

    def initialize_dic_for_new_utensil(self, utensil, food_or_verb):
        self.utensils_to[utensil] = {}
        self.utensils_to[utensil]['CV Container Matches Txt Container'] = self.utensils_in_sentence[utensil][
            'CV Container Matches Txt Container']
        self.utensils_to[utensil]['Overlaps'] = self.utensils_in_sentence[utensil]['Overlaps']
        self.utensils_to[utensil]['Accuracy'] = self.utensils_in_sentence[utensil]['Accuracy']
        self.utensils_to[utensil]['Counter'] = self.utensils_in_sentence[utensil]['Counter']
        self.utensils_to[utensil][food_or_verb] = {}


class UsedFor(Use):
    def __init__(self):
        super().__init__()

    def append_verbs_to_utensils(self, verbs):
        for utensil in self.utensils_in_sentence:
            if utensil in self.utensils_to:
                self.increment_counter_in_dict(utensil)
                for verb in verbs:
                    if verb in self.utensils_to[utensil]['Verbs']:
                        self.utensils_to[utensil]['Verbs'][verb] += 1
                    else:
                        self.utensils_to[utensil]['Verbs'][verb] = 1
            else:
                self.initialize_dic_for_new_utensil(utensil, 'Verbs')
                for verb in verbs:
                    self.utensils_to[utensil]['Verbs'][verb] = 1

    def analyze_verbs_and_convert_to_csv(self):
        for utensil in self.utensils_to:
            top_3_verbs = get_top_three(self.utensils_to[utensil]['Verbs'], 'Verbs')
            self.csv_data.append({'Utensil': utensil,
                                  'Accuracy': (self.utensils_to[utensil]['Accuracy']/self.utensils_to[utensil]['Counter']),
                                  'Counter': self.utensils_to[utensil]['Counter'],
                                  'CV Container Matches Txt Container': self.utensils_to[utensil]['CV Container Matches Txt Container'],
                                  'Overlaps': self.utensils_to[utensil]['Overlaps'],
                                  'Verbs': self.utensils_to[utensil]['Verbs'],
                                  'Top 3 Verbs': top_3_verbs,
                                  'Antonyms': word_net.get_antonyms_from_dic(self.utensils_to[utensil]['Verbs'])})


class UsedToPrepare(Use):
    def __init__(self):
        super().__init__()

    def append_foods_to_utensils(self, foods):
        for utensil in self.utensils_in_sentence:
            if utensil in self.utensils_to:
                self.increment_counter_in_dict(utensil)
                for food_key_in_sentence in foods:
                    if food_key_in_sentence in self.utensils_to[utensil]['Foods']:
                        self.utensils_to[utensil]['Foods'][food_key_in_sentence]['Food Counter'] += 1
                    else:
                        self.utensils_to[utensil]['Foods'][food_key_in_sentence] = {}
                        self.utensils_to[utensil]['Foods'][food_key_in_sentence]['Food Counter'] = 1
                        self.utensils_to[utensil]['Foods'][food_key_in_sentence]['ConceptFoods'] = foods[food_key_in_sentence]
            else:
                self.initialize_dic_for_new_utensil(utensil, 'Foods')
                for food_key_in_sen in foods:
                    self.utensils_to[utensil]['Foods'][food_key_in_sen] = {}
                    self.utensils_to[utensil]['Foods'][food_key_in_sen]['Food Counter'] = 1
                    self.utensils_to[utensil]['Foods'][food_key_in_sen]['ConceptFoods'] = foods[food_key_in_sen]

    def analyze_foods_and_convert_to_csv(self):
        for utensil in self.utensils_to:
            foods = get_foods(self.utensils_to[utensil]['Foods'])
            concept_foods = get_concepts(self.utensils_to[utensil]['Foods'])
            self.csv_data.append({'Utensil': utensil,
                                  'Accuracy': (self.utensils_to[utensil]['Accuracy']/self.utensils_to[utensil]['Counter']),
                                  'Counter': self.utensils_to[utensil]['Counter'],
                                  'CV Container Matches Txt Container': self.utensils_to[utensil]['CV Container Matches Txt Container'],
                                  'Overlaps': self.utensils_to[utensil]['Overlaps'],
                                  'Foods': foods,
                                  'Top 3 Foods': get_top_three(foods, 'Foods'),
                                  'ConceptFoods': concept_foods,
                                  'Top 3 Concept Foods': get_top_three(concept_foods, 'ConceptFoods')})
