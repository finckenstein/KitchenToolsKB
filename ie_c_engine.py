#!/usr/bin/env python3
import database_query as db
import spacy
import ast
import csv
import utility.apis.concept_net_api as concept_net
from edges.contains import Contains


def write_to_csv(data):
    fields = ['Container', 'Concepts in Kitchenware', 'Top 3 concepts', 'Number of Unique Concepts',
              'Foods in Kitchenware', 'Top 3 Foods', 'Number of Unique Foods', 'Total Number of Food and Concepts',
              'Raw Data Collected']
    filename = "contains.csv"
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)


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
