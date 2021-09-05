from utility.overlapping_tools_in_frame import get_overlapping_tools, is_tool_kitchenware, get_tool


class OperateWith:
    def __init__(self):
        self.location_tool_combination = {}

    def append_data(self, overlapping_tools_in_frame, vid_file):
        for quad in overlapping_tools_in_frame:
            tup_format1 = quad[0], quad[2]
            tup_format2 = quad[2], quad[0]

            if tup_format1 not in self.location_tool_combination and tup_format2 not in self.location_tool_combination:
                self.location_tool_combination[tup_format1] = [1, [quad[1], quad[3]], [vid_file]]
            elif tup_format1 in self.location_tool_combination:
                self.update_tool_list(tup_format1, quad[1], quad[3], vid_file)
            elif tup_format2 in self.location_tool_combination:
                self.update_tool_list(tup_format2, quad[3], quad[1], vid_file)

    def update_tool_list(self, tuple_format, score1, score2, vid_file):
        self.location_tool_combination[tuple_format][0] += 1
        self.location_tool_combination[tuple_format][1][0] += score1
        self.location_tool_combination[tuple_format][1][1] += score2
        if vid_file not in self.location_tool_combination[tuple_format][2]:
            self.location_tool_combination[tuple_format][2].append_list_of_verbs(vid_file)
        print("incremented occurrence for tuple: ", tuple_format, self.location_tool_combination[tuple_format])
