from utility import partition_tools as pt


def find_most_accurate_for_each(dic):
    print("[find_most_accurate_for_each] ", dic)
    tmp_tools = {}
    for tool in dic:
        print(dic[tool])
        tmp_tools[tool] = {'Top Accuracy': max(dic[tool]), 'Occurrence': len(dic[tool])}
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
        if (cutlery != most_accurate_dic['Cutlery'] and cutlery_with_most_most_accurate[cutlery]['Top Accuracy'] > 55
                and cutlery_with_most_most_accurate[cutlery]['Top Accuracy'] > tmp_cutlery['Accuracy']):
            tmp_cutlery['Cutlery'] = cutlery
            tmp_cutlery['Accuracy'] = cutlery_with_most_most_accurate[cutlery]['Top Accuracy']

    if tmp_cutlery['Cutlery'] is not None:
        other_most_accurate.append(tmp_cutlery)

    return other_most_accurate


def update_dict(dict_in_qust, tool_key, detected_dict):
    if tool_key in dict_in_qust:
        dict_in_qust.append(detected_dict[tool_key][1])
    else:
        dict_in_qust = [detected_dict[tool_key][1]]
    return dict_in_qust


def most_accurate_container_type(contained_type, dic):
    container_dic = find_most_accurate_for_each(dic)
    most_acc_container = {contained_type: None, 'Accuracy': -1}

    for container in container_dic:
        if container_dic[container]['Top Accuracy'] > most_acc_container['Accuracy']:
            most_acc_container[contained_type] = container
            most_acc_container['Accuracy'] = container_dic[container]['Top Accuracy']
    return most_acc_container


class CutleryToRecipe:
    def __init__(self, recipe_url, recipe_name, recipe_video):
        self.recipe_url = recipe_url
        self.recipe_name = recipe_name
        self.recipe_video = recipe_video

        self.foods = {}

        self.glasses = {}
        # {Glasses: [accuracies]}
        self.cutlery = {}
        # {cutlery: [accuracies]}
        self.container = {}
        # {container: [accuracies]}

        self.last_detected_cutlery = {}
        # {'Cutlery': cutlery_tool, 'Accuracy': int}
        self.last_detected_container = {}
        # {'Container': cutlery_tool, 'Accuracy': int}
        self.last_detected_glass = {}
        # {'Glass': glass_tool, 'Accuracy': int}
        self.csv_data = []
        self.other_detected = {}

    def update_container_data(self, tool_key, accuracy):
        self.last_detected_container = {'Container': tool_key, 'Accuracy': accuracy}
        if tool_key in self.container:
            self.container[tool_key].append(accuracy)
        else:
            self.container[tool_key] = [accuracy]

    def update_cutlery_data(self, tool_key, accuracy):
        self.last_detected_cutlery = {'Cutlery': tool_key, 'Accuracy': accuracy}
        if tool_key in self.cutlery:
            self.cutlery[tool_key].append(accuracy)
        else:
            self.cutlery[tool_key] = [accuracy]

    def update_glasses_data(self, tool_key, accuracy):
        self.last_detected_glass = {'Glass': tool_key, 'Accuracy': accuracy}
        if tool_key in self.glasses:
            self.glasses[tool_key].append(accuracy)
        else:
            self.glasses[tool_key] = [accuracy]

    def update_other_data(self, tool_key, accuracy):
        if tool_key in self.other_detected:
            self.other_detected[tool_key].append(accuracy)
        else:
            self.other_detected[tool_key] = [accuracy]

    def update_foods_data(self, tool_key, accuracy):
        if tool_key in self.foods:
            if accuracy > self.foods[tool_key]['Top Accuracy']:
                self.foods[tool_key]['Top Accuracy'] = accuracy
            self.foods[tool_key]['Occurrences'] += 1
        else:
            self.foods[tool_key] = {'Top Accuracy': accuracy, 'Occurrences': 1}

    def filter_out_none_cutlery_and_eating_utensils(self, tools):
        for detected_dict in tools:
            for tool_key in detected_dict:
                if tool_key in pt.cutlery_cv:
                    self.update_cutlery_data(tool_key, detected_dict[tool_key][1])
                elif tool_key in pt.eating_container_cv:
                    self.update_container_data(tool_key, detected_dict[tool_key][1])
                elif tool_key in pt.coco_glasses:
                    self.update_glasses_data(tool_key, detected_dict[tool_key][1])
                elif tool_key in pt.coco_foods:
                    self.update_foods_data(tool_key, detected_dict[tool_key][1])
                else:
                    self.update_other_data(tool_key, detected_dict[tool_key][1])

    def most_occurring(self, cutlery_or_container):
        dic_in_question = {}
        if cutlery_or_container == 'Cutlery':
            dic_in_question = self.cutlery
        elif cutlery_or_container == 'Container':
            dic_in_question = self.container
        elif cutlery_or_container == 'Glass':
            dic_in_question = self.glasses

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
            if tmp_cutlery[key]['Top Accuracy'] > most_accurate_cutlery['Accuracy']:
                most_accurate_cutlery['Cutlery'] = key
                most_accurate_cutlery['Accuracy'] = tmp_cutlery[key]['Top Accuracy']
            elif tmp_cutlery[key] == most_accurate_cutlery['Accuracy']:
                if container is None:
                    most_accurate_cutlery['Cutlery'] = key
                elif container == "bowl" and (key == "spoon" or key == "chopsticks"):
                    most_accurate_cutlery['Cutlery'] = key
                elif container == "plate" and (key == "fork" or key == "knife" or key == "chopsticks"):
                    most_accurate_cutlery['Cutlery'] = key

        return get_other_most_accurate(most_accurate_cutlery, tmp_cutlery)

    def analyze_data_and_convert_to_csv(self):
        most_accurate_container = most_accurate_container_type('Container', self.container)
        most_occurring_container = self.most_occurring('Container')
        all_container = find_most_accurate_for_each(self.container)

        most_accurate_cutlery = self.most_accurate_cutlery(most_accurate_container['Container'])
        most_occurring_cutlery = self.most_occurring('Cutlery')
        all_cutlery = find_most_accurate_for_each(self.cutlery)

        most_accurate_glass = most_accurate_container_type('Glass', self.glasses)
        most_occurring_glass = self.most_occurring('Glass')
        all_glasses = find_most_accurate_for_each(self.glasses)

        self.csv_data.append({'Recipe Title': self.recipe_name,
                              'Recipe URL': self.recipe_url,
                              'Recipe Video': self.recipe_video,
                              'Most_Accurate_Cutlery': most_accurate_cutlery,
                              'Most_Occurring_Cutlery': most_occurring_cutlery,
                              'Last_Detected_Cutlery': self.last_detected_cutlery,
                              'All_Cutlery': all_cutlery,
                              'Most_Accurate_Container': most_accurate_container,
                              'Most_Occurring_Container': most_occurring_container,
                              'Last_Detected_Container': self.last_detected_container,
                              'All_Containers': all_container,
                              'Most_Accurate_Glass': most_accurate_glass,
                              'Most_Occurring_Glass': most_occurring_glass,
                              'Last_Detected_Glass': self.last_detected_glass,
                              'All_Glasses': all_glasses,
                              'Potential Foods': self.foods,
                              'Other detections': self.other_detected})
