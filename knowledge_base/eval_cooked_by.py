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


def get_csv_data(filename):
    relation = open(filename)
    relation_reader = csv.reader(relation)
    next(relation_reader)
    return list(relation_reader)


def get_predicted_verbs(food, predicted_food_verb_list):
    for row in predicted_food_verb_list:
        if row[0] == food:
            return ast.literal_eval(row[1])
    return None


def evaluate_predictions(pred_verb_list, true_verb_list, is_strict):
    tmp = {'Precision': 0, 'Recall': 0, 'True Positive': {}, 'False Positive': {}, 'False Negative': []}
    if is_strict:
        print("actual length: ", len(true_verb_list))
        verb_list_to_use = true_verb_list
    else:
        verb_list_to_use = get_synonyms(true_verb_list)
        print("length with synonyms: ", len(verb_list_to_use))
    print("length of list of predicted verbs: ", len(pred_verb_list))

    for verb in pred_verb_list:
        if verb in verb_list_to_use:
            tmp['True Positive'][verb] = pred_verb_list[verb]
        else:
            tmp['False Positive'][verb] = pred_verb_list[verb]

    for verb in verb_list_to_use:
        if verb not in pred_verb_list:
            tmp['False Negative'].append(verb)

    tmp['Precision'] = (len(tmp['True Positive'])/(len(tmp['True Positive']) + len(tmp['False Positive'])))
    tmp['Recall'] = (len(tmp['True Positive'])/(len(tmp['True Positive']) + len(tmp['False Negative'])))
    return tmp


def get_average(dic_verbs):
    if len(dic_verbs) == 0:
        return 0
    summation = 0
    for verb in dic_verbs:
        summation += dic_verbs[verb]

    return summation / len(dic_verbs)


def get_total_number_of_foods():
    all_foods_csv = get_csv_data('extracted_knowledge/foods_in_all_recipe.csv')
    all_food = []
    for food_concept in all_foods_csv:
        ingredients = ast.literal_eval(food_concept[2])
        for ingredient in ingredients:
            if ingredient not in all_food:
                all_food.append(ingredient)
    print("all food mentioned in all recipes: ", len(all_food))


def print_results(predicted_food_verb_list):
    for row in predicted_food_verb_list:
        print("food concept is: ", row[0])
        print(list(ast.literal_eval(row[1])))


def main():
    predicted_food_verb_list = get_csv_data('extracted_knowledge/food_cooked_by.csv')
    true_food_verb_list = get_csv_data('ground_truths/food_cooked_by_truth.csv')

    get_total_number_of_foods()

    # print_results(predicted_food_verb_list)

    strict_evaluation_food = {}
    lenient_evaluation_food = {}
    avg = {'Precision': 0, 'Recall': 0, 'TP': 0, 'FP': 0, 'Length': 0}

    for row in true_food_verb_list:
        current_food = row[0]
        true_verbs = row[1].split(", ")
        if len(true_verbs) == 1:
            continue
        predicted_verbs = get_predicted_verbs(current_food, predicted_food_verb_list)
        assert predicted_verbs is not None, "there should be predictions for food"

        print("\n\ncurrent food: ", current_food)

        strict_evaluation_food[current_food] = evaluate_predictions(predicted_verbs, true_verbs, True)
        lenient_evaluation_food[current_food] = evaluate_predictions(predicted_verbs, true_verbs, False)

        print("strict precision: ", strict_evaluation_food[current_food]['Precision'] * 100)
        print("strict recall: ", strict_evaluation_food[current_food]['Recall'] * 100)
        print("strict average weight of TP: ", get_average(strict_evaluation_food[current_food]['True Positive']))
        print("strict average weight of FP: ", get_average(strict_evaluation_food[current_food]['False Positive']))
        print("\n")
        print("lenient precision: ", lenient_evaluation_food[current_food]['Precision'] * 100)
        print("lenient recall: ", lenient_evaluation_food[current_food]['Recall'] * 100)
        print("lenient average weight of TP: ", get_average(lenient_evaluation_food[current_food]['True Positive']))
        print("lenient average weight of FP: ", get_average(lenient_evaluation_food[current_food]['False Positive']))

        avg['Precision'] += strict_evaluation_food[current_food]['Precision']
        avg['Recall'] += strict_evaluation_food[current_food]['Recall']
        avg['TP'] += get_average(strict_evaluation_food[current_food]['True Positive'])
        avg['FP'] += get_average(strict_evaluation_food[current_food]['False Positive'])
        avg['Length'] += 1

    print("Avg. Precision: ", (avg['Precision'] / avg['Length'])*100)
    print("Avg. Recall: ", (avg['Recall'] / avg['Length']) * 100)
    print("Avg. TP: ", avg['TP'] / avg['Length'])
    print("Avg. FP: ", avg['FP'] / avg['Length'])


    print(len(strict_evaluation_food))

if __name__ == '__main__':
    main()
