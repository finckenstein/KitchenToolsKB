#!/usr/bin/env python3
import nltk
# nltk.download('wordnet')
from nltk.corpus import wordnet


if __name__ == "__main__":
    syns = wordnet.synsets("sheet")
    antonyms = []
    synonyms = []

    for syn in syns:
        print(syn.lemma_names())

    print(antonyms)