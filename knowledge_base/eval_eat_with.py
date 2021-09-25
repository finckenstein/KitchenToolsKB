#!/usr/bin/env python3
import csv
import ast


def get_prediction_for(recipe_to_get, predicted_values_list):
    for recipe in predicted_values_list:
        if predicted_values_list[recipe]['URL'] == recipe_to_get:
            return predicted_values_list[recipe]
    return None


def get_with_weights(eat_with):
    tmp = {}
    for row in eat_with:
        recipe = row[0]
        most_accurate_cutlery = ast.literal_eval(row[3])

        tmp[recipe] = {}
        tmp[recipe]['URL'] = row[1]
        tmp[recipe]['Most Occurring'] = []
        for most_occurring_dic in ast.literal_eval(row[4]):
            tmp[recipe]['Most Occurring'].append(most_occurring_dic['Cutlery'])

        tmp[recipe]['Cutlery'] = []
        accuracy = 0
        counter = 0

        for dic in most_accurate_cutlery:
            tmp[recipe]['Cutlery'].append(dic['Cutlery'])
            accuracy += dic['Accuracy']
            counter += 1

        tmp[recipe]['Cutlery Weight'] = accuracy / counter

        most_occurring = ast.literal_eval(row[4])
        for dic in most_occurring:
            for cutlery in tmp[recipe]['Cutlery']:
                if cutlery == dic['Cutlery']:
                    tmp[recipe]['Cutlery Weight'] += dic['Occurrence'] + dic['Average Accuracy']

        if len(ast.literal_eval(row[5])) == 0:
            tmp[recipe]['Last Seen'] = None
            last_seen = {'Cutlery': None, 'Accuracy': -1}
        else:
            tmp[recipe]['Last Seen'] = ast.literal_eval(row[5])['Cutlery']
            last_seen = ast.literal_eval(row[5])

        for cutlery in tmp[recipe]['Cutlery']:
            if cutlery == last_seen['Cutlery']:
                tmp[recipe]['Cutlery Weight'] += last_seen['Accuracy']

    return tmp


def print_average_weight(prediction_list):
    counter = 0
    for prediction in prediction_list:
        counter += prediction['Cutlery Weight']
    return counter / len(prediction_list)


# function filters out predictions like: ['person', 'fork'] to just ['fork']
# because it is not technically wrong since a person is needed to use a fork. It increases precision
def remove_unnecessary_hand(predictions_dic):
    tmp = []
    if 'person' in predictions_dic['Cutlery'] and len(predictions_dic['Cutlery']) == 2:
        for cutlery in predictions_dic['Cutlery']:
            if cutlery != 'person':
                tmp.append(cutlery)
    else:
        tmp = predictions_dic['Cutlery']
    return tmp


def update_missing_values(correct_cutlery_list, predicted_cutlery, fn_cutlery, prediction_dic, title):
    if len(correct_cutlery_list) > len(predicted_cutlery):
        missing = len(correct_cutlery_list) - len(predicted_cutlery)
        counter = 0
        for correct_cutlery in correct_cutlery_list:
            if correct_cutlery not in predicted_cutlery:
                fn_cutlery.append({'Title': title, 'URL': prediction_dic['URL'],
                                   'Missing_Cutlery': correct_cutlery})
                counter += 1
            if counter == missing:
                break


def evaluation(true_recipe, predicted_cutlery, prediction_dic, tp_cutlery, fp_cutlery, fn_cutlery):
    correct_cutlery_list = true_recipe[3].split(", ")
    assert len(correct_cutlery_list) > 0, "length of correct cutlery must be larger than 0"
    assert len(correct_cutlery_list) < 3, "length of correct cutlery must be smaller than 3"

    if 'none' in correct_cutlery_list:
        correct_cutlery_list = []

    for cutlery in predicted_cutlery:
        if cutlery in correct_cutlery_list:
            tp_cutlery.append(prediction_dic)
        else:
            fp_cutlery.append(prediction_dic)

    update_missing_values(correct_cutlery_list, predicted_cutlery, fn_cutlery, prediction_dic, true_recipe[0])


def print_all_types_of_cutlery(predictions, is_prediction):
    dic = {'fork': 0, 'spoon': 0, 'knife': 0, 'chopsticks': 0, 'person': 0,
           'fork_knife': 0, 'fork_spoon': 0, 'fork_chopsticks': 0, 'fork_person': 0,
           'spoon_knife': 0, 'spoon_chopsticks': 0, 'spoon_person': 0,
           'knife_chopsticks': 0, 'knife_person': 0,
           'chopsticks_person': 0,
           'total': 0}

    for recipe in predictions:
        if is_prediction:
            cutlery_list = predictions[recipe]['Cutlery']
        else:
            cutlery_list = recipe[3].split(", ")
        if len(cutlery_list) == 1:
            if 'fork' in cutlery_list:
                dic['fork'] += 1
            elif 'spoon' in cutlery_list:
                dic['spoon'] += 1
            elif 'knife' in cutlery_list:
                dic['knife'] += 1
            elif 'chopsticks' in cutlery_list:
                dic['chopsticks'] += 1
            elif 'person' in cutlery_list:
                dic['person'] += 1
        elif len(cutlery_list) == 2:
            if 'fork' in cutlery_list and 'knife' in cutlery_list:
                dic['fork_knife'] += 1
            elif 'fork' in cutlery_list and 'spoon' in cutlery_list:
                dic['fork_spoon'] += 1
            elif 'fork' in cutlery_list and 'chopsticks' in cutlery_list:
                dic['fork_chopsticks'] += 1
            elif 'fork' in cutlery_list and 'person' in cutlery_list:
                dic['fork_person'] += 1
            elif 'spoon' in cutlery_list and 'knife' in cutlery_list:
                dic['spoon_knife'] += 1
            elif 'spoon' in cutlery_list and 'chopsticks' in cutlery_list:
                dic['spoon_chopsticks'] += 1
            elif 'spoon' in cutlery_list and 'person' in cutlery_list:
                dic['spoon_person'] += 1
            elif 'knife' in cutlery_list and 'chopsticks' in cutlery_list:
                dic['knife_chopsticks'] += 1
            elif 'knife' in cutlery_list and 'person' in cutlery_list:
                dic['knife_person'] += 1
            elif 'knife' in cutlery_list and 'chopsticks' in cutlery_list:
                dic['chopsticks_person'] += 1
        dic['total'] += len(cutlery_list)

    dic = dict(sorted(dic.items(), key=lambda item: item[1], reverse=True))
    for key in dic:
        print(key, dic[key])


def main():
    extracted_knowledge = open('extracted_knowledge/eaten_with.csv')
    extracted_knowledge_reader = csv.reader(extracted_knowledge)
    next(extracted_knowledge_reader)
    extracted_knowledge_list = list(extracted_knowledge_reader)

    extraction_with_weights = get_with_weights(extracted_knowledge_list)
    sorted_ew = dict(sorted(extraction_with_weights.items(), key=lambda item: item[1]['Cutlery Weight'], reverse=True))
    print("All predicted recipes sorted by Weight:")
    for recipe in sorted_ew:
        print(recipe, sorted_ew[recipe], "\n")

    ground_truth = open('ground_truths/eat_with_truth.csv')
    ground_truth_reader = csv.reader(ground_truth)
    next(ground_truth_reader)
    ground_truth_list = list(ground_truth_reader)

    print("\nTotal number of cutlery in the ground truth:")
    print_all_types_of_cutlery(ground_truth_list, False)

    tp_hard_cutlery = []
    fp_hard_cutlery = []
    fn_hard_cutlery = []

    tp_medium_cutlery = []
    fp_medium_cutlery = []
    fn_medium_cutlery = []

    predictions_in_truth = {}

    for true_recipe in ground_truth_list:
        predictions_for_recipe = get_prediction_for(true_recipe[1], sorted_ew)
        assert predictions_for_recipe is not None, "recipes in ground truth should be present in predictions"

        evaluation(true_recipe, predictions_for_recipe['Cutlery'], predictions_for_recipe,
                   tp_hard_cutlery, fp_hard_cutlery, fn_hard_cutlery)
        evaluation(true_recipe, remove_unnecessary_hand(predictions_for_recipe), predictions_for_recipe,
                   tp_medium_cutlery, fp_medium_cutlery, fn_medium_cutlery)

        predictions_in_truth[true_recipe[0]] = predictions_for_recipe

    print("\nTotal number of cutlery in the predictions")
    print_all_types_of_cutlery(predictions_in_truth, True)

    hard_precision = (len(tp_hard_cutlery) / (len(tp_hard_cutlery) + len(fp_hard_cutlery)))
    hard_recall = (len(tp_hard_cutlery) / (len(tp_hard_cutlery) + len(fn_hard_cutlery)))
    print("\nprecision hard: ", hard_precision)
    print("recall hard: ", hard_recall)
    print("Average weight of true positive: ", print_average_weight(tp_hard_cutlery))
    print("Average weight of false positive: ", print_average_weight(fp_hard_cutlery))

    medium_precision = (len(tp_medium_cutlery) / (len(tp_medium_cutlery) + len(fp_medium_cutlery)))
    medium_recall = (len(tp_medium_cutlery) / (len(tp_medium_cutlery) + len(fn_medium_cutlery)))
    print("\nprecision medium: ", medium_precision)
    print("recall medium: ", medium_recall)
    print("Average weight of true positive: ", print_average_weight(tp_medium_cutlery))
    print("Average weight of false positive: ", print_average_weight(fp_medium_cutlery))


if __name__ == '__main__':
    main()
