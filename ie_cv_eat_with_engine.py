#!/usr/bin/env python3
import tensorflow as tf
import cv2
import os

import database_query as db
from utility import paths as path, video_utility_functions as vid
from utility.write_to_csv import WriteToCSV
from computer_vision import make_inference_from_cv as inference
from computer_vision.tensorflow_object_detection_utils import ops as utils_ops
from computer_vision.tensorflow_object_detection_utils import label_map_util
from edges.cutlery_to_recipe import CutleryToRecipe


def print_findings(dic):
    print("for recipe: ", dic['Recipe Title'], " with URL: ", dic['Recipe URL'])

    print("Most_Accurate_Cutlery: ", dic['Most_Accurate_Cutlery'])
    print("Most_Occurring_Cutlery: ", dic['Most_Occurring_Cutlery'])
    print("Last_Detected_Cutlery: ", dic['Last_Detected_Cutlery'])
    print("All Cutlery: ", dic['All Cutlery'])

    print("Most_Accurate_Container: ", dic['Most_Accurate_Container'])
    print("Most_Occurring_Container: ", dic['Most_Occurring_Container'])
    print("Last_Detected_Container: ", dic['Last_Detected_Container'])
    print("All Containers: ", dic['All Containers:'])

    print("Most_Accurate_Glass: ", dic['Most_Accurate_Glass'])
    print("Most_Occurring_Glass: ", dic['Most_Occurring_Glass'])
    print("Last_Detected_Glass: ", dic['Last_Detected_Glass'])
    print("All Glasses: ", dic['All Glasses:'])
    print("\n\n\n")


def analyze_video(vid_file, vid_dur, eaten_with, cv_coco_modl, coco_category, cv_kt_model, kt_cat):
    cap = cv2.VideoCapture(path.PATH_TO_VIDEOS + vid_file)
    frm_rate = cap.set(cv2.CAP_PROP_POS_MSEC, (vid_dur - 13.5) * 1000) # 12

    while cap.isOpened():
        coco_found_tools = inference.make_inference_for_ew(cap, cv_coco_modl, frm_rate, coco_category, 0.49, 1, vid_dur)
        print("coco found tools: ", coco_found_tools)

        kt_cv_found_tools = inference.make_inference_for_ew(cap, cv_kt_model, frm_rate, kt_cat, 0.49, 1, vid_dur)
        print("kt found tools: ", kt_cv_found_tools)

        if not coco_found_tools[0] or not kt_cv_found_tools[0]:
            break
        if coco_found_tools[1]:
            eaten_with.filter_out_none_cutlery_and_eating_utensils(coco_found_tools[1])
        if kt_cv_found_tools[1]:
            eaten_with.filter_out_none_cutlery_and_eating_utensils(kt_cv_found_tools[1])

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    utils_ops.tf = tf.compat.v1
    tf.gfile = tf.io.gfile

    kt_category = label_map_util.create_category_index_from_labelmap(path.PATH_TO_LABELS, use_display_name=True)
    kt_model = inference.load_model(path.model_name)

    coco_categories = label_map_util.create_category_index_from_labelmap(path.coco_labels, use_display_name=True)
    coco_model = inference.load_model(path.coco_name)

    files = os.listdir(path.PATH_TO_VIDEOS)
    recipes = db.sql_fetch_1to1_videos('all')

    csv_headers = ['Recipe Title', 'Recipe URL', 'Recipe Video',
                   'Most_Accurate_Cutlery', 'Most_Occurring_Cutlery', 'Last_Detected_Cutlery', 'All Cutlery'
                   'Most_Accurate_Container', 'Most_Occurring_Container', 'Last_Detected_Container', 'All Containers'
                   'Most_Accurate_Glass', 'Most_Occurring_Glass', 'Last_Detected_Glass', 'All Glasses'
                   'Potential Foods', 'Other detections']
    store_in_csv = WriteToCSV(csv_headers)
    store_in_csv.write_csv_header('knowledge_base/eaten_with.csv')

    i = 0
    for recipe in recipes:
        eat_with = CutleryToRecipe(recipe[db.RecipeWithVideoI.URL],
                                   recipe[db.RecipeWithVideoI.TITLE], recipe[db.RecipeWithVideoI.VIDEO_ID])

        video_file = vid.get_video_file(files, recipe[db.RecipeWithVideoI.VIDEO_ID])
        video_length = vid.get_video_length(path.PATH_TO_VIDEOS + video_file)

        analyze_video(video_file, video_length, eat_with, coco_model, coco_categories, kt_model, kt_category)

        eat_with.analyze_data_and_convert_to_csv()
        store_in_csv.append_to_csv(eat_with.csv_data, "knowledge_base/eaten_with.csv")

        print("\n\n\niteration: ", i, " is over. Analyzed video: ", recipe[db.RecipeWithVideoI.VIDEO_ID])
        print_findings(eat_with.csv_data[0])
        i += 1
