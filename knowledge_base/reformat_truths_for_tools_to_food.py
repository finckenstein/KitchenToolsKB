#!/usr/bin/env python3
import csv


def write_to_csv(fields, data, filename):
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)


def main():
    foods = open('ground_truths/tmp_food_to_tools.csv')
    extracted_knowledge_reader = csv.reader(foods)
    next(extracted_knowledge_reader)
    foods_to_tools = list(extracted_knowledge_reader)

    container_to_food = {}
    utensil_to_food = {}

    for food in foods_to_tools:
        current_food = food[0]
        list_of_containers = food[1].split(", ")
        list_of_utensils = food[2].split(", ")

        for container in list_of_containers:
            if container in container_to_food:
                container_to_food[container].append(current_food)
            else:
                container_to_food[container] = [current_food]

        if list_of_utensils[0] == 'none':
            continue
        for utensil in list_of_utensils:
            if utensil in utensil_to_food:
                utensil_to_food[utensil].append(current_food)
            else:
                utensil_to_food[utensil] = [current_food]

    container_list_csv = []
    for container in container_to_food:
        container_list_csv.append({'Container': container,
                                   'Associated Food': container_to_food[container]})

    utensil_list_csv = []
    for utensil in utensil_to_food:
        utensil_list_csv.append({'Utensil': utensil,
                                 'Associated Food': utensil_to_food[utensil]})

    write_to_csv(list(container_list_csv[0].keys()), container_list_csv, 'old_contains_truth.csv')
    write_to_csv(list(utensil_list_csv[0].keys()), utensil_list_csv, 'old_utensils_used_to_prepare_truth.csv')


if __name__ == '__main__':
    main()
