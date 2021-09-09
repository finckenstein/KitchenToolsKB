#!/usr/bin/env python3
import tensorflow as tf
import cv2
import os
import csv

import database_query as db
from utility import paths as path, video_utility_functions as vid
import utility.write_to_csv as write_csv
from computer_vision import make_inference_from_cv as inference
from computer_vision.tensorflow_object_detection_utils import ops as utils_ops
from computer_vision.tensorflow_object_detection_utils import label_map_util
from edges.cutlery_to_recipe import CutleryToRecipe


def print_findings(dic):
    print("for recipe: ", dic['Recipe Title'], " with URL: ", dic['Recipe URL'])
    print("Most_Accurate_Cutlery: ", dic['Most_Accurate_Cutlery'])
    print("Most_Occurring_Cutlery: ", dic['Most_Occurring_Cutlery'])
    print("Last_Detected_Cutlery: ", dic['Last_Detected_Cutlery'])
    print("Most_Accurate_Container: ", dic['Most_Accurate_Container'])
    print("Most_Occurring_Container: ", dic['Most_Occurring_Container'])
    print("Last_Detected_Container: ", dic['Last_Detected_Container'])
    print("\n\n\n")


def analyze_video(vid_file, vid_length, eaten_with, model, category_i):
    cap = cv2.VideoCapture(path.PATH_TO_VIDEOS + vid_file)
    frame_rate = cap.set(cv2.CAP_PROP_POS_MSEC, (vid_length - 8) * 1000)

    while cap.isOpened():
        found_tools = inference.make_inference_for_ew(cap, model, frame_rate, category_i, 0.3, 1,
                                                      vid_length)
        print("found tools: ", found_tools)

        if not found_tools[0]:
            break
        elif found_tools[1]:
            for tool in found_tools[1]:
                for tool_key in tool:
                    print(tool[tool_key][1])
            eaten_with.filter_out_none_cutlery_and_eating_utensils(found_tools[1])

    cap.release()
    cv2.destroyAllWindows()


def use_coco_model(ew, vid_file, vid_length, model, categories):
    ew.cutlery = {}
    ew.container = {}
    ew.last_detected_cutlery = {}
    ew.last_detected_container = {}
    analyze_video(vid_file, vid_length, ew, model, categories)
    ew.analyze_data_and_convert_to_csv(True)


if __name__ == '__main__':
    utils_ops.tf = tf.compat.v1
    tf.gfile = tf.io.gfile

    category_index = label_map_util.create_category_index_from_labelmap(path.PATH_TO_LABELS, use_display_name=True)
    detection_model = inference.load_model(path.model_name)

    coco_categories = label_map_util.create_category_index_from_labelmap(path.coco_labels, use_display_name=True)
    coco_model = inference.load_model(path.coco_name)

    files = os.listdir(path.PATH_TO_VIDEOS)
    recipes = db.sql_fetch_1to1_videos('all')
    write_csv.write_headers_for_ew()

    i = 0
    for recipe in recipes:
        eat_with = CutleryToRecipe(recipe[db.RecipeWithVideoI.URL],
                                   recipe[db.RecipeWithVideoI.TITLE], recipe[db.RecipeWithVideoI.VIDEO_ID])
        if recipe[db.RecipeWithVideoI.VIDEO_ID] == 0:
            video_file = vid.get_video_file(files, recipe[db.RecipeWithVideoI.VIDEO_ID])
            video_length = vid.get_video_length(path.PATH_TO_VIDEOS + video_file)

            analyze_video(video_file, video_length, eat_with, detection_model, category_index)

            print("found cutlery: ", eat_with.cutlery)
            print("found container: ", eat_with.container)

            if len(eat_with.cutlery) == 0:
                use_coco_model(eat_with, video_file, video_length, coco_model, coco_categories)
            else:
                eat_with.analyze_data_and_convert_to_csv(False)

            write_csv.append_ew_data_to_csv(eat_with.csv_data)
            print("\n\n\niteration: ", i, " is over. Analyzed video: ", recipe[db.RecipeWithVideoI.VIDEO_ID])
            print_findings(eat_with.csv_data[0])
            i += 1
