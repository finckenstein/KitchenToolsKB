#!/usr/bin/env python3
import csv
import ast


def get_csv_data(filename):
    relation = open(filename)
    relation_reader = csv.reader(relation)
    next(relation_reader)
    return list(relation_reader)


def get_verbs_associated(current_marker, list_to_iterate):
    for marker_row in list_to_iterate:
        if marker_row[0] == current_marker:
            return list(ast.literal_eval(marker_row[1]))
    return None


def match_verbs(verb_list_1, verb_list_2):
    number_in_common = 0
    not_in_common = 0
    for verb1 in verb_list_1:
        if verb1 in verb_list_2:
            number_in_common += 1
        else:
            not_in_common += 1
    return number_in_common, not_in_common


def main():
    food_verb_list = get_csv_data('extracted_knowledge/food_cooked_by.csv')
    utensil_food_list = get_csv_data('extracted_knowledge/utensils_used_to_prepare.csv')
    utensil_verb_list = get_csv_data('extracted_knowledge/utensils_used_for.csv')

    transitivity_metric = {}

    for utensil_food in utensil_food_list:
        current_utensil = utensil_food[0]
        utensil_direct_foods_list = list(ast.literal_eval(utensil_food[4]))
        utensil_direct_verb_list = get_verbs_associated(current_utensil, utensil_verb_list)
        transitivity_metric[current_utensil] = {}

        for food in utensil_direct_foods_list:
            food_direct_verb_list = get_verbs_associated(food, food_verb_list)
            assert food_direct_verb_list is not None, "food needs to be found"
            verbs_in_common, verbs_not_in_common = match_verbs(utensil_direct_verb_list, food_direct_verb_list)
            assert (verbs_in_common + verbs_not_in_common) == len(utensil_direct_verb_list)

            transitivity_metric[current_utensil][food] = {'Verbs in Common': verbs_in_common,
                                                          'Verbs not in Common': verbs_not_in_common,
                                                          'Total verbs for tool': len(utensil_direct_verb_list),
                                                          'Total verbs for food': len(food_direct_verb_list)}

    for tool in transitivity_metric:
        for food in transitivity_metric[tool]:
            print('tool: ', tool, ' food: ', food)
            accuracy = (transitivity_metric[tool][food]['Verbs in Common']/
                        transitivity_metric[tool][food]['Total verbs for tool'])
            print('% of verbs in common: ', accuracy)


if __name__ == '__main__':
    main()
