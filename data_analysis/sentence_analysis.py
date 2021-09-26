#!/usr/bin/env python3
import spacy
from nltk.corpus import wordnet
nlp = spacy.load("en_core_web_trf")


if __name__ == "__main__":
    string = "Put the bread on the cutting board and cut it."
    step = nlp(string)
    sentences = list(step.sents)

    for sentence in sentences:
        for token in sentence:
            print(token.text, token.pos_, token.dep_)




