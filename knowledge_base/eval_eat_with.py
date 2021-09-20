#!/usr/bin/env python3
import csv
import ast


def get_prediction_for(recipe_to_get, predicted_values_list):
    for predicted_val_recipe in predicted_values_list:
        if predicted_val_recipe[1] == recipe_to_get:
            return predicted_val_recipe
    return None


# function filters out predictions like: ['person', 'fork'] to just ['fork']
# because it is not technically wrong since a person is needed to use a fork. It increases precision
def remove_unnecessary_hand(predictions_list_dic):
    if len(predictions_list_dic) == 1 and predictions_list_dic[0]['Cutlery'] == 'person':
        return predictions_list_dic

    tmp = []
    for dic in predictions_list_dic:
        if dic['Cutlery'] != 'person':
            tmp.append(dic)
    return tmp


def update_tp_and_fp(tp_cutlery, fp_cutlery, predictions_for_recipe, correct_cutlery_list):
    all_predicted_cutlery = []
    predicted_cutlery_list = remove_unnecessary_hand(ast.literal_eval(predictions_for_recipe[3]))

    for predicted_cutlery in predicted_cutlery_list:
        if predicted_cutlery['Cutlery'] in correct_cutlery_list:
            tp_cutlery.append({'Title': predictions_for_recipe[0], 'URL': predictions_for_recipe[1],
                               'Video_ID': predictions_for_recipe[2],
                               'Correct_Cutlery': correct_cutlery_list, 'Predicted_Cutlery': predicted_cutlery,
                               'Most Detected Cutlery': predictions_for_recipe[4],
                               'Last Detected Cutlery': predictions_for_recipe[5]})
        else:
            fp_cutlery.append({'Title': predictions_for_recipe[0], 'URL': predictions_for_recipe[1],
                               'Video_ID': predictions_for_recipe[2],
                               'Correct_Cutlery': correct_cutlery_list, 'Predicted_Cutlery': predicted_cutlery,
                               'Most Detected Cutlery': predictions_for_recipe[4],
                               'Last Detected Cutlery': predictions_for_recipe[5]})
        all_predicted_cutlery.append(predicted_cutlery['Cutlery'])

    if len(all_predicted_cutlery) == 1 and all_predicted_cutlery[0] is None:
        all_predicted_cutlery = []
    return all_predicted_cutlery


def update_fn(fn_cutlery, correct_cutlery_list, all_predicted_cutlery, predictions_for_recipe):
    if len(correct_cutlery_list) > len(all_predicted_cutlery):
        missing = len(correct_cutlery_list) - len(all_predicted_cutlery)
        counter = 0
        for correct_cutlery in correct_cutlery_list:
            if correct_cutlery not in all_predicted_cutlery:
                fn_cutlery.append({'Title': predictions_for_recipe[0], 'URL': predictions_for_recipe[1],
                                   'Video_ID': predictions_for_recipe[2],
                                   'Missing_Cutlery': correct_cutlery})
                counter += 1
            if counter == missing:
                break


def update_values_for_cutlery(true_recipe, predictions_for_recipe, tp_cutlery, fp_cutlery, fn_cutlery):
    correct_cutlery_list = true_recipe[3].split(", ")
    assert len(correct_cutlery_list) > 0, "length of correct cutlery must be larger than 0"

    if 'none' in correct_cutlery_list and len(correct_cutlery_list) == 1:
        correct_cutlery_list = []

    print("current recipe URL: ", true_recipe[1])
    print("true cutlery: ", correct_cutlery_list)
    all_predicted_cutlery = update_tp_and_fp(tp_cutlery, fp_cutlery, predictions_for_recipe, correct_cutlery_list)
    print("predicted cutlery: ", all_predicted_cutlery)
    update_fn(fn_cutlery, correct_cutlery_list, all_predicted_cutlery, predictions_for_recipe)

    print("true positive cutlery: ", len(tp_cutlery))
    print("false positive cutlery: ", len(fp_cutlery))
    print("false negative cutlery: ", len(fn_cutlery))


def update_values_for_dishware(true_recipe, predictions_for_recipe, tp_dishware, fp_dishware, fn_dishware):
    true_dishware = true_recipe[4]
    predicted_dishware = ast.literal_eval(predictions_for_recipe[7])
    print("\n true dishware: ", true_dishware)
    print("predicted dishware: ", predicted_dishware)
    if predicted_dishware['Container'] == true_dishware or (predicted_dishware['Container'] is None and true_dishware == 'none'):
        tp_dishware.append({'Title': predictions_for_recipe[0], 'URL': predictions_for_recipe[1],
                            'Video_ID': predictions_for_recipe[2],
                            'Predicted_Container': predicted_dishware})
    elif predicted_dishware['Container'] != true_dishware:
        fp_dishware.append({'Title': predictions_for_recipe[0], 'URL': predictions_for_recipe[1],
                            'Video_ID': predictions_for_recipe[2],
                            'Predicted_Container': predicted_dishware})
    elif predicted_dishware['Container'] is None and true_dishware != 'none':
        fn_dishware.append({'Title': predictions_for_recipe[0], 'URL': predictions_for_recipe[1],
                            'Video_ID': predictions_for_recipe[2],
                            'Predicted_Container': true_dishware})

    print("true positive dishware: ", len(tp_dishware))
    print("false positive dishware: ", len(fp_dishware))
    print("false negative dishware: ", len(fn_dishware), "\n\n")


def get_totals(ground_truth_list, extracted_knowledge_list):
    truth_counter = 0
    predictions_counter = 0
    for truth in ground_truth_list:
        truth_counter += len(truth[3].split(", "))
        predictions_for_recipe = get_prediction_for(truth[1], extracted_knowledge_list)
        predicted_cutlery_list = remove_unnecessary_hand(ast.literal_eval(predictions_for_recipe[3]))
        predictions_counter += len(predicted_cutlery_list)
    return truth_counter, predictions_counter


def main():
    extracted_knowledge = open('extracted_knowledge/eaten_with.csv')
    extracted_knowledge_reader = csv.reader(extracted_knowledge)
    next(extracted_knowledge_reader)
    extracted_knowledge_list = list(extracted_knowledge_reader)

    ground_truth = open('ground_truths/eat_with_truth.csv')
    ground_truth_reader = csv.reader(ground_truth)
    next(ground_truth_reader)
    ground_truth_list = list(ground_truth_reader)

    tp_cutlery = []
    fp_cutlery = []
    fn_cutlery = []

    tp_dishware = []
    fp_dishware = []
    fn_dishware = []

    tp_recipe = []
    fp_recipe = []

    for true_recipe in ground_truth_list:
        predictions_for_recipe = get_prediction_for(true_recipe[1], extracted_knowledge_list)
        assert predictions_for_recipe is not None, "recipes in ground truth should be present in predictions"

        update_values_for_cutlery(true_recipe, predictions_for_recipe, tp_cutlery, fp_cutlery, fn_cutlery)
        update_values_for_dishware(true_recipe, predictions_for_recipe, tp_dishware, fp_dishware, fn_dishware)

    total_truths, total_pred = get_totals(ground_truth_list, extracted_knowledge_list)
    print("total predictions: ", total_pred)
    print("total truths: ", total_truths)

    cutlery_precision = (len(tp_cutlery) / (len(tp_cutlery) + len(fp_cutlery)))
    cutlery_recall = (len(tp_cutlery) / (len(tp_cutlery) + len(fn_cutlery)))
    print("cutlery precision: ", cutlery_precision)
    print("cutlery recall: ", cutlery_recall)

    dishware_precision = (len(tp_dishware) / (len(tp_dishware) + len(fp_dishware)))
    dishware_recall = (len(tp_dishware) / (len(tp_dishware) + len(fn_dishware)))
    print("dishware precision: ", dishware_precision)
    print("dishware recall: ", dishware_recall)


if __name__ == '__main__':
    main()
