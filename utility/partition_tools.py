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
