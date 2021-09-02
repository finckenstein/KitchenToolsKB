#!/usr/bin/env python3
import database_query as db
import spacy
import ast
from contains_edge.kitchenware import Kitchenware


class Contains:
    def __init__(self, kitchenware_from_db):
        self.kitchenware = Kitchenware(kitchenware_from_db)
        self.contains_dic = {}


def is_verb_or_pronoun(token):
    return token.pos_ == "VERB" or token.pos_ == "PRON"


def is_noun(token):
    return token.pos_ == "NOUN"


def analyze_sentence(sen, c):
    sentence_i = 0
    while sentence_i < len(sen):
        token = sen[sentence_i]
        word = sen[sentence_i].lemma_.lower()

        if is_verb_or_pronoun(token):
            if c.kitchenware.check_verb_to_verify_implied_kitchenware(word):
                print(word, " changed kitchenware implicitly to: ", c.kitchenware.cur_kitchenware)
        elif is_noun(token):
            if c.kitchenware.check_explicit_change_in_kitchenware(token, word, sen, sentence_i):
                print(word, " changed kitchenware explicitly to: ", c.kitchenware.cur_kitchenware)

        sentence_i += 1


def parse_recipe(rec, nlp, contains):
    dictionary = ast.literal_eval(rec)
    for key in dictionary:
        step = nlp(dictionary[key])
        sentences = list(step.sents)

        for sentence in sentences:
            print("\n\n", sentence)
            if contains.kitchenware.pre_parse_sentence_to_find_kitchenware(sentence):
                print("before analyzing sentence, kitchenware is: ", contains.kitchenware.cur_kitchenware)
            else:
                print("before analyzing sentence, kitchenware did not change: ", contains.kitchenware.cur_kitchenware)

            analyze_sentence(sentence, contains)


if __name__ == '__main__':
    recipe_rows = db.sql_fetch_1to1_videos("all")
    nlp = spacy.load('en_core_web_trf')

    contains_edge = Contains(db.sql_fetch_kitchenware_db())
    for recipe in recipe_rows:
        parse_recipe(recipe[db.RecipeI.PREPARATION], nlp, contains_edge)
        break
