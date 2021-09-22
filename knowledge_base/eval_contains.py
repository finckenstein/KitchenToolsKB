#!/usr/bin/env python3
import csv
import ast


def get_truth_concepts_for(curr_container, ground_truth_list):
    for truth_container in ground_truth_list:
        if curr_container == truth_container[0]:
            return ast.literal_eval(truth_container[1])
    return None


def evaluate_utensil(predicted_concepts, truthful_concepts):
    tmp = {'Precision': 0, 'Recall': 0, 'True Positive': {}, 'False Positive': {}, 'False Negative': []}

    for predict_concept_key in predicted_concepts:
        if predict_concept_key in truthful_concepts:
            tmp['True Positive'][predict_concept_key] = predicted_concepts[predict_concept_key]
        else:
            tmp['False Positive'][predict_concept_key] = predicted_concepts[predict_concept_key]

    for true_concepts in truthful_concepts:
        if true_concepts not in predicted_concepts:
            tmp['False Negative'].append(true_concepts)

    tmp['Precision'] = (len(tmp['True Positive']) / (len(tmp['True Positive']) + len(tmp['False Positive'])))
    tmp['Recall'] = (len(tmp['True Positive']) / (len(tmp['True Positive']) + len(tmp['False Negative'])))

    return tmp


def main():
    extracted_knowledge = open('extracted_knowledge/contains.csv')
    extracted_knowledge_reader = csv.reader(extracted_knowledge)
    next(extracted_knowledge_reader)
    extracted_knowledge_list = list(extracted_knowledge_reader)

    ground_truth = open('ground_truths/contains_truth.csv')
    ground_truth_list = list(csv.reader(ground_truth))

    evaluation = {}

    for predicted_container_with_food in extracted_knowledge_list:
        curr_container = predicted_container_with_food[0]
        assert curr_container not in evaluation, "container in extracted knowledge should be unique."

        predicted_concepts = ast.literal_eval(predicted_container_with_food[4])
        truthful_concepts = get_truth_concepts_for(curr_container, ground_truth_list)
        if truthful_concepts is None:
            print(curr_container, " not supported.\n\n")
            continue

        evaluation[curr_container] = evaluate_utensil(predicted_concepts, truthful_concepts)

        print("current container: ", curr_container)
        print("true concepts: ", truthful_concepts)
        print("*** correct concepts (true positive): ", list(evaluation[curr_container]['True Positive']))
        print("*** incorrect concepts (false positive): ", list(evaluation[curr_container]['False Positive']))
        print("*** missing concepts (false negative): ", evaluation[curr_container]['False Negative'])
        print("true positive: ", len(evaluation[curr_container]['True Positive']))
        print("false positive: ", len(evaluation[curr_container]['False Positive']))
        print("false negative: ", len(evaluation[curr_container]['False Negative']))
        print("precision: ", evaluation[curr_container]['Precision'])
        print("recall: ", evaluation[curr_container]['Recall'])
        print("\n\n")


if __name__ == '__main__':
    main()
