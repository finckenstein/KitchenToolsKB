#!/usr/bin/env python3
import csv
import ast


def main():
    extracted_knowledge = open('extracted_knowledge/contains.csv')
    extracted_knowledge_reader = csv.reader(extracted_knowledge)
    next(extracted_knowledge_reader)
    extracted_knowledge_list = list(extracted_knowledge_reader)

    # ground_truth = open('ground_truths/utensils_used_for_truth.csv')
    # ground_truth_list = list(csv.reader(ground_truth))

    # evaluation = {}

    for predicted_container_with_food in extracted_knowledge_list:
        curr_container = predicted_container_with_food[0]
        print("current container: ", curr_container)
        concepts = ast.literal_eval(predicted_container_with_food[4])
        for concept in concepts:
            print(concept)
        print("\n\n")


if __name__ == '__main__':
    main()
