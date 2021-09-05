import cv2
import utility.paths as path
import utility.partition_tools as pt
from computer_vision import make_inference_from_cv as inference
from utility.track_kitchenware.kitchenware import filter_out_none_kitchenware_tools_tuple


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
                overlapping_tools_in_frame.append_list_of_verbs(tuple1)
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


def filter_out_duplicate_kitchenware_in_overlapping(kitchenware_dic, overlapping):
    tmp = {}
    for kitchenware in kitchenware_dic:
        if kitchenware not in overlapping:
            tmp[kitchenware] = ''
    return tmp


def filter_out_duplicate_utils_in_overlapping(utils_dic, overlapping):
    tmp = []
    for kitchenware_key in overlapping:
        if overlapping[kitchenware_key] not in utils_dic[None]:
            tmp.append(overlapping[kitchenware_key])
    return {None: tmp}


def cv_detected_tools(found_tools, tools_overlap_with_kitchenware):
    print("CV detected tools: ", found_tools)

    detected_kitchenware = pt.get_kitchenware(found_tools)
    print("detected_kitchenware: ", detected_kitchenware)

    detected_utils = pt.get_utils(found_tools)
    print("detected utils: ", detected_utils)

    overlapping_tools = check_for_overlapping_tools(found_tools)
    well_formatted_overlapping_tools = filter_out_none_kitchenware_tools_tuple(overlapping_tools)
    print("well formatted overlapping tools: ", well_formatted_overlapping_tools)

    if len(well_formatted_overlapping_tools) > 0:
        detected_kitchenware = filter_out_duplicate_kitchenware_in_overlapping(detected_kitchenware,
                                                                               well_formatted_overlapping_tools)
        detected_utils = filter_out_duplicate_utils_in_overlapping(detected_utils,
                                                                   well_formatted_overlapping_tools)
        to_append = well_formatted_overlapping_tools
        to_append.update(detected_kitchenware)
        if len(detected_utils[None]) > 0:
            to_append.update(detected_utils)
        tools_overlap_with_kitchenware.append_list_of_verbs(to_append)
        print("branch 1 appended: ", to_append)
    elif len(detected_kitchenware) > 0 and len(detected_utils[None]) > 0:
        to_append = detected_kitchenware
        to_append.update(detected_utils)
        tools_overlap_with_kitchenware.append_list_of_verbs(to_append)
        print("branch 2 appended: ", to_append)
    elif len(detected_kitchenware) > 0:
        tools_overlap_with_kitchenware.append_list_of_verbs(detected_kitchenware)
        print("branch 3 appended: ", detected_kitchenware)
    elif len(detected_utils[None]) > 0:
        tools_overlap_with_kitchenware.append_list_of_verbs(detected_utils)
        print("branch 4 appended: ", detected_utils)
    else:
        tools_overlap_with_kitchenware.append_list_of_verbs([])
        print("branch 5 appended empty list")


def get_cv_tools_in_sequential_order(f, model, category_index):
    cap = cv2.VideoCapture(path.PATH_TO_VIDEOS + f)
    frame_rate = cap.get(5)
    tools_overlap_with_kitchenware = []

    while cap.isOpened():
        found_tools = inference.make_inference_for_ow(cap, model, frame_rate, category_index, 0.5, 1)
        if not found_tools[0]:
            break

        if found_tools[1] is None:
            print("appending empty array []")
            tools_overlap_with_kitchenware.append([])
        elif len(found_tools[1]) > 0:
            cv_detected_tools(found_tools[1], tools_overlap_with_kitchenware)

    for elem in tools_overlap_with_kitchenware:
        print(elem)

    cap.release()
    cv2.destroyAllWindows()

    return tools_overlap_with_kitchenware
