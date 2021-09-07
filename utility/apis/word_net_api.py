#!/usr/bin/env python3
# import nltk
# nltk.download('wordnet')
from nltk.corpus import wordnet


def tuple_stored(a, s, a_list):
    for triple in a_list:
        if triple[0] == a and s == triple[1]:
            return True
    return False


def get_antonyms(verbs):
    antonyms_of_tool = []
    for verb_tuple in verbs:
        if verb_tuple[0] is None:
            antonyms_of_tool.append(None)
        else:
            for syn in wordnet.synsets(verb_tuple[0]):
                for l in syn.lemmas():
                    if l.antonyms():
                        antonym = l.antonyms()[0].name()
                        if not tuple_stored(antonym, verb_tuple[0], antonyms_of_tool):
                            antonyms_of_tool.append((l.antonyms()[0].name(), verb_tuple[0], verb_tuple[1]))
    return antonyms_of_tool


def antonyms_of_top_three(verbs):
    antonyms_of_tool = []
    for verb_tuple in verbs:
        if verb_tuple[0] is None:
            antonyms_of_tool.append(None)
        else:
            for syn in wordnet.synsets(verb_tuple[0]):
                for l in syn.lemmas():
                    if l.antonyms():
                        antonym = l.antonyms()[0].name()
                        antonyms_of_tool.append(antonym)
    return antonyms_of_tool


def get_antonyms_from_dic(verbs_dic):
    antonyms_of_tool = []
    for verb_key in verbs_dic:
        for syn in wordnet.synsets(verb_key):
            for l in syn.lemmas():
                if l.antonyms():
                    antonym = l.antonyms()[0].name()
                    if not tuple_stored(antonym, verb_key, antonyms_of_tool):
                        antonyms_of_tool.append((antonym, verb_key, verbs_dic[verb_key]))
    return antonyms_of_tool
