#!/usr/bin/env python3
import spacy

nlp = spacy.load("en_core_web_trf")


if __name__ == "__main__":
    string = "While the cauliflower is baking, make the sauce: Heat the canola oil in a medium skillet over medium heat."
    step = nlp(string)
    sentences = list(step.sents)

    for sentence in sentences:
        for token in sentence:
            print(token.text, token.pos_, token.dep_)
