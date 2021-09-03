#!/usr/bin/env python3
import database_query as db
import spacy
import ast
import csv

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

        self.all_data = []

    def append_data(self, concept_food, word):
        if self.kitchenware.cur_kitchenware is None:
            return
        for dic in self.contains[self.kitchenware.cur_kitchenware]:
            for concept_key in dic:
                if concept_key == concept_food:
                    self.append_new_food_to_existing_concept(concept_key, word)
                    return

        print("[append_data] for kitchenware: ", self.kitchenware.cur_kitchenware,
              " created new concept key: ", concept_food, " and added new word: ", word)
        self.contains[self.kitchenware.cur_kitchenware][concept_food] = [(word, 1)]

    def append_new_food_to_existing_concept(self, concept_key, word):
        if self.kitchenware.cur_kitchenware is not None:
            print("[append_new_food_to_existing_concept] for kitchenware: ", self.kitchenware.cur_kitchenware,
                  " appended: ", word, " to existing concept: ", concept_key)
            self.contains[self.kitchenware.cur_kitchenware][concept_key].append(word, 1)

    def is_word_stored(self, word):
        for kitchenware in self.contains:
            for concept_key in self.contains[kitchenware]:
                index = 0
                for food_tuple in self.contains[kitchenware][concept_key]:
                    if food_tuple[0] == word:
                        self.increment_occurrence_of_word(kitchenware, concept_key, index, word)
                        print("[is_word_stored] for kitchenware: ", kitchenware,
                              " incremented occurrence of word: ", word, " to: ",
                              self.contains[kitchenware][concept_key][index][1])
                        return True
                    index += 1
        return False

    def increment_occurrence_of_word(self, kitchenware, concept_key, index, word):
        counter = self.contains[kitchenware][concept_key][index][1] + 1
        self.contains[kitchenware][concept_key][index] = (word, counter)

    def get_sum_food_occurrences_in_concept(self, k, c):
        summation = 0
        for food_tuple in self.contains[k][c]:
            summation += food_tuple[1]
        return summation

    def get_concepts_for(self, k):
        tmp = []
        for concepts in self.contains[k]:
            tmp.append((concepts, self.get_sum_food_occurrences_in_concept(k, concepts)))
        return tmp

    def get_foods_for(self, k):
        tmp = []
        for concepts in self.contains[k]:
            for food_tuple in self.contains[k][concepts]:
                tmp.append(food_tuple)
        return tmp

    def analyze_and_convert_data(self):
        for kitchenware in self.contains:
            concepts_in_kitchenware = self.get_concepts_for(kitchenware)
            foods_in_kitchenware = self.get_foods_for(kitchenware)

            self.all_data.append({'Container': kitchenware,
                                  'Concepts in Kitchenware': concepts_in_kitchenware,
                                  'Top 3 concepts': get_top_three(concepts_in_kitchenware),
                                  'Number of Unique Concepts': len(concepts_in_kitchenware),
                                  'Foods in Kitchenware': foods_in_kitchenware,
                                  'Top 3 Foods': get_top_three(foods_in_kitchenware),
                                  'Number of Unique Foods': len(foods_in_kitchenware),
                                  'Total Number of Food and Concepts': get_total_sum(foods_in_kitchenware),
                                  'Raw Data Collected': self.contains[kitchenware]})


def write_to_csv(data):
    fields = ['Container', 'Concepts in Kitchenware', 'Top 3 concepts', 'Number of Unique Concepts',
              'Total Number of Concept', 'Foods in Kitchenware', 'Top 3 Foods', 'Number of Unique Foods',
              'Total Number of Food and Concepts', 'Raw Data Collected']
    filename = "contains.csv"
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)


def get_total_sum(list_of_tuples):
    summation = 0
    for food_tuple in list_of_tuples:
        summation += food_tuple[1]
    return summation


def get_top_three(list_of_tuples):
    maxi = sec_maxi = third_maxi = (None, -1)
    for tmp_tuple in list_of_tuples:
        if tmp_tuple[1] > maxi[1]:
            third_maxi = sec_maxi
            sec_maxi = maxi
            maxi = tmp_tuple
        elif tmp_tuple[1] > sec_maxi[1]:
            third_maxi = sec_maxi
            sec_maxi = tmp_tuple
        elif tmp_tuple[1] > third_maxi[1]:
            third_maxi = tmp_tuple
    return [maxi, sec_maxi, third_maxi]


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

            if (token.dep_ == "compound" and sentence_i + 1 < len(sen)
                    and not c.is_word_stored(word + " " + sen[sentence_i + 1].lemma_.lower())):
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
                print("Kitchenware before analyzing sentence: ", contains.kitchenware.cur_kitchenware)
                analyze_sentence(sentence_part, contains)


if __name__ == '__main__':
    recipe_rows = db.sql_fetch_recipe_db("all")
    nlp = spacy.load('en_core_web_trf')

    contains_edge = Contains(db.sql_fetch_kitchenware_db())
    i = 1
    for recipe in recipe_rows:
        contains_edge.kitchenware.cur_kitchenware = None
        parse_recipe(recipe[db.RecipeI.PREPARATION], nlp, contains_edge)

        print("\n\n\niteration: ", i, " is over. Analyzed recipe: ", recipe[db.RecipeI.URL], ". All data so far:")
        print(contains_edge.contains)
        if i == 3:
            break
        i += 1

    print("\n\n\n")
    contains_edge.analyze_and_convert_data()
    for elem in contains_edge.all_data:
        print(elem)
    write_to_csv(contains_edge.all_data)
