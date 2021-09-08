#!/usr/bin/env python3
# import nltk
# nltk.download('wordnet')
from nltk.corpus import wordnet


def get_antonyms_from_dic(verbs_dic, has_counter):
    antonyms_of_tool = {}
    for verb_key in verbs_dic:
        if has_counter:
            counter = verbs_dic[verb_key]['Counter']
        else:
            counter = verbs_dic[verb_key]
        # print(verb_key, verbs_dic[verb_key])
        if verb_key is not None:
            for syn in wordnet.synsets(verb_key):
                for l in syn.lemmas():
                    if l.antonyms():
                        antonym = l.antonyms()[0].name()
                        if antonym in antonyms_of_tool:
                            antonyms_of_tool[antonym]['Original Verb'].append(verb_key)
                            antonyms_of_tool[antonym]['Verb Counter'] += counter
                        else:
                            antonyms_of_tool[antonym] = {'Original Verb': [verb_key],
                                                         'Verb Counter': counter}
    return antonyms_of_tool
