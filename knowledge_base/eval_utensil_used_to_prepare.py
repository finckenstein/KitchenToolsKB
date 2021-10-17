#!/usr/bin/env python3
import csv
import ast


def get_true_foods_for(utensil, ground_truths):
    for true_utensil_foods in ground_truths:
        if true_utensil_foods[0] == utensil:
            return ast.literal_eval(true_utensil_foods[1])
    return None


def evaluate_utensil(predicted_utensil_food, true_foods_for_utensil):
    tmp = {'Precision': None, 'Recall': None, 'True Positive': {}, 'False Positive': {}, 'False Negative': []}

    for verb_key in predicted_utensil_food:
        if verb_key in true_foods_for_utensil:
            tmp['True Positive'][verb_key] = predicted_utensil_food[verb_key]
        else:
            tmp['False Positive'][verb_key] = predicted_utensil_food[verb_key]

    for true_verbs in true_foods_for_utensil:
        if true_verbs not in predicted_utensil_food:
            tmp['False Negative'].append(true_verbs)

    tmp['Precision'] = (len(tmp['True Positive']) / (len(tmp['True Positive']) + len(tmp['False Positive'])))
    tmp['Recall'] = (len(tmp['True Positive']) / (len(tmp['True Positive']) + len(tmp['False Negative'])))

    return tmp


def get_top_5(sorted_v):
    if len(sorted_v) == 0:
        return {}

    maxi = list(sorted_v.values())[0]
    counter = 0
    top_5_dict = {}

    for elem in sorted_v:
        score = sorted_v[elem]

        if maxi != score:
            counter += 1
            maxi = sorted_v[elem]

        if counter == 5:
            break
        else:
            top_5_dict[elem] = sorted_v[elem]
    return top_5_dict


def create_weights(extractions, index):
    predictions_with_weight = {}
    for row in extractions:
        curr_utensil = row[0]
        predictions_with_weight[curr_utensil] = {}

        all_verbs = ast.literal_eval(row[index])
        for verb in all_verbs:
            predictions_with_weight[curr_utensil][verb] = ((all_verbs[verb]['Is CV in Sync With Text'] /
                                                            all_verbs[verb]['Counter']) +
                                                           all_verbs[verb]['Is Tool Meant'] + (
                                                                   all_verbs[verb]['Accuracy'] / 100))
    return predictions_with_weight


def get_ingredients(utensil, ingredients):
    for k in ingredients:
        if k == utensil:
            return ingredients[k]


def print_results(predict, ingredients_dic):
    for utensil in predict:
        print("\n\ncurrent utensil: ", utensil)
        tmp_dict = predict[utensil]
        ingredient_dic = get_ingredients(utensil, ingredients_dic)

        sorted_concepts_by_weight = dict(sorted(tmp_dict.items(), key=lambda item: item[1], reverse=True))
        top_5_concepts = get_top_5(sorted_concepts_by_weight)
        print("Concepts: ", list(top_5_concepts))
        print("All Concepts: ", list(sorted_concepts_by_weight))

        sorted_ingredients_by_weight = dict(sorted(ingredient_dic.items(), key=lambda item: item[1], reverse=True))
        top_5_ingredients = get_top_5(sorted_ingredients_by_weight)
        # print("Ingredients: ", list(top_5_ingredients))
        # print("All Ingredients: ", list(sorted_ingredients_by_weight))


def get_average(verb_dic):
    if len(verb_dic) == 0:
        return 0
    summation = 0
    for verb in verb_dic:
        summation += verb_dic[verb]
    return summation / len(verb_dic)


def main():
    extracted_knowledge = open('extracted_knowledge/utensils_used_to_prepare.csv')
    extracted_knowledge_reader = csv.reader(extracted_knowledge)
    next(extracted_knowledge_reader)
    extracted_knowledge_list = list(extracted_knowledge_reader)

    ground_truth = open('ground_truths/utensils_used_to_prepare_truth.csv')
    ground_truth_list = list(csv.reader(ground_truth))

    predictions_with_weight = create_weights(extracted_knowledge_list, 4)
    ingredient_with_weight = create_weights(extracted_knowledge_list, 1)
    print_results(predictions_with_weight, ingredient_with_weight)

    evaluation = {}
    avg = {'Precision': 0, 'Recall': 0, 'TP': 0, 'FP': 0, 'Length': 0}
    total_predictions = 0
    total_truths = 0

    for utensil in predictions_with_weight:
        true_foods_for_utensil = get_true_foods_for(utensil, ground_truth_list)
        if true_foods_for_utensil is None:
            print("\n\nutensil not supported: ", utensil)
            continue

        evaluation[utensil] = evaluate_utensil(predictions_with_weight[utensil], true_foods_for_utensil)

        print("\n\ncurrent utensil: ", utensil)
        print("precision: ", evaluation[utensil]['Precision'] * 100, "%")
        print("recall: ", evaluation[utensil]['Recall'] * 100, "%")
        print("avg. weight of tp: ", get_average(evaluation[utensil]['True Positive']))
        print("avg. weight of fp: ", get_average(evaluation[utensil]['False Positive']))
        print("total predictions: ", len(predictions_with_weight[utensil]))
        print("total truths: ", len(true_foods_for_utensil))

        avg['Precision'] += evaluation[utensil]['Precision']
        avg['Recall'] += evaluation[utensil]['Recall']
        avg['TP'] += get_average(evaluation[utensil]['True Positive'])
        avg['FP'] += get_average(evaluation[utensil]['False Positive'])
        avg['Length'] += 1
        total_predictions += len(predictions_with_weight[utensil])
        total_truths += len(true_foods_for_utensil)

    print("\n\n")
    print("precision: ", avg['Precision']/avg['Length'] * 100)
    print("recall: ", avg['Recall'] / avg['Length'] * 100)
    print("TP: ", avg['TP'] / avg['Length'])
    print("FP: ", avg['FP'] / avg['Length'])
    print("total predictions: ", total_predictions)
    print(avg['Length'])
    print("Total truths: ", total_truths)


if __name__ == '__main__':
    main()
