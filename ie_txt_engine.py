#!/usr/bin/env python3
import database_query as db
import spacy
import ast

from utility.apis import concept_net_api as concept_net
from utility.container import Container
import utility.write_to_csv as w_csv

from edges.container_to_foods import ContainerToFoods
from edges.to_verbs import ToVerbs


def handle_potential_food(noun, track_concepts, c, cur_kitchenware):
    concepts_tracked = track_concepts.get_concepts_for_noun(noun)
    if concepts_tracked is None:
        concepts = concept_net.get_concept(noun)
        track_concepts.update_tracking(noun, concepts)
        print("appended noun: ", noun, " for concept: ", concepts)
    else:
        concepts = concepts_tracked
        print("concept stored. noun: ", noun, " for concepts: ", concepts_tracked)

    if len(concepts) > 0:
        track_concepts.update_concepts_in_sentence(noun, concepts)
        c.append_food(noun, concepts, cur_kitchenware)


def analyze_sentence(sen, c, k, cuf, track_concepts, verbs):
    sen_i = 0
    while sen_i < len(sen):
        token = sen[sen_i]
        word = sen[sen_i].lemma_.lower()
        print(word)

        if token.pos_ == "VERB" and token.dep_ != "xcomp":
            cuf.append_single_verb(word, k.cur_kitchenware)
            if word not in verbs:
                verbs.append(word)

        elif token.pos_ == "NOUN":
            if k.check_explicit_change_in_kitchenware(token, word, sen, sen_i):
                print("kitchenware explicitly to: ", k.cur_kitchenware)

            if token.dep_ == "compound" and sen_i + 1 < len(sen):
                compound_word = word + " " + sen[sen_i + 1].lemma_.lower()
                handle_potential_food(compound_word, track_concepts, c, k.cur_kitchenware)

            handle_potential_food(word, track_concepts, c, k.cur_kitchenware)

        sen_i += 1


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


def parse_recipe(rec, nl, contains, kitchenware, container_used_to, fcb, track_concepts):
    dictionary = ast.literal_eval(rec)
    for key in dictionary:
        step = nl(dictionary[key])
        sentences = list(step.sents)
        kitchenware_tracker.cur_kitchenware = None

        for sentence in sentences:
            print("\n\n", sentence)
            track_concepts.foods_in_sentence = {}
            verbs = []

            for sentence_part in split_sentence_into_punctuations(sentence):
                kitchenware.pre_parse_sentence_to_find_kitchenware(sentence_part)
                print("Kitchenware before analyzing sentence: ", kitchenware.cur_kitchenware, "\n")
                analyze_sentence(sentence_part, contains, kitchenware, container_used_to, track_concepts, verbs)

            print("verbs in sentence: ", verbs)
            print("foods in sentence: ", track_concepts.foods_in_sentence)
            fcb.append_list_of_verbs(track_concepts.foods_in_sentence, verbs)


if __name__ == '__main__':
    recipe_rows = db.sql_fetch_recipe_db("all")
    nlp = spacy.load('en_core_web_trf')

    contains_edge = ContainerToFoods()
    kitchenware_tracker = Container()
    container_used_for = ToVerbs()
    food_cooked_by = ToVerbs()
    track_concept_net_results = concept_net.TrackConceptsFound()

    i = 1
    for recipe in recipe_rows:
        parse_recipe(recipe[db.RecipeI.PREPARATION], nlp, contains_edge, kitchenware_tracker, container_used_for,
                     food_cooked_by, track_concept_net_results)

        print("\n\n\niteration: ", i, " is over. Analyzed recipe: ", recipe[db.RecipeI.URL], ". All data so far:")
        print("\n\nrecipe: ", recipe[db.RecipeI.PREPARATION])
        print("contains: ", contains_edge.contains)
        print("\n\ncontainer used for: ", container_used_for.to_verbs_dic)
        print("\n\nfoods cooked by: ", food_cooked_by.to_verbs_dic)
        print("\n\nconceptNet stored: ", track_concept_net_results.noun_to_concepts)

        if i == 3:
            break
        i += 1

    contains_edge.analyze_and_convert_data()
    w_csv.write_container_to_csv(contains_edge.csv_data, "contains.csv")

    container_used_for.analyze_and_convert_data("Container")
    w_csv.write_verbs_to_describe_to_csv('Container', container_used_for.csv_data, "container_used_for.csv")

    food_cooked_by.analyze_and_convert_data("Food")
    w_csv.write_verbs_to_describe_to_csv('Food', food_cooked_by.csv_data, "food_cooked_by.csv")
