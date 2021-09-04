#!/usr/bin/env python3
import tensorflow as tf
import cv2
import os
import csv

from computer_vision import make_inference_from_cv as inference
from utility import paths as path, video_utility_functions as vid, overlapping_tools_in_frame as overlap
from computer_vision.tensorflow_object_detection_utils import label_map_util
from computer_vision.tensorflow_object_detection_utils import ops as utils_ops
from edges.operate_with import OperateWith


def write_to_csv(data):
    fields = ['Nodes', 'Occurrences', 'Accuracy', 'Video', 'Occurrences in Video']
    filename = "operate_with_old.csv"
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)


def turn_dictionary_into_list(location_tool_combination):
    node_tuple = []
    for key in location_tool_combination:
        node_tuple.append({'Nodes': key,
                           'Occurrences': location_tool_combination[key][0],
                           'Accuracy': (location_tool_combination[key][1][0] / location_tool_combination[key][0],
                                        location_tool_combination[key][1][1] / location_tool_combination[key][0]),
                           'Video': location_tool_combination[key][2],
                           'Occurrences in Video': len(location_tool_combination[key][2])})
    return node_tuple


def open_capture(f, video_id, ow):
    cap = cv2.VideoCapture(path.PATH_TO_VIDEOS + f)
    frame_rate = cap.get(5)

    while cap.isOpened():
        found_tools = inference.make_inference_for_ow(cap, detection_model, frame_rate, category_index, 0.5, 1)
        if not found_tools[0]:
            break
        elif found_tools[1] is not None and len(found_tools[1]) > 0:
            tools_that_overlap = overlap.check_for_overlapping_tools(found_tools[1])
            ow.append_data(tools_that_overlap, video_id)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    utils_ops.tf = tf.compat.v1
    tf.gfile = tf.io.gfile

    category_index = label_map_util.create_category_index_from_labelmap(path.PATH_TO_LABELS, use_display_name=True)
    detection_model = inference.load_model(path.model_name)
    files = os.listdir(path.PATH_TO_VIDEOS)

    operate_with = OperateWith()
    i = 0
    for file in files:
        if '.mp4' in file:
            vid_id = vid.get_video_id(file)
            print("VIDEO ID: ", vid_id)

            open_capture(file, vid_id, operate_with)

            print("\n\n\niteration ", i, " is over. Analyzed video: ", vid_id, ". location_tool_combination is:")
            for k in operate_with.location_tool_combination:
                print(k, operate_with.location_tool_combination[k])
            print("\n\n\n")
            i += 1
            break

    list_of_dic = turn_dictionary_into_list(operate_with.location_tool_combination)
    for element in list_of_dic:
        print(element)
    write_to_csv(list_of_dic)
