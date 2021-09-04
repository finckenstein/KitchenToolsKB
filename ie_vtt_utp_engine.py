#!/usr/bin/env python3
import tensorflow as tf
import os
import cv2
import spacy
import ast
import csv

import database_query as db
from utility import paths as path, video_utility_functions as vid
from utility import overlapping_tools_in_frame as overlapping_tools

from computer_vision import make_inference_from_cv as inference
from computer_vision.tensorflow_object_detection_utils import ops as utils_ops
from computer_vision.tensorflow_object_detection_utils import label_map_util
from edges.contains import Contains
from utility.sync_txt_with_video import Sync


def is_verb_or_pronoun(token):
    return token.pos_ == "VERB" or token.pos_ == "PRON"


def is_noun(token):
    return token.pos_ == "NOUN"


def analyze_sentence(sen, c, s):
    sentence_i = 0
    explicitly_stated = False
    implicitly_stated = False
    current_verb = None

    while sentence_i < len(sen):
        token = sen[sentence_i]
        word = sen[sentence_i].lemma_.lower()

        print("\n\nNEW WORD: ", word)

        if is_verb_or_pronoun(token):
            if c.kitchenware.check_verb_to_verify_implied_kitchenware(word):
                implicitly_stated = True
                print(word, " changed kitchenware implicitly to: ", c.kitchenware.cur_kitchenware)
            current_verb = word
        elif is_noun(token):
            if c.kitchenware.check_explicit_change_in_kitchenware(token, word, sen, sentence_i):
                explicitly_stated = True
                print(word, " changed kitchenware explicitly to: ", c.kitchenware.cur_kitchenware)

        cv_kitchenware_dict = s.get_cv_detected_tool()

        print("reached word: ", s.word_counter, " out of: ", s.word_count)
        print("at list index: ", s.list_index, " out of: ", len(s.tools_in_video))

        # TODO: implement edge cases e.g. len(cv_kitchenware_dict.keys()) >= 2, len(cv_kitchenware_dict.keys()) == 0

        print("\ncv_kitchenware_dict:", cv_kitchenware_dict)

        sentence_i += 1


def parse_recipe(rec_preparation, n, container, syn):
    dictionary = ast.literal_eval(rec_preparation)
    print("parse_recipe preparation dictionary:", dictionary)

    for key in dictionary:
        step = n(dictionary[key])
        sentences = list(step.sents)
        print(step)
        for sentence in sentences:
            print("\n\n", sentence)
            analyze_sentence(sentence, container, syn)


if __name__ == '__main__':
    utils_ops.tf = tf.compat.v1
    tf.gfile = tf.io.gfile

    category_index = label_map_util.create_category_index_from_labelmap(path.PATH_TO_LABELS, use_display_name=True)
    model = inference.load_model(path.model_name)
    files = os.listdir(path.PATH_TO_VIDEOS)

    recipe_rows = db.sql_fetch_1to1_videos("all")
    nlp = spacy.load('en_core_web_trf')
    contains_edge = Contains(db.sql_fetch_kitchenware_db())
    i = 1

    for recipe in recipe_rows:
        if recipe[db.RecipeWithVideoI.VIDEO_ID] == 0:
            video_file = vid.get_video_file(files, recipe[db.RecipeWithVideoI.VIDEO_ID])
            print("VIDEO ID: ", recipe[db.RecipeWithVideoI.VIDEO_ID], " for recipe: ", recipe[db.RecipeWithVideoI.URL])

            # cv_detected_kitchenware_per_second_of_vid = overlapping_tools.get_cv_tools_in_sequential_order(
            #     video_file, model, category_index)
            cv_detected_kitchenware_per_second_of_vid = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], {'blender': []}, [], {'blender': []}, [], [], {'blender': []}, {'blender': []}, {'blender': []}, {'blender': []}, {'whisk': 'blender'}, [], [], [], [], [], [], [], [], {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'bowl': [], 'baking-sheet': []}, {'bowl': [], 'baking-sheet': []}, [], [], [], [], [], [], [], [], {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, [], [], [], {'bowl': [], 'baking-sheet': []}, {'bowl': [], 'baking-sheet': []}, {'bowl': [], 'baking-sheet': []}, {'bowl': []}, {'bowl': []}, {'oven-glove': 'baking-sheet'}, {'oven-glove': 'baking-sheet'}, {'tongs': 'baking-sheet'}, {'tongs': 'baking-sheet'}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'plate': []}, [], {'bowl': []}, {'bowl': []}, {'plate': []}, {'plate': []}, [], [], [], [], {'plate': []}, {'plate': []}, {'plate': []}, {'plate': []}, [], [], [], [], [], [], [], [], [], [], [], []]

            # video 6: cv_detected_kitchenware_per_second_of_vid = [{'cutting-board': []}, {'cutting-board': []}, {'cutting-board': []}, {'cutting-board': []}, {'cutting-board': []}, {'pot': []}, {'jug': 'pot'}, {'pot': []}, {'pot': []}, {'pot': []}, {'pot': []}, {'pot': []}, {'pot': []}, {'pot': []}, {'pot': []}, {'pot': []}, {'tongs': 'pot'}, {'jug': 'pot'}, [], [], {'lid': 'pot'}, {'tongs': 'pot'}, {'tongs': 'pot'}, {'pot': [], 'bowl': []}, {'pot': []}, {'pot': []}, {'pot': [], 'bowl': []}, {'pot': []}, {'tongs': 'pot'}, {'pot': []}, {'pot': []}, [], {'pot': []}, {'lepel': 'pot'}, [], {'plate': []}, {'plate': []}, {'plate': []}, {'plate': []}, {'plate': []}, [], [], {'plate': []}, [], [], [], []]
            # video 86: [{'bowl': []}, {'bowl': []}, {'whisk': 'bowl'}, [], [], {'bowl': []}, {'bowl': []}, {'bowl': []}, {'bowl': []}, {'whisk': 'bowl'}, {'bowl': []}, {'bowl': []}, {'bowl': []}, [], [], [], [], [], [], [], [], [], [], [], [], {'baking-sheet': []}, [], [], [], [], [], {'pinch-bowl': 'bowl'}, {'pinch-bowl': 'bowl'}, {'pinch-bowl': 'bowl'}, {'pinch-bowl': 'bowl'}, {'pinch-bowl': 'bowl', 'turner': 'pan'}, {'pinch-bowl': 'bowl'}, {'pinch-bowl': 'bowl'}, {'pinch-bowl': 'bowl'}, {'pinch-bowl': 'bowl'}, [], [], {'turner': 'pan'}, {'pan': [], 'bowl': []}, {'pan': [], 'bowl': []}, {'pan': [], 'bowl': []}, {'pan': [], 'bowl': []}, {'pan': [], 'bowl': []}, {'pan': [], 'bowl': []}, {'pan': [], 'bowl': []}, [], [], {'pinch-bowl': 'pan'}, {'silicone-spatula': 'bowl'}, {'pinch-bowl': 'bowl'}, {'bowl': []}, {'bowl': []}, {'bowl': []}, {'bowl': []}, {'bowl': []}, {'bowl': []}, {'pinch-bowl': 'pan'}, [], [], [], [], [], [], [], [], [], [], [], [], [], [], {'bowl': []}, {'bowl': []}, {'whisk': 'bowl'}, {'whisk': 'bowl'}, {'bowl': []}, {'bowl': []}, [], [], [], [], [], [], [], {'plate': []}, [], [], [], [], [], [], {'bowl': []}, {'bowl': []}, {'bowl': []}, {'bowl': []}, {'bowl': []}]
            # video 0: [[], [], [], [], [], [], [], [], [], [], [], [], [], [], {'blender': []}, [], {'blender': []}, [], [], {'blender': []}, {'blender': []}, {'blender': []}, {'blender': []}, {'whisk': 'blender'}, [], [], [], [], [], [], [], [], {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'bowl': [], 'baking-sheet': []}, {'bowl': [], 'baking-sheet': []}, [], [], [], [], [], [], [], [], {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, [], [], [], {'bowl': [], 'baking-sheet': []}, {'bowl': [], 'baking-sheet': []}, {'bowl': [], 'baking-sheet': []}, {'bowl': []}, {'bowl': []}, {'oven-glove': 'baking-sheet'}, {'oven-glove': 'baking-sheet'}, {'tongs': 'baking-sheet'}, {'tongs': 'baking-sheet'}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'baking-sheet': [], 'bowl': []}, {'plate': []}, [], {'bowl': []}, {'bowl': []}, {'plate': []}, {'plate': []}, [], [], [], [], {'plate': []}, {'plate': []}, {'plate': []}, {'plate': []}, [], [], [], [], [], [], [], [], [], [], [], []]
            print(len(cv_detected_kitchenware_per_second_of_vid), cv_detected_kitchenware_per_second_of_vid)

            sync = Sync(recipe, nlp, cv_detected_kitchenware_per_second_of_vid)
            contains_edge.kitchenware.cur_kitchenware = None
            parse_recipe(recipe[db.RecipeI.PREPARATION], nlp, contains_edge, sync)

            break
