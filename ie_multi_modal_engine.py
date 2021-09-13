#!/usr/bin/env python3
import database_query as db
import spacy
import ast
import tensorflow as tf
import os

from utility.apis import concept_net_api as concept_net
from utility.container import Container
import utility.write_to_csv as w_csv
import utility.paths as path
import utility.video_utility_functions as vid
from utility import overlapping_tools_in_frame as overlapping_tools

from computer_vision import make_inference_from_cv as inference
from computer_vision.tensorflow_object_detection_utils import ops as utils_ops
from computer_vision.tensorflow_object_detection_utils import label_map_util

from edges.utensils_to import UtensilsToFoods, UtensilsToVerbs
from utility.sync_txt_with_video import Sync


def does_current_cv_container_match_txt(txt, cv):
    assert cv is not None, "container cv should not be None"
    tmp = cv.replace("-", " ")
    if txt == tmp:
        return 1
    else:
        return 0


def get_detected_utensils(cv_dict, txt_container, sync):
    if cv_dict is None:
        return {}

    utensils = {}
    is_in_sync = sync.is_video_in_sync_with_txt(txt_container, cv_dict)
    for container in cv_dict:
        if container is None:
            for utensil in cv_dict[None]:
                assert utensil not in utensils, "utensil gotten from cv should be unique"
                utensils[utensil] = {}
                utensils[utensil]['Accuracy'] = cv_dict[None][utensil]
                utensils[utensil]['CV is in Sync with TXT'] = is_in_sync
                utensils[utensil]['Utensil is meant'] = 0
        elif len(cv_dict[container]) > 0:
            for utensil in cv_dict[container]:
                overlaps = does_current_cv_container_match_txt(txt_container, container)
                assert utensil not in utensils, "utensil gotten from cv should be unique"
                utensils[utensil] = {}
                utensils[utensil]['Accuracy'] = cv_dict[container][utensil]
                utensils[utensil]['CV is in Sync with TXT'] = is_in_sync
                utensils[utensil]['Utensil is meant'] = overlaps
    return utensils


def handle_potential_food(noun, track_concepts):
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


def analyze_sentence(sen, utp, k, uuf, track_concepts, verbs, s):
    sen_i = 0

    while sen_i < len(sen):
        token = sen[sen_i]
        word = sen[sen_i].lemma_.lower()
        print("\n\n\n", word)
        if token.pos_ == "VERB" and token.dep_ != "xcomp" and word not in verbs:
            verbs.append(word)
        elif token.pos_ == "NOUN":
            if k.check_explicit_change_in_kitchenware(token, word, sen, sen_i):
                print("kitchenware explicitly to: ", k.cur_kitchenware)

            if token.dep_ == "compound" and sen_i + 1 < len(sen):
                compound_word = word + " " + sen[sen_i + 1].lemma_.lower()
                handle_potential_food(compound_word, track_concepts)

            handle_potential_food(word, track_concepts)

        print("current txt kitchenware: ", k.cur_kitchenware)
        cv_kitchenware_dict = s.get_cv_detected_tool()
        print("cv detected: ", cv_kitchenware_dict)
        utensils_detected = get_detected_utensils(cv_kitchenware_dict, k.cur_kitchenware, s)
        print("utensils to be used: ", utensils_detected)

        if len(utensils_detected) > 0:
            uuf.append_utensils_found(utensils_detected)
            utp.append_utensils_found(utensils_detected)

        sen_i += 1


def parse_recipe(rec, nl, used_to_prep, kitchenware, utensil_used_to, track_concepts, sync):
    dictionary = ast.literal_eval(rec)
    for key in dictionary:
        step = nl(dictionary[key])
        sentences = list(step.sents)
        kitchenware_tracker.cur_kitchenware = None

        for sentence in sentences:
            print("\n\n", sentence)
            track_concepts.foods_in_sentence = {}
            verbs = []
            utensil_used_to.utensils_in_sentence = {}
            used_to_prep.utensils_in_sentence = {}

            kitchenware.pre_parse_sentence_to_find_kitchenware(sentence)
            print("Kitchenware before analyzing sentence: ", kitchenware.cur_kitchenware, "\n")
            analyze_sentence(sentence, used_to_prep, kitchenware, utensil_used_to, track_concepts, verbs, sync)

            utensil_used_to.append_verbs_to_utensils(verbs)
            used_to_prep.append_foods_to_utensils(track_concepts.foods_in_sentence)
            print("utensils found in sentence: ", utensil_used_to.utensils_in_sentence)
            print("verbs in sentence: ", verbs)
            print("foods in sentence: ", track_concepts.foods_in_sentence)


if __name__ == '__main__':
    utils_ops.tf = tf.compat.v1
    tf.gfile = tf.io.gfile

    category_index = label_map_util.create_category_index_from_labelmap(path.PATH_TO_LABELS, use_display_name=True)
    model = inference.load_model(path.model_name)
    files = os.listdir(path.PATH_TO_VIDEOS)

    recipe_rows = db.sql_fetch_1to1_videos("all")
    nlp = spacy.load('en_core_web_trf')

    used_to_prepare = UtensilsToFoods()
    kitchenware_tracker = Container()
    util_used_for = UtensilsToVerbs()
    track_concept_net_results = concept_net.TrackConceptsFound()

    i = 1
    for recipe in recipe_rows:
        # print("\n\n\n", recipe)
        if recipe[db.RecipeWithVideoI.VIDEO_ID] == 0:
            print("VIDEO ID: ", recipe[db.RecipeWithVideoI.VIDEO_ID], " for recipe: ", recipe[db.RecipeWithVideoI.URL])

            # vide 0: cv_detected_kitchenware_per_second_of_vid = [{None: {'sieve': 52}}, {None: {'turner': 41}}, {None: {'sieve': 50}}, {None: {'whisk': 45}}, {None: {'whisk': 49}}, {None: {'whisk': 47}}, {}, {None: {'pinch-bowl': 49}}, {'bowl': ''}, {'bowl': {'pinch-bowl': 43}}, {}, {}, {'bowl': ''}, {None: {'jar': 41}}, {'blender': ''}, {'bowl': ''}, {'blender': ''}, {}, {None: {'silicone-spatula': 59}}, {'blender': ''}, {'blender': ''}, {'blender': ''}, {'blender': ''}, {'blender': {'whisk': 58}}, {'bowl': ''}, {'bowl': ''}, {'bowl': ''}, {'bowl': ''}, {}, {None: {'whisk': 63}}, {None: {'sieve': 52}}, {None: {'sieve': 58}}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': {'brush': 43}, 'bowl': ''}, {'bowl': '', 'baking-sheet': ''}, {'bowl': '', 'baking-sheet': ''}, {None: {'silicone-spatula': 52}}, {}, {None: {'sieve': 58}}, {None: {'silicone-spatula': 51}}, {None: {'turner': 40}}, {None: {'silicone-spatula': 42}}, {None: {'silicone-spatula': 40}}, {}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': {'pinch-bowl': 44}, 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {}, {'plate': ''}, {}, {'bowl': '', 'baking-sheet': ''}, {'bowl': '', 'baking-sheet': ''}, {'bowl': '', 'baking-sheet': '', 'food-container': ''}, {'bowl': ''}, {'bowl': ''}, {'baking-sheet': {'oven-glove': 60}, 'bowl': ''}, {'baking-sheet': {'oven-glove': 51}, 'bowl': ''}, {'baking-sheet': {'tongs': 60}, 'bowl': ''}, {'baking-sheet': {'tongs': 65}, 'bowl': ''}, {'baking-sheet': {'tongs': 43}, 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': {'tongs': 45}, 'bowl': ''}, {'plate': '', 'bowl': ''}, {'plate': '', 'bowl': ''}, {'bowl': ''}, {'bowl': ''}, {'plate': '', 'baking-dish': ''}, {'plate': '', 'baking-dish': '', 'bowl': ''}, {}, {None: {'whisk': 45}}, {None: {'whisk': 48}}, {None: {'silicone-spatula': 47}}, {'plate': ''}, {'plate': '', 'food-container': ''}, {'plate': ''}, {'plate': ''}, {None: {'sieve': 46}}, {None: {'whisk': 47, 'sieve': 41}}, {None: {'whisk': 65, 'sieve': 42}}, {None: {'whisk': 74}}, {None: {'whisk': 55, 'sieve': 50}}, {None: {'whisk': 45}}, {}, {}, {}, {}, {}, {}]
            video_file = vid.get_video_file(files, recipe[db.RecipeWithVideoI.VIDEO_ID])
            # cv_detected_kitchenware_per_second_of_vid = overlapping_tools.get_cv_tools_in_sequential_order(
            #     video_file, model, category_index)
            cv_detected_kitchenware_per_second_of_vid = [{None: {'sieve': 52}}, {None: {'turner': 41}}, {None: {'sieve': 50}}, {None: {'whisk': 45}}, {None: {'whisk': 49}}, {None: {'whisk': 47}}, {}, {None: {'pinch-bowl': 49}}, {'bowl': ''}, {'bowl': {'pinch-bowl': 43}}, {}, {}, {'bowl': ''}, {None: {'jar': 41}}, {'blender': ''}, {'bowl': ''}, {'blender': ''}, {}, {None: {'silicone-spatula': 59}}, {'blender': ''}, {'blender': ''}, {'blender': ''}, {'blender': ''}, {'blender': {'whisk': 58}}, {'bowl': ''}, {'bowl': ''}, {'bowl': ''}, {'bowl': ''}, {}, {None: {'whisk': 63}}, {None: {'sieve': 52}}, {None: {'sieve': 58}}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': {'brush': 43}, 'bowl': ''}, {'bowl': '', 'baking-sheet': ''}, {'bowl': '', 'baking-sheet': ''}, {None: {'silicone-spatula': 52}}, {}, {None: {'sieve': 58}}, {None: {'silicone-spatula': 51}}, {None: {'turner': 40}}, {None: {'silicone-spatula': 42}}, {None: {'silicone-spatula': 40}}, {}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': {'pinch-bowl': 44}, 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {}, {'plate': ''}, {}, {'bowl': '', 'baking-sheet': ''}, {'bowl': '', 'baking-sheet': ''}, {'bowl': '', 'baking-sheet': '', 'food-container': ''}, {'bowl': ''}, {'bowl': ''}, {'baking-sheet': {'oven-glove': 60}, 'bowl': ''}, {'baking-sheet': {'oven-glove': 51}, 'bowl': ''}, {'baking-sheet': {'tongs': 60}, 'bowl': ''}, {'baking-sheet': {'tongs': 65}, 'bowl': ''}, {'baking-sheet': {'tongs': 43}, 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': '', 'bowl': ''}, {'baking-sheet': {'tongs': 45}, 'bowl': ''}, {'plate': '', 'bowl': ''}, {'plate': '', 'bowl': ''}, {'bowl': ''}, {'bowl': ''}, {'plate': '', 'baking-dish': ''}, {'plate': '', 'baking-dish': '', 'bowl': ''}, {}, {None: {'whisk': 45}}, {None: {'whisk': 48}}, {None: {'silicone-spatula': 47}}, {'plate': ''}, {'plate': '', 'food-container': ''}, {'plate': ''}, {'plate': ''}, {None: {'sieve': 46}}, {None: {'whisk': 47, 'sieve': 41}}, {None: {'whisk': 65, 'sieve': 42}}, {None: {'whisk': 74}}, {None: {'whisk': 55, 'sieve': 50}}, {None: {'whisk': 45}}, {}, {}, {}, {}, {}, {}]
            for elem in cv_detected_kitchenware_per_second_of_vid:
                print(elem)
            print(len(cv_detected_kitchenware_per_second_of_vid), cv_detected_kitchenware_per_second_of_vid)

            sync_text_with_video = Sync(recipe, nlp, cv_detected_kitchenware_per_second_of_vid)
            parse_recipe(recipe[db.RecipeI.PREPARATION], nlp, used_to_prepare, kitchenware_tracker, util_used_for,
                         track_concept_net_results, sync_text_with_video)

            print("\n\n\niteration: ", i, " is over. Analyzed recipe: ", recipe[db.RecipeI.URL], ". All data so far:")
            print("\n\nrecipe: ", recipe[db.RecipeI.PREPARATION])
            print("\n\nutensil to food: ", used_to_prepare.utensils_to)
            print("\n\nutensil used for: ", util_used_for.utensils_to)
            print("\n\nconceptNet stored: ", track_concept_net_results.noun_to_concepts)

            if i == 3:
                break
            i += 1

    util_used_for.analyze_verbs_and_convert_to_csv()
    w_csv.write_to_csv(list(util_used_for.csv_data.keys()), util_used_for.csv_data, "utensils_used_for.csv")

    used_to_prepare.analyze_foods_and_convert_to_csv()
    w_csv.write_to_csv(list(used_to_prepare.csv_data.keys()), used_to_prepare.csv_data, "utensils_used_to_prepare.csv")
