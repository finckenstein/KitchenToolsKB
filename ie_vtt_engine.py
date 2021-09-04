#!/usr/bin/env python3
import tensorflow as tf
import os
import cv2
import spacy
import ast
import csv

import database_query as db
from utility import paths as path, video_utility_functions as vid

from computer_vision import make_inference_from_cv as inference
from computer_vision.tensorflow_object_detection_utils import ops as utils_ops
from computer_vision.tensorflow_object_detection_utils import label_map_util

from utility.overlapping_tools_in_frame import check_for_overlapping_tools, is_tool_kitchenware, is_tool_util, get_tool


def is_verb_or_pronoun(token):
    return token.pos_ == "VERB" or token.pos_ == "PRON"


def is_noun(token):
    return token.pos_ == "NOUN"


def analyze_sentence(sen, container, vtt):
    sentence_i = 0
    explicitly_stated = False
    implicitly_stated = False
    current_verb = None

    while sentence_i < len(sen):
        token = sen[sentence_i]
        word = sen[sentence_i].lemma_.lower()

        print("\n\nNEW WORD: ", word)

        if is_verb_or_pronoun(token):
            if container.check_verb_to_verify_implied_kitchenware(word):
                implicitly_stated = True
                print(word, " changed kitchenware implicitly to: ", container.cur_kitchenware)
            current_verb = word
        elif is_noun(token):
            if container.check_explicit_change_in_kitchenware(token, word, sen, sentence_i):
                explicitly_stated = True
                print(word, " changed kitchenware explicitly to: ", container.cur_kitchenware)

        found_tools = vtt.get_cv_detected_tool()
        print("CV detected tools: ", found_tools)

        sentence_i += 1


def parse_recipe(rec, n, container, vtt):
    dictionary = ast.literal_eval(rec[db.RecipeWithVideoI.PREPARATION])
    for key in dictionary:
        step = n(dictionary[key])
        sentences = list(step.sents)

        for sentence in sentences:
            print("\n\n", sentence)
            analyze_sentence(sentence, container, vtt)


def filter_out_none_kitchenware_tools_tuple(list_of_overlapping_tools):
    tuple_in_formation = []
    for tools_tuple in list_of_overlapping_tools:
        if is_tool_kitchenware(tools_tuple[0]) and is_tool_util(tools_tuple[2]):
            print(is_tool_kitchenware(tools_tuple[0]), is_tool_kitchenware(tools_tuple[2]), tools_tuple,
                  " in if. It is well formatted. Appended!")
            tuple_in_formation.append(tools_tuple)
        elif is_tool_kitchenware(tools_tuple[2]) and is_tool_util(tools_tuple[0]):
            print(is_tool_kitchenware(tools_tuple[2]), is_tool_kitchenware(tools_tuple[0]), tools_tuple,
                  " in elif. is well formatted. Appended!")
            tuple_in_formation.append((tools_tuple[2], tools_tuple[0]))
    return tuple_in_formation


def open_capture(f, video_id):
    cap = cv2.VideoCapture(path.PATH_TO_VIDEOS + f)
    frame_rate = cap.get(5)
    overlapping_tools = []

    while cap.isOpened():
        found_tools = inference.make_inference_for_ow(cap, detection_model, frame_rate, category_index, 0.35, 1)
        if not found_tools[0]:
            break
        elif len(found_tools[1]) > 0:
            tmp = check_for_overlapping_tools(found_tools[1])

            if len(tmp) > 0:
                tmp = filter_out_none_kitchenware_tools_tuple(tmp)
                overlapping_tools.append(tmp)
                print("appended to tools list\n")
            else:
                print("did not append anything\n")
        elif len(found_tools[1]) == 0 and is_tool_kitchenware(get_tool(found_tools[1])):
            cv_detected_kitchenware = get_tool(found_tools[1])
            print("appending solo: ", cv_detected_kitchenware)
            overlapping_tools.append(get_tool(cv_detected_kitchenware))

    for elem in overlapping_tools:
        print(elem)

    cap.release()
    cv2.destroyAllWindows()

    print(overlapping_tools)
    return overlapping_tools


def turn_dictionary_into_list(location_tool_combination):
    node_tuple = []
    for k in location_tool_combination:
        node_tuple.append({'Nodes': k,
                           'Occurrences': location_tool_combination[k][0],
                           'Accuracy': (location_tool_combination[k][1][0] / location_tool_combination[k][0],
                                        location_tool_combination[k][1][1] / location_tool_combination[k][0]),
                           'Video': location_tool_combination[k][2]})
    return node_tuple


if __name__ == '__main__':
    utils_ops.tf = tf.compat.v1
    tf.gfile = tf.io.gfile

    category_index = label_map_util.create_category_index_from_labelmap(path.PATH_TO_LABELS, use_display_name=True)
    detection_model = inference.load_model(path.model_name)
    files = os.listdir(path.PATH_TO_VIDEOS)

    i = 0
    for file in files:
        if '.mp4' in file:
            vid_id = vid.get_video_id(file)
            print("VIDEO ID: ", vid_id)

            open_capture(file, vid_id)


