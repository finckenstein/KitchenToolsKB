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


def get_true_verbs_for(utensil, ground_truths):
    for true_utensil_verbs in ground_truths:
        if true_utensil_verbs[0] == utensil:
            return true_utensil_verbs[1].split(", ")
    return None


def evaluate_utensil(predicted_utensil_verbs, true_verbs_for_utensil):
    tmp = {'Precision': None, 'Recall': None, 'True Positive': {}, 'False Positive': {}, 'False Negative': []}
    verbs_with_synonyms = get_synonyms(true_verbs_for_utensil)

    for verb_key in predicted_utensil_verbs:
        if verb_key in verbs_with_synonyms:
            tmp['True Positive'][verb_key] = predicted_utensil_verbs[verb_key]
        else:
            tmp['False Positive'][verb_key] = predicted_utensil_verbs[verb_key]

    for true_verbs in true_verbs_for_utensil:
        if true_verbs not in predicted_utensil_verbs:
            tmp['False Negative'].append(true_verbs)

    tmp['Precision'] = (len(tmp['True Positive']) / (len(tmp['True Positive']) + len(tmp['False Positive'])))
    tmp['Recall'] = (len(tmp['True Positive']) / (len(tmp['True Positive']) + len(tmp['False Negative'])))

    return tmp


def main():
    extracted_knowledge = open('extracted_knowledge/utensils_used_for.csv')
    extracted_knowledge_reader = csv.reader(extracted_knowledge)
    next(extracted_knowledge_reader)
    extracted_knowledge_list = list(extracted_knowledge_reader)

    ground_truth = open('ground_truths/utensils_used_for_truth.csv')
    ground_truth_list = list(csv.reader(ground_truth))

    evaluation = {}

    for predicted_utensil_with_verbs in extracted_knowledge_list:
        curr_utensil = predicted_utensil_with_verbs[0]
        predicted_utensil_verbs = ast.literal_eval(predicted_utensil_with_verbs[1])

        true_verbs_for_utensil = get_true_verbs_for(curr_utensil, ground_truth_list)
        if true_verbs_for_utensil is None:
            print("utensil not supported: ", curr_utensil)
            continue

        evaluation[curr_utensil] = evaluate_utensil(predicted_utensil_verbs, true_verbs_for_utensil)

        print("current utensil: ", curr_utensil)
        print("true verbs: ", true_verbs_for_utensil)
        print("*** correct verbs (true positive): ", list(evaluation[curr_utensil]['True Positive']))
        print("*** incorrect verbs (false positive): ", list(evaluation[curr_utensil]['False Positive']))
        print("*** missing verbs (false negative): ", evaluation[curr_utensil]['False Negative'])
        print("true positive: ", len(evaluation[curr_utensil]['True Positive']))
        print("false positive: ", len(evaluation[curr_utensil]['False Positive']))
        print("false negative: ", len(evaluation[curr_utensil]['False Negative']))
        print("precision: ", evaluation[curr_utensil]['Precision'])
        print("recall: ", evaluation[curr_utensil]['Recall'])
        print("\n\n")


if __name__ == '__main__':
    main()
