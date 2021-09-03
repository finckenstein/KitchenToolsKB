from utility import partition_tools as pt


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


def fetch_other_most_occurring_tools(most_occurring_tool, dicti):
    other_tools = most_occurring_tool
    for tool in dicti:
        if most_occurring_tool[1] == len(dicti[tool]) and most_occurring_tool[0] != tool:
            other_tools.append((tool, fetch_average(tool, dicti)))
    return other_tools


def there_are_other_most_occurring_tools(max_occurring_tool, dic):
    for tool in dic:
        if max_occurring_tool[1] == len(dic[tool]) and max_occurring_tool[0] != tool:
            return True
    return False


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
