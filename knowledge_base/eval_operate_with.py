#!/usr/bin/env python3
import csv
import ast


def prediction_is_true(predicted_value, truth_values):
    predicted_tuple = ast.literal_eval(predicted_value)
    # print("predicted value: ", predicted_tuple)
    for true_val in truth_values:
        true_vals_as_list = true_val[0].split(", ")

        tool1 = true_vals_as_list[0]
        tool2 = true_vals_as_list[1]

        true_tup1 = tool1, tool2
        true_tup2 = tool2, tool1

        if predicted_tuple == true_tup1 or predicted_tuple == true_tup2:
            # print("ground truth: ", true_tup1, " is correctly predicted by: ", predicted_tuple)
            return True

    return False


def get_models_predictions(predictions, true_predictions):
    fp = []
    tp = []
    for prediction in predictions:
        if prediction_is_true(prediction[0], true_predictions):
            tp.append(prediction)
        else:
            fp.append(prediction)
    return tp, fp


def ground_truth_predicted(true_vals_as_list, predictions):
    tool1 = true_vals_as_list[0]
    tool2 = true_vals_as_list[1]

    true_tup1 = tool1, tool2
    true_tup2 = tool2, tool1

    for prediction in predictions:
        prediction_tuple = ast.literal_eval(prediction[0])
        if prediction_tuple == true_tup1 or prediction_tuple == true_tup2:
            return True
    return False


def get_models_failed_predictions(predictions, true_predictions):
    fn = []

    for true_value in true_predictions:
        if not ground_truth_predicted(true_value[0].split(", "), predictions):
            fn.append("("+true_value[0]+")")

    return fn


def get_edge_weights(list_of_predictions):
    video_occurrence = 0
    occurrence = 0
    for prediction in list_of_predictions:
        occurrence += int(prediction[1])
        video_occurrence += len(list(prediction[3]))
    return (video_occurrence/len(list_of_predictions)), (occurrence/len(list_of_predictions))


def make_dict(extracted_knowledge_list):
    tmp = {}
    for row in extracted_knowledge_list:
        print(type(row[3]))
        list_of_video = ast.literal_eval(row[3])
        occurrence = ast.literal_eval(row[1])
        tmp[row[0]] = {'Accuracy': row[2],
                       'Occurrence':  occurrence,
                       'Videos': list_of_video,
                       'Weight': ((2*(len(list_of_video)))+occurrence)}
    return tmp


def main():
    extracted_knowledge = open('extracted_knowledge/operate_with.csv')
    extracted_knowledge_reader = csv.reader(extracted_knowledge)
    next(extracted_knowledge_reader)
    extracted_knowledge_list = list(extracted_knowledge_reader)

    operate_with_in_dict = make_dict(extracted_knowledge_list)
    sorted_op = dict(sorted(operate_with_in_dict.items(), key=lambda item: item[1]['Weight'], reverse=True))
    print("sorted relations by significance.")
    for relation in sorted_op:
        print(relation, sorted_op[relation]['Weight'])

    ground_truth = open('ground_truths/operate_with_truth.csv')
    ground_truth_list = list(csv.reader(ground_truth))

    true_positive, false_positive = get_models_predictions(extracted_knowledge_list, ground_truth_list)
    print("\n\n")
    false_negative = get_models_failed_predictions(extracted_knowledge_list, ground_truth_list)

    print("true positives: ", len(true_positive), " i.e. correct predictions.")
    print("false positives: ", len(false_positive), " i.e. incorrect predictions.")
    print("false_negative: ", len(false_negative), "i.e. missing predictions")

    precision = (len(true_positive) / (len(true_positive) + len(false_positive)))
    recall = (len(true_positive) / (len(true_positive) + len(false_negative)))

    print("precision: ", precision)
    print("recall: ", recall)

    tp_edge_weights = get_edge_weights(true_positive)
    fp_edge_weights = get_edge_weights(false_positive)

    print("edge weights of true positive predictions. Video Occurrence: ", tp_edge_weights[0], ". Total Occurrence: ", tp_edge_weights[1])
    print("edge weights of false positive predictions:  Video Occurrence: ", fp_edge_weights[0], ". Total Occurrence: ", fp_edge_weights[1])


if __name__ == '__main__':
    main()
