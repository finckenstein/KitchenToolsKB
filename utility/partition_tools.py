kitchenware_cv = ['bowl', 'pan', 'pot', 'cutting-board', 'plate', 'baking-sheet', 'baking-dish', 'blender',
                  'food-container', 'baking-form', 'baking-rack', 'cupcake-tin']

tools_cv = ['pinch-bowl', 'silicone-spatula', 'jug', 'lepel', 'tongs', 'wooden-spatula', 'whisk', 'fork', 'spoon',
            'knife', 'mixer', 'measuring-cup', 'turner', 'sieve', 'peeler', 'rolling-pin',
            'brush', 'skimmer', 'ladle', 'scoop', 'grater', 'icing-spatula', 'pepper-mill', 'hammer', 'chopsticks',
            'oil-dispenser', 'lid', 'squeezer', 'jar', 'oven-glove', 'masher', 'pizza-cutter']

cutlery_cv = ['fork', 'knife', 'spoon', 'chopsticks']

eating_kitchenware_cv = ['bowl', 'plate']

synonymous_kitchenware = {'pan': ['skillet'],
                          'pot': ['saucepan'],
                          'baking dish': ['foil dish', 'casserole', 'baking form'],
                          'baking sheet': ['sheet pan', 'baking rack'],
                          'grill': ['griddle', 'barbecue', 'bbq'],
                          'blender': [], 'cupcake tin': [], 'cutting board': [],
                          'bowl': ['food container'], 'plate': []}


def is_tool_util(tool):
    return tool in tools_cv


def is_tool_kitchenware(key):
    return key in kitchenware_cv


def get_partitioning_of_tools(cv_tools, func):
    tmp = []
    for elem in cv_tools:
        for tool_key in elem:
            print(tool_key, elem[tool_key])
            if func(tool_key):
                tmp.append(tool_key)
    return tmp


def get_kitchenware(tools):
    kitchenware = get_partitioning_of_tools(tools, is_tool_kitchenware)
    tmp = {}
    for kit in kitchenware:
        tmp[kit] = ''
    return tmp


def get_utils(cv_detected):
    utils = get_partitioning_of_tools(cv_detected, is_tool_util)
    return {None: utils}
