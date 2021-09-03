#!/usr/bin/env python3
import tensorflow as tf
import cv2
import os
import csv

import database_query as db
from utility import paths as path, video_utility_functions as vid, partition_tools as pt

from computer_vision import make_inference_from_cv as inference
from computer_vision.tensorflow_object_detection_utils import ops as utils_ops
from computer_vision.tensorflow_object_detection_utils import label_map_util


def parse_recipe():


if __name__ == '__main__':
    utils_ops.tf = tf.compat.v1
    tf.gfile = tf.io.gfile

    category_index = label_map_util.create_category_index_from_labelmap(path.PATH_TO_LABELS, use_display_name=True)
    detection_model = inference.load_model(path.model_name)

    files = os.listdir(path.PATH_TO_VIDEOS)
    recipes = db.sql_fetch_1to1_videos('all')
    title_to_cutlery = {}

    for recipe in recipes:
        parse_recipe(recipe)
        video_file = vid.get_video_file(files, recipe[db.RecipeWithVideoI.VIDEO_ID])
        video_length = vid.get_video_length(path.PATH_TO_VIDEOS + video_file)


