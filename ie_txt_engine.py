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
            verbs.append(word)

        elif token.pos_ == "NOUN":
            if k.check_explicit_change_in_kitchenware(token, word, sen, sen_i):
                print("kitchenware explicitly to: ", k.cur_kitchenware)

            if token.dep_ == "compound" and sen_i + 1 < len(sen):
                compound_word = word + "_" + sen[sen_i + 1].lemma_.lower()
                handle_potential_food(compound_word, track_concepts, c, k.cur_kitchenware)

            handle_potential_food(word, track_concepts, c, k.cur_kitchenware)

        sen_i += 1


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

            kitchenware.pre_parse_sentence_to_find_kitchenware(sentence)
            print("Kitchenware before analyzing sentence: ", kitchenware.cur_kitchenware, "\n")

            analyze_sentence(sentence, contains, kitchenware, container_used_to, track_concepts, verbs)

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
    tmp_prep = []

    i = 1
    for recipe in recipe_rows:
        print("\n: Recipe ", i, ": ", recipe[db.RecipeI.PREPARATION])
        parse_recipe(recipe[db.RecipeI.PREPARATION], nlp, contains_edge, kitchenware_tracker, container_used_for,
                     food_cooked_by, track_concept_net_results)
        tmp_prep.append(recipe[db.RecipeI.PREPARATION])

        if i == 3:
            break
        i += 1

    print("\n\nconceptNet stored: ")
    counter = 0
    for elem in track_concept_net_results.noun_to_concepts:
        if len(track_concept_net_results.noun_to_concepts[elem]) > 0:
            counter += 1
        print(elem, track_concept_net_results.noun_to_concepts[elem])
    print("counter: ", counter)

    for recipe in tmp_prep:
        print("\n\n", recipe)

    print("\n\ncontains:")
    for elem in contains_edge.contains:
        print(elem, contains_edge.contains[elem])

    print("\n\ncontainer used for:")
    for elem in container_used_for.to_verbs_dic:
        print(elem, container_used_for.to_verbs_dic[elem])

    print("\n\nfoods cooked by:")
    for elem in food_cooked_by.to_verbs_dic:
        print(elem, food_cooked_by.to_verbs_dic[elem])
    print(len(food_cooked_by.to_verbs_dic))

    contains_edge.analyze_and_convert_data()
    w_csv.write_to_csv(list(contains_edge.csv_data[0].keys()), contains_edge.csv_data, "knowledge_base/contains.csv")

    container_used_for.analyze_and_convert_data("Container")
    w_csv.write_to_csv(list(container_used_for.csv_data[0].keys()), container_used_for.csv_data,
                       "knowledge_base/container_used_for.csv")

    food_cooked_by.analyze_and_convert_data("Food")
    w_csv.write_to_csv(list(food_cooked_by.csv_data[0].keys()), food_cooked_by.csv_data,
                       "knowledge_base/food_cooked_by.csv")
