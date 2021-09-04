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
        self.word_count = get_number_of_words(recipe[db.RecipeWithVideoI.PREPARATION], nlp)
        self.words_per_second = self.word_count / video_duration
        print("words_per_seconds: ", self.words_per_second)

        self.tools_in_video = history_of_tools_in_video
        self.word_counter = 0
        self.remainder = 0
        self.list_index = 0

    def get_cv_kitchenware(self):
        if self.list_index < len(self.tools_in_video):
            return self.tools_in_video[int(self.list_index)]
        else:
            return None

    def increment_index(self):
        self.list_index += 1

    def increase_counter(self, difference):
        self.word_counter += difference

