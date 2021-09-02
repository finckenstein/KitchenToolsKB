#!/usr/bin/env python3
import tensorflow as tf
import cv2
import os
import csv

from computer_vision import make_inference_from_cv as inference
from utility import paths as path, video_utility_functions as vid, partition_tools as pt

from computer_vision.tensorflow_object_detection_utils import label_map_util
from computer_vision.tensorflow_object_detection_utils import ops as utils_ops


class OperateWith:
    def __init__(self):
        self.location_tool_combination = {}

    def check_for_overlapping_tools(self, found_tools, f):
        appended = False
        for current_tool in found_tools:
            for current_key in current_tool:
                overlapping_tools = get_overlapping_tools(found_tools, current_key, current_tool)
                score = current_tool[current_key][1]
                if self.iterate_over_overlapping_tools(overlapping_tools, current_key, score, f):
                    appended = True
        return appended

    def iterate_over_overlapping_tools(self, overlapping_tools, current_tool, tool_score, f):
        did_append = False
        if len(overlapping_tools) >= 1:
            is_current_tool_location = is_key_location(current_tool)

            for consider_tool in overlapping_tools:
                elem_tool = get_tool(consider_tool)
                elem_score = consider_tool[elem_tool]
                is_overlapping_tool_a_location = is_key_location(elem_tool)

                if ((is_current_tool_location and is_overlapping_tool_a_location)
                        or (not is_current_tool_location and not is_overlapping_tool_a_location)):
                    tuple_format1 = current_tool, elem_tool
                    tuple_format2 = elem_tool, current_tool
                    self.overlapping_tools_are_the_same_type(tuple_format1, tuple_format2, tool_score, elem_score, f)
                    did_append = True
                elif not is_current_tool_location and is_overlapping_tool_a_location:
                    tuple_format = (current_tool, elem_tool)
                    self.overlapping_tools_are_different_type(tuple_format, tool_score, elem_score, f)
                    did_append = True
        return did_append

    def overlapping_tools_are_different_type(self, tuple_format, tool_score, elem_score, vid_file):
        if tuple_format not in self.location_tool_combination:
            self.append_to_tool_list(tuple_format, tool_score, elem_score, vid_file)
        else:
            self.update_tool_list(tuple_format, tool_score, elem_score, vid_file)

    def overlapping_tools_are_the_same_type(self, tuple_format1, tuple_format2, tool_score, elem_score, vid_file):
        if tuple_format1 not in self.location_tool_combination and tuple_format2 not in self.location_tool_combination:
            self.append_to_tool_list(tuple_format1, tool_score, elem_score, vid_file)
        elif tuple_format1 in self.location_tool_combination:
            self.update_tool_list(tuple_format1, tool_score, elem_score, vid_file)

    def update_tool_list(self, tuple_format, tool_score, elem_score, vid_file):
        self.location_tool_combination[tuple_format][0] += 1
        self.location_tool_combination[tuple_format][1][0] += tool_score
        self.location_tool_combination[tuple_format][1][1] += elem_score
        if vid_file not in self.location_tool_combination[tuple_format][2]:
            self.location_tool_combination[tuple_format][2].append(vid_file)
        print("incremented occurrence for tuple: ", tuple_format, self.location_tool_combination[tuple_format])

    def append_to_tool_list(self, tuple_format, tool_score, elem_score, vid_file):
        self.location_tool_combination[tuple_format] = [1, [tool_score, elem_score], [vid_file]]
        print("appended for the first time: ", tuple_format, self.location_tool_combination[tuple_format])


def write_to_csv(data):
    fields = ['Nodes', 'Occurrences', 'Accuracy', 'Video']
    filename = "operate_with.csv"
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
                           'Video': location_tool_combination[key][2]})
    return node_tuple


def get_range(dic_values, is_x_axis):
    if is_x_axis:
        return [*range(dic_values[2], dic_values[3], 1)]
    else:
        return [*range(dic_values[0], dic_values[1], 1)]


def is_key_location(key):
    return key in pt.kitchenware_cv


def get_tool(dic):
    for key in dic:
        return key
    return None


def get_overlapping_tools(other_tools_list, current_key, current_tool_dic):
    tmp_tools = []
    current_coordinates = current_tool_dic[current_key]
    current_y_min = current_coordinates[0][0]
    current_y_max = current_coordinates[0][1]
    current_x_min = current_coordinates[0][2]
    current_x_max = current_coordinates[0][3]

    for other_tool_dic in other_tools_list:
        for other_tool_key in other_tool_dic:
            if other_tool_key != current_key:

                other_y_range = get_range(other_tool_dic[other_tool_key][0], is_x_axis=False)
                other_x_range = get_range(other_tool_dic[other_tool_key][0], is_x_axis=True)

                y_axis_overlap = False
                x_axis_overlap = False

                for y_num in other_y_range:
                    if current_y_min < y_num < current_y_max:
                        y_axis_overlap = True
                        break
                for x_num in other_x_range:
                    if current_x_min < x_num < current_x_max:
                        x_axis_overlap = True
                        break

                if y_axis_overlap and x_axis_overlap:
                    tmp_tools.append({other_tool_key: other_tool_dic[other_tool_key][1]})
    return tmp_tools


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

            cap = cv2.VideoCapture(path.PATH_TO_VIDEOS + file)
            frame_rate = cap.get(5)

            while cap.isOpened():
                found_tools = inference.make_inference_for_ow(cap, detection_model, frame_rate, category_index, 0.5, 1) # frame_rate as arg
                if not found_tools[0]:
                    break
                elif found_tools[1]:
                    print("found tools from CV: ", found_tools[1])
                    if operate_with.check_for_overlapping_tools(found_tools[1], vid_id):
                        print("appended to tools list\n")
                    else:
                        print("did not append anything\n")

            cap.release()
            cv2.destroyAllWindows()

            print("\n\n\niteration ", i, " is over. Analyzed video: ", vid_id, ". location_tool_combination is:")
            for key in operate_with.location_tool_combination:
                print(key, operate_with.location_tool_combination[key])
            print("\n\n\n")
            i += 1

    list_of_dic = turn_dictionary_into_list(operate_with.location_tool_combination)
    for element in list_of_dic:
        print(element)
    write_to_csv(list_of_dic)
