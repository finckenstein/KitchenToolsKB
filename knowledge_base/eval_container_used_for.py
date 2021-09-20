#!/usr/bin/env python3
import csv
import ast
from nltk.corpus import wordnet


def get_synonyms(verbs):
    synonyms = []
    for verb in verbs:
        synonyms.append(verb)
        for syn in wordnet.synsets(verb):
            for l in syn.lemmas():
                synonym = l.name()
                if synonym not in synonyms:
                    synonyms.append(synonym)
    print(len(synonyms))
    return synonyms


def get_true_verbs_for(container, ground_truths):
    print(container)
    for true_container_verbs in ground_truths:
        if true_container_verbs[0] == container:
            return true_container_verbs[1].split(", ")
    return None


def evaluate_container(predicted_container_verbs, true_verbs_for_container):
    tmp = {'Precision': None, 'Recall': None, 'True Positive': {}, 'False Positive': {}, 'False Negative': []}
    verbs_with_synonyms = get_synonyms(true_verbs_for_container)

    for verb_key in predicted_container_verbs:
        if verb_key in verbs_with_synonyms:
            tmp['True Positive'][verb_key] = predicted_container_verbs[verb_key]
        else:
            tmp['False Positive'][verb_key] = predicted_container_verbs[verb_key]

    for true_verbs in true_verbs_for_container:
        if true_verbs not in predicted_container_verbs:
            tmp['False Negative'].append(true_verbs)

    tmp['Precision'] = (len(tmp['True Positive']) / (len(tmp['True Positive']) + len(tmp['False Positive'])))
    tmp['Recall'] = (len(tmp['True Positive']) / (len(tmp['True Positive']) + len(tmp['False Negative'])))

    return tmp


def get_average(dic):
    summation = 0
    counter = 0
    for verb_key in dic:
        summation += dic[verb_key]
        counter += 1
    return summation / counter


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

        true_verbs_for_container = get_true_verbs_for(curr_container, ground_truth_list)
        assert true_verbs_for_container is not None, "container must be found"

        evaluation[curr_container] = evaluate_container(predicted_container_verbs, true_verbs_for_container)

        print("current container: ", curr_container)
        print("true verbs: ", true_verbs_for_container)
        print("correct verbs (true positive): ", list(evaluation[curr_container]['True Positive']))
        print("incorrect verbs (false positive): ", list(evaluation[curr_container]['False Positive']))
        print("missing verbs (false negative): ", evaluation[curr_container]['False Negative'])
        print("true positive: ", len(evaluation[curr_container]['True Positive']))
        print("average occurrence of true detected verbs: ", get_average(evaluation[curr_container]['True Positive']))
        print("false positive: ", len(evaluation[curr_container]['False Positive']))
        print("average occurrence of falsely detected verbs: ", get_average(evaluation[curr_container]['False Positive']))
        print("false negative: ", len(evaluation[curr_container]['False Negative']))
        print("precision: ", evaluation[curr_container]['Precision'])
        print("recall: ", evaluation[curr_container]['Recall'])
        print("\n\n")


if __name__ == '__main__':
    main()
