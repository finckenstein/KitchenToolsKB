from utility import partition_tools as pt


def is_tool_util(tool):
    return tool in pt.tools_cv


def is_tool_kitchenware(key):
    return key in pt.kitchenware_cv


def get_tool(dic):
    for key in dic:
        return key
    return None


def get_range(dic_values, is_x_axis):
    if is_x_axis:
        return [*range(dic_values[2], dic_values[3], 1)]
    else:
        return [*range(dic_values[0], dic_values[1], 1)]


def get_overlapping_tools(other_tools_list, current_key, current_tool_dic):
    tmp_tools = []
    current_coordinates = current_tool_dic[current_key]
    current_y_min = current_coordinates[0][0]
    current_y_max = current_coordinates[0][1]
    current_x_min = current_coordinates[0][2]
    current_x_max = current_coordinates[0][3]

    for other_tool_dic in other_tools_list:
        for other_tool_key in other_tool_dic:
            if other_tool_key != current_key:

                other_y_range = get_range(other_tool_dic[other_tool_key][0], is_x_axis=False)
                other_x_range = get_range(other_tool_dic[other_tool_key][0], is_x_axis=True)

                y_axis_overlap = False
                x_axis_overlap = False

                for y_num in other_y_range:
                    if current_y_min < y_num < current_y_max:
                        y_axis_overlap = True
                        break
                for x_num in other_x_range:
                    if current_x_min < x_num < current_x_max:
                        x_axis_overlap = True
                        break

                if y_axis_overlap and x_axis_overlap:
                    tmp_tools.append({other_tool_key: other_tool_dic[other_tool_key][1]})
    return tmp_tools


def check_for_overlapping_tools(found_tools):
    print("\n\n", found_tools)
    overlapping_tools_in_frame = []
    for current_tool in found_tools:
        for current_key in current_tool:
            overlapping_tools = get_overlapping_tools(found_tools, current_key, current_tool)
            iterate_over_overlapping_tools(overlapping_tools, current_key, overlapping_tools_in_frame)
    print("overlapping tools in frame: ", overlapping_tools_in_frame, "\n\n")
    return overlapping_tools_in_frame


def iterate_over_overlapping_tools(overlapping_tools, current_tool, overlapping_tools_in_frame):
    print("[iterate_over_overlapping_tools]", current_tool, "overlaps with: ", overlapping_tools)
    did_append = False
    if len(overlapping_tools) >= 1:

        for consider_tool in overlapping_tools:
            elem_tool = get_tool(consider_tool)
            print(elem_tool)

            tuple1 = current_tool, elem_tool
            tuple2 = elem_tool, current_tool
            if tuple1 not in overlapping_tools_in_frame and tuple2 not in overlapping_tools_in_frame:
                print("appending: ", tuple1)
                overlapping_tools_in_frame.append(tuple1)
                did_append = True
    return did_append
