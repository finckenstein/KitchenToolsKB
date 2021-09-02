#!/usr/bin/env python3
import database_query as db
import spacy
import ast
from contains_edge.kitchenware import Kitchenware
import contains_edge.concept_net_api as concept_net
from utility.partition_tools import synonymous_kitchenware


class Contains:
    def __init__(self, kitchenware_from_db):
        self.kitchenware = Kitchenware(kitchenware_from_db)
        self.contains = {}

        for key in synonymous_kitchenware:
            self.contains[key] = {}
        print(self.contains)

    def append_data(self, concept_food, word):
        for dic in self.contains[self.kitchenware.cur_kitchenware]:
            for concept_key in dic:
                if concept_key == concept_food:
                    self.append_new_food_to_existing_concept(concept_key, word)
                    return

        print("[append_data] created new concept key: ", concept_food, " and added new word: ", word)
        self.contains[self.kitchenware.cur_kitchenware][concept_food] = [(word, 0)]

    def append_new_food_to_existing_concept(self, concept_key, word):
        print("[append_new_food_to_existing_concept] appended: ", word, " to existing concept: ", concept_key)
        self.contains[self.kitchenware.cur_kitchenware][concept_key].append(word, 0)

    def is_word_stored(self, word):
        for concept_key in self.contains[self.kitchenware.cur_kitchenware]:
            index = 0
            for food_tuple in self.contains[self.kitchenware.cur_kitchenware][concept_key]:
                if food_tuple[0] == word:
                    self.increment_occurrence_of_word(concept_key, index, word)
                    print("[is_word_stored] incremented occurrence of word: ", word, " to: ",
                          self.contains[self.kitchenware.cur_kitchenware][concept_key][index][1])
                    return True
                index += 1
        return False

    def increment_occurrence_of_word(self, concept_key, index, word):
        counter = self.contains[self.kitchenware.cur_kitchenware][concept_key][index][1] + 1
        self.contains[self.kitchenware.cur_kitchenware][concept_key][index] = (word, counter)


def is_verb_or_pronoun(token):
    return token.pos_ == "VERB" or token.pos_ == "PRON"


def is_noun(token):
    return token.pos_ == "NOUN"


def append_concepts_sequentially(c, concepts, word):
    for concept in concepts:
        c.append_data(concept, word)


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

            if token.dep_ == "compound" and sentence_i + 1 < len(sen) and not c.is_word_stored(word):
                concepts = concept_net.get_concept(word + "_" + sen[sentence_i + 1].lemma_.lower())
                append_concepts_sequentially(c, concepts, word + " " + sen[sentence_i + 1].lemma_.lower())

            if not c.is_word_stored(word):
                concepts = concept_net.get_concept(word)
                append_concepts_sequentially(c, concepts, word)

        sentence_i += 1


def split_sentence_into_punctuations(s):
    sentence_parts = []
    word_array = []

    for token in s:
        if token.pos_ == "PUNCT":
            sentence_parts.append(word_array)
            word_array = []
        else:
            word_array.append(token)

    return sentence_parts


def parse_recipe(rec, nlp, contains):
    dictionary = ast.literal_eval(rec)
    for key in dictionary:
        step = nlp(dictionary[key])
        sentences = list(step.sents)

        for sentence in sentences:
            print("\n\n", sentence)
            for sentence_part in split_sentence_into_punctuations(sentence):
                contains.kitchenware.pre_parse_sentence_to_find_kitchenware(sentence_part)
                analyze_sentence(sentence_part, contains)


if __name__ == '__main__':
    recipe_rows = db.sql_fetch_recipe_db("all")
    nlp = spacy.load('en_core_web_trf')

    contains_edge = Contains(db.sql_fetch_kitchenware_db())
    for recipe in recipe_rows:
        contains_edge.kitchenware.cur_kitchenware = None
        parse_recipe(recipe[db.RecipeI.PREPARATION], nlp, contains_edge)
        print(contains_edge.contains)
        break
