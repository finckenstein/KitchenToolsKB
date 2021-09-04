import cv2
import utility.paths as path
import utility.partition_tools as pt
from computer_vision import make_inference_from_cv as inference
from utility.track_kitchenware.kitchenware import filter_out_none_kitchenware_tools_tuple, get_kitchenware


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


def iterate_over_overlapping_tools(overlapping_tools, current_tool, overlapping_tools_in_frame, current_tool_score):
    did_append = False
    if len(overlapping_tools) >= 1:

        for consider_tool in overlapping_tools:
            elem_tool = get_tool(consider_tool)
            elem_score = consider_tool[elem_tool]
            print(elem_tool)

            tuple1 = current_tool, current_tool_score, elem_tool, elem_score
            tuple2 = elem_tool, elem_score, current_tool, current_tool_score
            if tuple1 not in overlapping_tools_in_frame and tuple2 not in overlapping_tools_in_frame:
                overlapping_tools_in_frame.append(tuple1)
                did_append = True
    return did_append


def reformat_data(list_of_quad):
    tmp = []
    for qud in list_of_quad:
        if pt.is_tool_kitchenware(qud[0]) and pt.is_tool_util(qud[2]):
            tmp.append((qud[2], qud[3], qud[0], qud[1]))
        else:
            tmp.append(qud)
    return tmp


def check_for_overlapping_tools(found_tools):
    overlapping_tools_in_frame = []
    for current_tool in found_tools:
        for current_key in current_tool:
            overlapping_tools = get_overlapping_tools(found_tools, current_key, current_tool)
            score = current_tool[current_key][1]
            iterate_over_overlapping_tools(overlapping_tools, current_key, overlapping_tools_in_frame, score)
    print("overlapping tools in frame: ", overlapping_tools_in_frame)

    return reformat_data(overlapping_tools_in_frame)


def get_cv_tools_in_sequential_order(f, model, category_index):
    cap = cv2.VideoCapture(path.PATH_TO_VIDEOS + f)
    frame_rate = cap.get(5)
    tools_overlap_with_kitchenware = []

    while cap.isOpened():
        found_tools = inference.make_inference_for_ow(cap, model, frame_rate, category_index, 0.5, 1)
        if not found_tools[0]:
            break

        if found_tools[1] is None:
            print("CV detected tools: ", found_tools[1])
            print("appending empty array []")
            tools_overlap_with_kitchenware.append([])
        elif len(found_tools[1]) > 0:
            print("CV detected tools: ", found_tools[1])
            detected_kitchenware = get_kitchenware(found_tools[1])
            print("detected_kitchenware: ", detected_kitchenware)

            overlapping_tools = check_for_overlapping_tools(found_tools[1])
            overlapping_tools_are_well_formatted = filter_out_none_kitchenware_tools_tuple(overlapping_tools)
            print("these overlapping tools are well formatted: ", overlapping_tools_are_well_formatted)

            if len(overlapping_tools_are_well_formatted) > 0:
                print("appending tool kitchenware tuple: ", overlapping_tools_are_well_formatted)
                tools_overlap_with_kitchenware.append(overlapping_tools_are_well_formatted)
            elif len(detected_kitchenware) > 0:
                print("appending solo kitchenware: ", detected_kitchenware)
                tools_overlap_with_kitchenware.append(detected_kitchenware)
            else:
                print("appending empty array []")
                tools_overlap_with_kitchenware.append([])

    for elem in tools_overlap_with_kitchenware:
        print(elem)

    cap.release()
    cv2.destroyAllWindows()

    return tools_overlap_with_kitchenware
