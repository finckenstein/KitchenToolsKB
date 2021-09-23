#!/usr/bin/env python3
import csv
import ast


def write_to_csv(fields, data, filename):
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)


def get_foods(current_tool, tool_foods_list):
    for tool_food_key in tool_foods_list:
        if tool_food_key[0] == current_tool:
            return ast.literal_eval(tool_food_key[1])
    return None


def add_to_dict(verb_list, foods_list, food_to_verbs_dict):
    for container_verb in verb_list:
        current_container = container_verb[0]
        container_verbs = container_verb[1].split(", ")
        container_food = get_foods(current_container, foods_list)

        if container_food is None:
            continue
        for food in container_food:
            if food in food_to_verbs_dict:
                for verb in container_verbs:
                    if verb not in food_to_verbs_dict[food]:
                        food_to_verbs_dict[food].append(verb)
            else:
                food_to_verbs_dict[food] = container_verbs


def main():
    food_to_verbs = {}
    # container_verb = open('ground_truths/container_used_for_truth.csv')
    # container_verb_list = list(csv.reader(container_verb))
    #
    # container_foods = open('ground_truths/contains_truth.csv')
    # container_foods_r = csv.reader(container_foods)
    # next(container_foods_r)
    # container_foods_list = list(container_foods_r)
    #
    # add_to_dict(container_verb_list, container_foods_list, food_to_verbs)

    utensil_verb = open('ground_truths/utensils_used_for_truth.csv')
    utensil_verb_list = list(csv.reader(utensil_verb))

    utensil_foods = open('ground_truths/utensils_used_to_prepare_truth.csv')
    utensil_foods_r = csv.reader(utensil_foods)
    next(utensil_foods_r)
    utensil_foods_list = list(utensil_foods_r)

    add_to_dict(utensil_verb_list, utensil_foods_list, food_to_verbs)

    csv_data = []
    for key in food_to_verbs:
        csv_data.append({'Food': key,
                         'Verb': food_to_verbs[key]})

    write_to_csv(list(csv_data[0].keys()), csv_data, 'old_food_cooked_by_truth.csv')


if __name__ == '__main__':
    main()
