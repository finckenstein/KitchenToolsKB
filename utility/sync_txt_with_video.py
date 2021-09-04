import ast

import database_query as db
from utility.video_utility_functions import get_video_length
import utility.paths as path
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


class Sync:
    def __init__(self, recipe, nlp, history_of_tools_in_video):
        video_duration = len(history_of_tools_in_video)
        word_count = get_number_of_words(recipe[db.RecipeWithVideoI.PREPARATION], nlp)

        self.words_per_second = word_count / video_duration
        print("words_per_seconds: ", self.words_per_second)

        self.tools_in_video = history_of_tools_in_video
        self.wait = False
        self.word_remainder = 0
        self.video_timestamp = 0
        self.counter = 0
        self.video_is_done = False

    def update_index_values(self):
        print(self.counter, int(self.words_per_second), self.counter > int(self.words_per_second))
        print()
        if self.counter > int(self.words_per_second):
            self.word_remainder += (self.counter - self.words_per_second)
            self.counter = 0
            self.video_timestamp += self.word_remainder
            print("incremented timestamp to: ", self.video_timestamp)
        elif self.word_remainder >= 1:
            self.word_remainder -= 1
            self.video_timestamp += 1
            print("incremented timestamp to: ", self.video_timestamp)
        else:
            print("in else. no values changed")

    def get_cv_detected_kitchenware(self):
        print("length of tools in counter: ", len(self.tools_in_video))
        self.update_index_values()

        video_detected_kitchenware = None
        if round(self.video_timestamp) < len(self.tools_in_video):
            video_detected_kitchenware = self.tools_in_video[round(self.video_timestamp)]
        else:
            self.video_is_done = True

        return video_detected_kitchenware

    def increment_word_counter(self):
        self.counter += 1
        print("incremented word counter to: ", self.counter)
