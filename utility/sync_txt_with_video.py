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


def convert_to_txt_format(past_dict):
    tmp = []
    for container in past_dict:
        if container is not None:
            tmp.append(container.replace("-", " "))
        else:
            tmp.append(None)
    return tmp


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
        cv_kitchenware_dict = self.get_tool()

        if math.ceil(self.word_counter) % math.ceil(self.words_per_second) == 0:
            self.list_index += 1
            self.increase_counter(math.ceil(self.words_per_second) - self.words_per_second)

        self.word_counter += 1
        return cv_kitchenware_dict

    def cv_container_from_past(self):
        if self.list_index < len(self.tools_in_video)-2:
            return self.tools_in_video[int(self.list_index)-2]
        else:
            return {}

    def cv_container_from_future(self):
        if self.list_index < len(self.tools_in_video):
            return self.tools_in_video[int(self.list_index)]
        else:
            return {}

    def cv_tools_from_past_present_future(self, cv_detected):
        past_dict = self.cv_container_from_past()
        if cv_detected is not None:
            past_dict.update(cv_detected)
        past_dict.update(self.cv_container_from_future())
        return past_dict

    def is_video_in_sync_with_txt(self, txt_container, cv_detected):
        if cv_detected is None:
            return 0

        cv_tools = self.cv_tools_from_past_present_future(cv_detected)
        cv_to_txt = convert_to_txt_format(cv_tools)

        if txt_container in cv_to_txt:
            return 1
        else:
            return 0

