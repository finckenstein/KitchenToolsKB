class ToolToTool:
    def __init__(self):
        self.location_tool_combination = {}
        self.csv_data = []

    def append_data(self, overlapping_tools_in_frame, vid_file):
        for quad in overlapping_tools_in_frame:
            tup_format1 = quad[0], quad[2]
            tup_format2 = quad[2], quad[0]

            if tup_format1 not in self.location_tool_combination and tup_format2 not in self.location_tool_combination:
                self.location_tool_combination[tup_format1] = {'Counter': 1,
                                                               'Accuracy': {tup_format1[0]: quad[1],
                                                                            tup_format1[2]: quad[3]},
                                                               'Videos': [vid_file]}
            elif tup_format1 in self.location_tool_combination:
                self.update_tool_list(tup_format1, quad[1], quad[3], vid_file)
            elif tup_format2 in self.location_tool_combination:
                self.update_tool_list(tup_format2, quad[3], quad[1], vid_file)

    def update_tool_list(self, tuple_format, score1, score2, vid_file):
        self.location_tool_combination[tuple_format]['Counter'] += 1
        self.location_tool_combination[tuple_format]['Accuracy'][tuple_format[0]] += score1
        self.location_tool_combination[tuple_format]['Accuracy'][tuple_format[1]] += score2
        if vid_file not in self.location_tool_combination[tuple_format]['Videos']:
            self.location_tool_combination[tuple_format]['Videos'].append_list_of_verbs(vid_file)
        print("incremented occurrence for tuple: ", tuple_format, self.location_tool_combination[tuple_format])

    def convert_data_to_csv(self):
        for tool_tuple in self.location_tool_combination:
            self.csv_data.append({'Nodes': tool_tuple,
                                  'Occurrences': self.location_tool_combination[tool_tuple]['Counter'],
                                  'Accuracy': {tool_tuple[0]: self.location_tool_combination[tool_tuple]['Accuracy'][tool_tuple[0]] / self.location_tool_combination[tool_tuple]['Counter'],
                                               tool_tuple[1]: self.location_tool_combination[tool_tuple]['Accuracy'][tool_tuple[1]] / self.location_tool_combination[tool_tuple]['Counter']},
                                  'Video': self.location_tool_combination[tool_tuple]['Videos'],
                                  'Occurrences in Video': len(self.location_tool_combination[tool_tuple]['Videos'])})
