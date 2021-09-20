#!/usr/bin/env python3
import csv
import ast


def get_true_verbs_for(container, ground_truths):
    print(container)
    for true_container_verbs in ground_truths:
        if true_container_verbs[0] == container:
            return true_container_verbs[1].split(", ")
    return None


def main():
    extracted_knowledge = open('extracted_knowledge/container_used_for.csv')
    extracted_knowledge_reader = csv.reader(extracted_knowledge)
    next(extracted_knowledge_reader)
    extracted_knowledge_list = list(extracted_knowledge_reader)

    ground_truth = open('ground_truths/container_used_for_truth.csv')
    ground_truth_list = list(csv.reader(ground_truth))

    evaluation = {}

    for container_verbs in extracted_knowledge_list:
        curr_container = container_verbs[0]
        predicted_container_verbs = ast.literal_eval(container_verbs[1])
        evaluation[curr_container] = {'Precision': None, 'Recall': None,
                                      'True Positive': {},
                                      'False Positive': {},
                                      'False Negative': []}

        true_verbs_for_container = get_true_verbs_for(curr_container, ground_truth_list)
        assert true_verbs_for_container is not None, "container must be found"

        for verb_key in predicted_container_verbs:
            if verb_key in true_verbs_for_container:
                evaluation[curr_container]['True Positive'][verb_key] = predicted_container_verbs[verb_key]
            else:
                evaluation[curr_container]['False Positive'][verb_key] = predicted_container_verbs[verb_key]

        for true_verbs in true_verbs_for_container:
            if true_verbs not in predicted_container_verbs:
                evaluation[curr_container]['False Negative'].append(true_verbs)

        tp = len(evaluation[curr_container]['True Positive'])
        fp = len(evaluation[curr_container]['False Positive'])
        fn = len(evaluation[curr_container]['False Negative'])
        print("current container: ", curr_container)
        print("true verbs: ", true_verbs_for_container)
        print("true positive: ", tp)
        print("false positive: ", fp)
        print("false positive list: ", list(evaluation[curr_container]['False Positive']))
        print("false negative: ", fn)
        print("false negative list: ", evaluation[curr_container]['False Negative'])
        evaluation[curr_container]['Precision'] = (tp / (tp + fp))
        evaluation[curr_container]['Recall'] = (tp / (tp + fn))
        print("precision: ", evaluation[curr_container]['Precision'])
        print("recall: ", evaluation[curr_container]['Recall'])
        print("\n\n")


if __name__ == '__main__':
    main()
