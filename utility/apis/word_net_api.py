#!/usr/bin/env python3
import nltk
# nltk.download('wordnet')
from nltk.corpus import wordnet


def get_antonyms(verbs):
    antonyms_of_tool = []
    for verb_tuple in verbs:
        for syn in wordnet.synsets(verb_tuple[0]):
            for l in syn.lemmas():
                if l.antonyms():
                    antonyms_of_tool.append(l.antonyms()[0].name())
    return antonyms_of_tool
