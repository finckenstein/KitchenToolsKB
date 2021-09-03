#!/usr/bin/env python3
import tensorflow as tf
import cv2
import os
import csv

import database_query as db
from utility import paths as path, video_utility_functions as vid
from computer_vision import make_inference_from_cv as inference
from computer_vision.tensorflow_object_detection_utils import ops as utils_ops
from computer_vision.tensorflow_object_detection_utils import label_map_util
from edges.eaten_with import EatenWith


def print_findings(dic, rec):
    print("for recipe: ", rec[db.RecipeWithVideoI.TITLE], " with URL: ", rec[db.RecipeWithVideoI.URL])
    j = 0
    for elem in dic[(rec[db.RecipeWithVideoI.URL], rec[db.RecipeWithVideoI.TITLE])]:
        if j == 0:
            print("most accurate cutlery: ", elem)
        elif j == 1:
            print("most occurring cutlery: ", elem)
        elif j == 2:
            print("last detected cutlery: ", elem)
        elif j == 3:
            print("most accurate container: ", elem)
        elif j == 4:
            print("most occurring containers: ", elem)
        elif j == 5:
            print("last detected container: ", elem)
        j += 1
    print("\n\n\n")


def write_to_csv(data):
    fields = ['Recipe', 'Most_Accurate_Cutlery', 'Most_Occurring_Cutlery', 'Last_Detected_Cutlery',
              'Most_Accurate_Container', 'Most_Occurring_Container', 'Last_Detected_Container']
    filename = "eaten_with.csv"
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)


def turn_dictionary_into_list(recipes_to_cutlery_dic):
    node_tuple = []
    for key in recipes_to_cutlery_dic:
        node_tuple.append({'Recipe': key,
                           'Most_Accurate_Cutlery': recipes_to_cutlery_dic[key][0],
                           'Most_Occurring_Cutlery': recipes_to_cutlery_dic[key][1],
                           'Last_Detected_Cutlery': recipes_to_cutlery_dic[key][2],
                           'Most_Accurate_Container': recipes_to_cutlery_dic[key][3],
                           'Most_Occurring_Container': recipes_to_cutlery_dic[key][4],
                           'Last_Detected_Container': recipes_to_cutlery_dic[key][5]})
    return node_tuple


def hands_detected(detected):
    for tool in detected:
        for tool_key in tool:
            if tool_key == "person":
                return True
    return False


def hands_are_used(v_file, coco_det_model, coco_cat, v_length):
    capture = cv2.VideoCapture(path.PATH_TO_VIDEOS + v_file)
    f_rate = capture.set(cv2.CAP_PROP_POS_MSEC, (v_length - 5) * 1000)

    while capture.isOpened():
        found = inference.make_inference_for_ew(capture, coco_det_model, f_rate, coco_cat, 0.5, 1,
                                                v_length)
        if not found[0]:
            break
        elif found[1] and hands_detected(found[1]):
            capture.release()
            cv2.destroyAllWindows()
            return True

    capture.release()
    cv2.destroyAllWindows()
    return False


def analyze_video(vid_file, vid_length):
    cap = cv2.VideoCapture(path.PATH_TO_VIDEOS + vid_file)
    frame_rate = cap.set(cv2.CAP_PROP_POS_MSEC, (vid_length - 8) * 1000)

    while cap.isOpened():
        found_tools = inference.make_inference_for_ew(cap, detection_model, frame_rate, category_index, 0.3, 1,
                                                      vid_length)
        print("found tools: ", found_tools)

        if not found_tools[0]:
            break
        elif found_tools[1]:
            eat_with.filter_out_none_cutlery_and_eating_tools(found_tools[1])

    cap.release()
    cv2.destroyAllWindows()


def get_data():
    eating_container = eat_with.determine_container()
    most_occurring_container = eat_with.most_occurring(False)

    if len(eat_with.cutlery) == 0:
        if hands_are_used(video_file, coco_model, coco_categories, video_length):
            return ["hands", None, None, eating_container, most_occurring_container, eat_with.last_detected_container]
        else:
            return [None, None, None, eating_container, most_occurring_container, eat_with.last_detected_container]
    else:
        most_occurring = eat_with.most_occurring(True)
        most_accurate = eat_with.most_accurate_cutlery(eating_container[0])
        if most_accurate[0] == "knife":
            return [('fork', most_accurate), most_occurring, eat_with.last_detected_cutlery,
                    eating_container, most_occurring_container, eat_with.last_detected_container]
        else:
            return [most_accurate, most_occurring, eat_with.last_detected_cutlery,
                    eating_container, most_occurring_container, eat_with.last_detected_container]


if __name__ == '__main__':
    utils_ops.tf = tf.compat.v1
    tf.gfile = tf.io.gfile

    category_index = label_map_util.create_category_index_from_labelmap(path.PATH_TO_LABELS, use_display_name=True)
    detection_model = inference.load_model(path.model_name)

    coco_categories = label_map_util.create_category_index_from_labelmap(path.coco_labels, use_display_name=True)
    coco_model = inference.load_model(path.coco_name)

    files = os.listdir(path.PATH_TO_VIDEOS)
    recipes = db.sql_fetch_1to1_videos('all')
    title_to_cutlery = {}

    i = 0
    for recipe in recipes:
        eat_with = EatenWith()
        if recipe[db.RecipeWithVideoI.VIDEO_ID] == 6:
            video_file = vid.get_video_file(files, recipe[db.RecipeWithVideoI.VIDEO_ID])
            video_length = vid.get_video_length(path.PATH_TO_VIDEOS + video_file)

            analyze_video(video_file, video_length)

            print("found cutlery: ", eat_with.cutlery)
            print("found container: ", eat_with.container)

            title_to_cutlery[(recipe[db.RecipeWithVideoI.URL], recipe[db.RecipeWithVideoI.TITLE])] = get_data()

            print("iteration: ", i, " is over. Analyzed video: ", recipe[db.RecipeWithVideoI.VIDEO_ID])
            print_findings(title_to_cutlery, recipe)
            i += 1

    list_of_dic = turn_dictionary_into_list(title_to_cutlery)
    write_to_csv(list_of_dic)
