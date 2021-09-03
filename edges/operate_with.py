from utility.overlapping_tools_in_frame import get_overlapping_tools, is_tool_kitchenware, get_tool


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
            is_current_tool_location = is_tool_kitchenware(current_tool)

            for consider_tool in overlapping_tools:
                elem_tool = get_tool(consider_tool)
                elem_score = consider_tool[elem_tool]
                is_overlapping_tool_a_location = is_tool_kitchenware(elem_tool)

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