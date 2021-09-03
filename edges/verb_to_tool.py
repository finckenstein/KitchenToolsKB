import os
import ast
import cv2

import database_query as db
from utility.video_utility_functions import get_video_file, get_video_length
from computer_vision.make_inference_from_cv import make_inference_for_vtt, load_model
import utility.paths as path
from computer_vision.tensorflow_object_detection_utils import label_map_util
from computer_vision.inference_with_KT_model import iterate_over_video


def get_number_of_words(preparation, nlp):
    prep_dic = ast.literal_eval(preparation)
    word_count = 0

    for key in prep_dic:
        step = nlp(prep_dic[key])
        sentences = list(step.sents)

        for sentence in sentences:
            print(sentence, len(sentence))
            word_count += len(sentence)

    print(word_count)
    return word_count


class VerbsToDescribeTool:
    def __init__(self, recipe, file, category_i, detection_model, nlp):
        self.category = category_i
        self.model = detection_model
        self.path_to_video = path.PATH_TO_VIDEOS + file

        self.wait = False
        self.word_remainder = 0
        self.video_timestamp = 0
        self.counter = 0

        self.video_duration = get_video_length(self.path_to_video) - 3
        word_count = get_number_of_words(recipe[db.RecipeWithVideoI.PREPARATION], nlp)
        self.words_per_second = word_count / self.video_duration
        print("words_per_seconds: ", self.words_per_second)

    def get_cv_detected_tool(self):
        video_detected_kitchenware = None
        if self.counter >= int(self.words_per_second):

            self.word_remainder += self.words_per_second - self.counter
            self.counter = 0

            video_detected_kitchenware = iterate_over_video(self.path_to_video, self.video_timestamp, self.category, self.model)
            # print(video_detected_kitchenware)
            self.video_timestamp += int(self.words_per_second)

        elif self.word_remainder >= 1:
            self.word_remainder -= 1

            video_detected_kitchenware = iterate_over_video(self.path_to_video, self.video_timestamp, self.category, self.model)
            self.video_timestamp += 1

        self.counter += 1

        print("word_remainder: ", self.word_remainder)
        print("counter: ", self.counter)
        print("video_timestamp: ", self.video_timestamp)

        return video_detected_kitchenware
