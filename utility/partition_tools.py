container_cv = ['bowl', 'pan', 'pot', 'cutting-board', 'plate', 'baking-sheet', 'baking-dish', 'blender',
                'food-container', 'baking-form', 'baking-rack', 'cupcake-tin']

utensils_cv = ['pinch-bowl', 'silicone-spatula', 'jug', 'lepel', 'tongs', 'wooden-spatula', 'whisk', 'fork', 'spoon',
               'knife', 'mixer', 'measuring-cup', 'turner', 'sieve', 'peeler', 'rolling-pin',
               'brush', 'skimmer', 'ladle', 'scoop', 'grater', 'icing-spatula', 'pepper-mill', 'hammer', 'chopsticks',
               'oil-dispenser', 'lid', 'squeezer', 'jar', 'oven-glove', 'masher', 'pizza-cutter']

cutlery_cv = ['fork', 'knife', 'spoon', 'chopsticks', 'person']

eating_container_cv = ['bowl', 'plate']

synonymous_kitchenware = {'pan': ['skillet', 'saucepan'],  # 914 + 359 + 193= 1466
                          'pot': [],  # 584
                          'baking dish': ['foil dish', 'casserole', 'baking form'],  # 121 + 1 + 14 + 0 = 136
                          'baking sheet': ['sheet pan', 'baking rack'],  # 449 + 20 + 9 = 478
                          'grill': ['griddle', 'barbecue', 'bbq'],  # 42 + 19 + 15 + 5 = 81
                          'blender': [],  # 210
                          'cupcake tin': ['muffin tin'],  # 1
                          'cutting board': [],  # 111
                          'bowl': ['food container'],  # 1199 + 0 = 1199
                          'plate': []}  # 166

coco_foods = ['cake', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut']

coco_glasses = ['wine glass', 'bottle', 'cup']


def is_tool_util(tool):
    return tool in utensils_cv


def is_tool_kitchenware(key):
    return key in container_cv


def get_partitioning_of_tools(cv_tools, func):
    tmp = []
    for elem in cv_tools:
        for tool_key in elem:
            if func(tool_key):
                tmp.append((tool_key, elem[tool_key][1]))
    return tmp


def get_kitchenware(tools):
    kitchenware = get_partitioning_of_tools(tools, is_tool_kitchenware)
    tmp = {}
    for kit in kitchenware:
        tmp[kit[0]] = ''
    return tmp


def filter_out_duplicates(tmp_utensil):
    tmp = {}
    for tup in tmp_utensil:
        if tup[0] not in tmp:
            tmp[tup[0]] = tup[1]
        elif tmp[tup[0]] < tup[1]:
            tmp[tup[0]] = tup[1]
    return tmp


def get_utils(cv_detected):
    tmp_utensil = get_partitioning_of_tools(cv_detected, is_tool_util)
    utensil = filter_out_duplicates(tmp_utensil)
    return {None: utensil}
