from utility import partition_tools as pt


def find_most_accurate_for_each(dic):
    tmp_tools = {}
    for tool in dic:
        tmp_tools[tool] = max(dic[tool])
    return tmp_tools


def get_average(list_of_accuracies):
    return sum(list_of_accuracies) / len(list_of_accuracies)


def get_other_most_occurring_tools(most_occurring_dict, cutlery_or_container, dicti):
    other_tools = [most_occurring_dict]
    for tool in dicti:
        if most_occurring_dict['Occurrence'] == len(dicti[tool]) and most_occurring_dict[cutlery_or_container] != tool:
            other_tools.append({cutlery_or_container: tool,
                                'Occurrence': len(dicti[tool]),
                                'Average Accuracy': get_average(dicti[tool])})
    return other_tools


def get_other_most_accurate(most_accurate_dic, cutlery_with_most_most_accurate):
    other_most_accurate = [most_accurate_dic]
    tmp_cutlery = {'Cutlery': None, 'Accuracy': -1}

    for cutlery in cutlery_with_most_most_accurate:
        if (cutlery != most_accurate_dic['Cutlery'] and cutlery_with_most_most_accurate[cutlery] > 40
                and cutlery_with_most_most_accurate[cutlery] > tmp_cutlery['Accuracy']):
            tmp_cutlery['Cutlery'] = cutlery
            tmp_cutlery['Accuracy'] = cutlery_with_most_most_accurate[cutlery]

    if tmp_cutlery['Cutlery'] is not None:
        other_most_accurate.append(tmp_cutlery)

    return other_most_accurate


class CutleryToRecipe:
    def __init__(self, recipe_url, recipe_name, recipe_video):
        self.recipe_url = recipe_url
        self.recipe_name = recipe_name
        self.recipe_video = recipe_video
        self.cutlery = {}
        # {cutlery: [accuracies]}
        self.container = {}
        # {container: [accuracies]}
        self.last_detected_cutlery = {}
        self.last_detected_container = {}
        self.csv_data = []

    def filter_out_none_cutlery_and_eating_utensils(self, tools):
        for tool in tools:
            for tool_key in tool:
                if tool_key in pt.cutlery_cv:
                    self.last_detected_cutlery = {'Container': tool_key, 'Accuracy': tool[tool_key][1]}
                    if tool_key in self.cutlery:
                        self.cutlery[tool_key].append(tool[tool_key][1])
                        print("[filter_out_none_cutlery] appended for: ", tool_key, len(self.cutlery[tool_key]))
                    else:
                        self.cutlery[tool_key] = [tool[tool_key][1]]
                        print("[filter_out_none_cutlery] added cutlery first time: ", tool_key)
                elif tool_key in pt.eating_kitchenware_cv:
                    self.last_detected_container = {'Container': tool_key, 'Accuracy': tool[tool_key][1]}
                    if tool_key in self.container:
                        self.container[tool_key].append(tool[tool_key][1])
                        print("[filter_out_none_cutlery] appended for: ", tool_key, len(self.container[tool_key]))
                    else:
                        self.container[tool_key] = [tool[tool_key][1]]
                        print("[filter_out_none_cutlery] added container first time: ", tool_key)

    def most_occurring(self, cutlery_or_container):
        dic_in_question = {}
        if cutlery_or_container == 'Cutlery':
            dic_in_question = self.cutlery
        elif cutlery_or_container == 'Container':
            dic_in_question = self.container

        most_occurring_tool = {cutlery_or_container: None, 'Occurrence': -1, 'Average Accuracy': -1}

        for tool in dic_in_question:
            if len(dic_in_question[tool]) > most_occurring_tool['Occurrence']:
                most_occurring_tool[cutlery_or_container] = tool
                most_occurring_tool['Occurrence'] = len(dic_in_question[tool])
                most_occurring_tool['Average Accuracy'] = get_average(dic_in_question[tool])

        return get_other_most_occurring_tools(most_occurring_tool, cutlery_or_container, dic_in_question)

    def most_accurate_cutlery(self, container):
        tmp_cutlery = find_most_accurate_for_each(self.cutlery)
        most_accurate_cutlery = {'Cutlery': None, 'Accuracy': -1}

        for key in tmp_cutlery:
            if tmp_cutlery[key] > most_accurate_cutlery['Accuracy']:
                most_accurate_cutlery['Cutlery'] = key
                most_accurate_cutlery['Accuracy'] = tmp_cutlery[key]
            elif tmp_cutlery[key] == most_accurate_cutlery['Accuracy']:
                if container is None:
                    most_accurate_cutlery['Cutlery'] = key
                elif container == "bowl" and (key == "spoon" or key == "chopsticks"):
                    most_accurate_cutlery['Cutlery'] = key
                elif container == "plate" and (key == "fork" or key == "knife" or key == "chopsticks"):
                    most_accurate_cutlery['Cutlery'] = key

        return get_other_most_accurate(most_accurate_cutlery, tmp_cutlery)

    def most_accurate_container(self):
        container_dic = find_most_accurate_for_each(self.container)
        most_accurate_container = {'Container': None, 'Accuracy': -1}

        for container in container_dic:
            if container_dic[container] > most_accurate_container['Accuracy']:
                most_accurate_container['Container'] = container
                most_accurate_container['Accuracy'] = container_dic[container]
        return most_accurate_container

    def analyze_data_and_convert_to_csv(self, used_coco_data):
        most_accurate_container = self.most_accurate_container()
        most_occurring_container = self.most_occurring('Container')

        most_accurate_cutlery = self.most_accurate_cutlery(most_accurate_container['Container'])
        most_occurring_cutlery = self.most_occurring('Cutlery')

        self.csv_data.append({'Recipe Title': self.recipe_name,
                              'Recipe URL': self.recipe_url,
                              'Recipe Video': self.recipe_video,
                              'Most_Accurate_Cutlery': most_accurate_cutlery,
                              'Most_Occurring_Cutlery': most_occurring_cutlery,
                              'Last_Detected_Cutlery': self.last_detected_cutlery,
                              'Most_Accurate_Container': most_accurate_container,
                              'Most_Occurring_Container': most_occurring_container,
                              'Last_Detected_Container': self.last_detected_container,
                              'Used_COCO_Model': used_coco_data})
