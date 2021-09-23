#!/usr/bin/env python3
import csv
import ast


def write_to_csv(fields, data, filename):
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)


def main():
    food_verb = open('extracted_knowledge/food_cooked_by.csv')
    food_verb_r = csv.reader(food_verb)
    next(food_verb_r)
    food_verb_list = list(food_verb_r)

    elements = {}

    for food_verb_elem in food_verb_list:
        food = food_verb_elem[0]
        print(food)
        verbs = list(ast.literal_eval(food_verb_elem[1]))
        elements[food] = verbs

    csv_data = []
    for key in elements:
        csv_data.append({'Food': key,
                         'Verb': elements[key]})

    write_to_csv(list(csv_data[0].keys()), csv_data, 'old_food_cooked_by_truth.csv')


if __name__ == '__main__':
    main()
