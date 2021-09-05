import ast
import math

import database_query as db


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
        video_duration = len(history_of_tools_in_video) - 1
        self.word_count = get_number_of_words(recipe[db.RecipeWithVideoI.PREPARATION], nlp) - 2
        self.words_per_second = self.word_count / video_duration
        print("words_per_seconds: ", self.words_per_second)

        self.tools_in_video = history_of_tools_in_video
        self.word_counter = 0
        self.remainder = 0
        self.list_index = 0

    def get_tool(self):
        if self.list_index < len(self.tools_in_video):
            return self.tools_in_video[int(self.list_index)]
        else:
            return None

    def increase_counter(self, difference):
        self.word_counter += difference

    def get_cv_detected_tool(self):
        print(self.word_counter, math.ceil(self.words_per_second), self.word_counter % math.ceil(self.words_per_second) == 0)
        cv_kitchenware_dict = self.get_tool()

        if math.ceil(self.word_counter) % math.ceil(self.words_per_second) == 0:
            self.list_index += 1
            self.increase_counter(math.ceil(self.words_per_second) - self.words_per_second)

        self.word_counter += 1
        return cv_kitchenware_dict

