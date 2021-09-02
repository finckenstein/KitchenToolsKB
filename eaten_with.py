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


class EatenWith:
    def __init__(self):
        self.cutlery = {}
        self.container = {}
        self.last_detected_cutlery = None
        self.last_detected_container = None

    def filter_out_none_cutlery_and_eating_tools(self, tools):
        for tool in tools:
            for tool_key in tool:
                if tool_key in pt.cutlery_cv:
                    self.last_detected_cutlery = tool_key, tool[tool_key][1]
                    if tool_key in self.cutlery:
                        self.cutlery[tool_key].append(tool[tool_key][1])
                        print("[filter_out_none_cutlery] appended for: ", tool_key, len(self.cutlery[tool_key]))
                    else:
                        self.cutlery[tool_key] = [tool[tool_key][1]]
                        print("[filter_out_none_cutlery] added cutlery first time: ", tool_key)
                elif tool_key in pt.eating_kitchenware_cv:
                    self.last_detected_container = tool_key, tool[tool_key][1]
                    if tool_key in self.container:
                        self.container[tool_key].append(tool[tool_key][1])
                        print("[filter_out_none_cutlery] appended for: ", tool_key, len(self.container[tool_key]))
                    else:
                        self.container[tool_key] = [tool[tool_key][1]]
                        print("[filter_out_none_cutlery] added container first time: ", tool_key)

    def determine_container(self):
        tmp_container = find_most_accurate_for_each(self.container)
        most_accurate_container = None
        maxi = -1
        for key in tmp_container:
            if tmp_container[key] > maxi:
                most_accurate_container = key
                maxi = tmp_container[key]
        return most_accurate_container, maxi

    def most_occurring(self, is_cutlery):
        if is_cutlery:
            dic_in_question = self.cutlery
        else:
            dic_in_question = self.container

        maxi = -1
        most_occurring_tool = None
        for tool in dic_in_question:
            if len(dic_in_question[tool]) > maxi:
                most_occurring_tool = tool, fetch_average(tool, dic_in_question)
                maxi = len(dic_in_question[tool])

        if there_are_other_most_occurring_tools(most_occurring_tool, dic_in_question):
            return fetch_other_most_occurring_tools(most_occurring_tool, dic_in_question)
        else:
            return most_occurring_tool

    def most_accurate_cutlery(self, eating_tool):
        tmp_cutlery = find_most_accurate_for_each(self.cutlery)
        most_accurate_cutlery = None
        maximum = -1

        for key in tmp_cutlery:
            if tmp_cutlery[key] > maximum:
                most_accurate_cutlery = key
                maximum = tmp_cutlery[key]
            elif tmp_cutlery[key] == maximum:
                if eating_tool is None:
                    most_accurate_cutlery = key
                elif eating_tool == "bowl" and (key == "spoon" or key == "chopsticks"):
                    most_accurate_cutlery = key
                elif eating_tool == "plate" and (key == "fork" or key == "knife" or key == "chopsticks"):
                    most_accurate_cutlery = key

        return most_accurate_cutlery, maximum


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


def find_most_accurate_for_each(dic):
    tmp_tools = {}
    for tool in dic:
        maxi = -1
        for num in dic[tool]:
            if num > maxi:
                maxi = num
        tmp_tools[tool] = maxi
    return tmp_tools


def fetch_average(cutlery, dic):
    sum_of_acc = 0
    for accuracy in dic[cutlery]:
        sum_of_acc += accuracy
    return sum_of_acc / len(dic[cutlery])


def there_are_other_most_occurring_tools(max_occurring_tool, dic):
    for tool in dic:
        if max_occurring_tool[1] == len(dic[tool]) and max_occurring_tool[0] != tool:
            return True
    return False


def fetch_other_most_occurring_tools(most_occurring_tool, dicti):
    other_tools = most_occurring_tool
    for tool in dicti:
        if most_occurring_tool[1] == len(dicti[tool]) and most_occurring_tool[0] != tool:
            other_tools.append((tool, fetch_average(tool, dicti)))
    return other_tools


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
