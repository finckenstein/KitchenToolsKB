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
    # print(len(synonyms))
    return synonyms


def get_true_verbs_for(container, ground_truths):
    # print(container)
    for true_container_verbs in ground_truths:
        if true_container_verbs[0] == container:
            return true_container_verbs[1].split(", ")
    return None


def evaluate_container(predicted_container_verbs, true_verbs_for_container, is_strict):
    tmp = {'Precision': None, 'Recall': None, 'True Positive': {}, 'False Positive': {}, 'False Negative': []}

    if is_strict:
        verbs_to_use = true_verbs_for_container
    else:
        verbs_to_use = get_synonyms(true_verbs_for_container)

    for verb_key in predicted_container_verbs:
        if verb_key in verbs_to_use:
            tmp['True Positive'][verb_key] = predicted_container_verbs[verb_key]
        else:
            tmp['False Positive'][verb_key] = predicted_container_verbs[verb_key]

    for true_verbs in verbs_to_use:
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


def print_most_significant_verbs(predictions):
    for prediction in predictions:
        print("\n\n")
        print("container: ", prediction[0])
        top_5_verbs = ast.literal_eval(prediction[2])
        print("top 5 verbs: ", list(top_5_verbs.keys()))
        top_5_antonyms = ast.literal_eval(prediction[4])
        print("top 5 antonyms: ", list(top_5_antonyms.keys()))


def get_average_of_two(dic1, dic2):
    summation = 0
    for verb_key in dic1:
        summation += dic1[verb_key]

    for verb_key in dic2:
        summation += dic2[verb_key]

    return summation / (len(dic1) + len(dic2))


def print_average(eval_dic):
    avg = {'Precision': 0, 'Recall': 0, 'Length': 0}
    for container in eval_dic:
        avg['Precision'] += eval_dic[container]['Precision']
        avg['Recall'] += eval_dic[container]['Recall']
        avg['Length'] += 1

    for key in avg:
        print(key, (avg[key] / avg['Length']))


def main():
    extracted_knowledge = open('extracted_knowledge/container_used_for.csv')
    extracted_knowledge_reader = csv.reader(extracted_knowledge)
    next(extracted_knowledge_reader)
    extracted_knowledge_list = list(extracted_knowledge_reader)

    print_most_significant_verbs(extracted_knowledge_list)

    ground_truth = open('ground_truths/container_used_for_truth.csv')
    ground_truth_list = list(csv.reader(ground_truth))

    strict_eval = {}
    lenient_eval = {}
    avg = {'Precision': 0, 'Recall': 0, 'Avg_TP_weight': 0, 'Avg_FP_weight': 0, 'Length': 0}

    for container_verbs in extracted_knowledge_list:
        curr_container = container_verbs[0]
        predicted_container_verbs = ast.literal_eval(container_verbs[1])

        true_verbs_for_container = get_true_verbs_for(curr_container, ground_truth_list)
        assert true_verbs_for_container is not None, "container must be found"

        strict_eval[curr_container] = evaluate_container(predicted_container_verbs, true_verbs_for_container, True)
        lenient_eval[curr_container] = evaluate_container(predicted_container_verbs, true_verbs_for_container, False)

        print("\n\n")
        print("current container: ", curr_container)
        print("strict precision: ", strict_eval[curr_container]['Precision'] * 100)
        print("strict recall: ", strict_eval[curr_container]['Recall'] * 100)

        print("lenient precision: ", lenient_eval[curr_container]['Precision'] * 100)
        print("lenient recall: ", lenient_eval[curr_container]['Recall'] * 100)
        avg_precision = ((strict_eval[curr_container]['Precision'] + lenient_eval[curr_container][
            'Precision']) / 2) * 100
        print("average precision: ", avg_precision)
        avg_recall = ((strict_eval[curr_container]['Recall'] + lenient_eval[curr_container]['Recall']) / 2) * 100
        print("average recall: ", avg_recall)
        avg_weight_tp = get_average_of_two(lenient_eval[curr_container]['True Positive'],
                                           strict_eval[curr_container]['True Positive'])
        print("average weight of true positive: ", avg_weight_tp)
        avg_weight_fp = get_average_of_two(lenient_eval[curr_container]['False Positive'],
                                           strict_eval[curr_container]['False Positive'])
        print("average weight of false positive: ", avg_weight_fp)
        avg['Precision'] += avg_precision
        avg['Recall'] += avg_recall
        avg['Avg_TP_weight'] += avg_weight_tp
        avg['Avg_FP_weight'] += avg_weight_fp
        avg['Length'] += 1

    print("\n\naverage for strict:")
    print_average(strict_eval)
    print("\n\naverage for lenient:")
    print_average(lenient_eval)
    print("\n\naverage for average:")
    for k in avg:
        print(k, avg[k]/avg['Length'])


if __name__ == '__main__':
    main()
