#!/usr/bin/env python3
import math

import numpy as np
import tensorflow as tf
import cv2
import pathlib

from computer_vision.tensorflow_object_detection_utils import ops as utils_ops
from computer_vision.tensorflow_object_detection_utils import visualization_utils as vis_util
import utility.paths as path


def load_model(model_path):
    model_dir = pathlib.Path(model_path) / "saved_model"
    model = tf.saved_model.load(str(model_dir))
    return model


# This function is taken from the object_detection_tutorial.py, from the TensorFlow object detection API
def run_inference_for_single_image(model, image):
    image = np.asarray(image)
    # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
    input_tensor = tf.convert_to_tensor(image)
    # The model expects a batch of images, so add an axis with `tf.newaxis`.
    input_tensor = input_tensor[tf.newaxis, ...]

    # Run inference
    model_fn = model.signatures['serving_default']
    output_dict = model_fn(input_tensor)

    # print(output_dict['detection_classes'])

    # All outputs are batches tensors.
    # Convert to numpy arrays, and take index [0] to remove the batch dimension.
    # We're only interested in the first num_detections.
    num_detections = int(output_dict.pop('num_detections'))
    output_dict = {key: value[0, :num_detections].numpy()
                   for key, value in output_dict.items()}
    output_dict['num_detections'] = num_detections

    # detection_classes should be ints.
    output_dict['detection_classes'] = output_dict['detection_classes'].astype(np.int64)

    # Handle models with masks:
    if 'detection_masks' in output_dict:
        # Reframe the the bbox mask to the image size.
        detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
            output_dict['detection_masks'], output_dict['detection_boxes'],
            image.shape[0], image.shape[1])
        detection_masks_reframed = tf.cast(detection_masks_reframed > 0.5,
                                           tf.uint8)
        output_dict['detection_masks_reframed'] = detection_masks_reframed.numpy()

    return output_dict


def show_image(image_np, output_dic, category_index, accuracy):
    vis_util.visualize_boxes_and_labels_on_image(
        image_np,
        output_dic['detection_boxes'],
        output_dic['detection_classes'],
        output_dic['detection_scores'],
        category_index,
        instance_masks=output_dic.get('detection_masks_reframed', None),
        use_normalized_coordinates=True,
        line_thickness=4,
        min_score_thresh=accuracy)

    cv2.imshow('object_detection', cv2.resize(image_np, (640, 640)))

    while True:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break


def make_inference(image_np, output_dict, category_index, accuracy):
    return vis_util.get_coordinates_for_tool_found(
        image_np,
        output_dict['detection_boxes'],
        output_dict['detection_classes'],
        output_dict['detection_scores'],
        category_index,
        instance_masks=output_dict.get('detection_masks_reframed', None),
        use_normalized_coordinates=True,
        line_thickness=4,
        min_score_thresh=accuracy)


def make_inference_for_ow(capture, model, fr, category_index, accuracy, get_what):
    frame_id = capture.get(get_what)  # current frame number
    ret, image_np = capture.read()
    if not ret:
        return False, []

    if frame_id % math.floor(fr) == 0:
        # Actual detection.
        output_dict = run_inference_for_single_image(model, image_np)

        # Visualization of the results of a detection.
        show_image(image_np, output_dict, category_index, accuracy)

        return True, make_inference(image_np, output_dict, category_index, accuracy)
    return True, []


def make_inference_for_ew(capture, model, fr, category_index, accuracy, get_what, video_length):
    frame_id = capture.get(get_what)  # current frame number
    ret, image_np = capture.read()
    print("we are at seconds: ", capture.get(cv2.CAP_PROP_POS_MSEC)/1000)
    if not ret or capture.get(cv2.CAP_PROP_POS_MSEC)/1000 >= video_length - 3:
        return False, []

    if frame_id % math.floor(fr) == 0:
        # Actual detection.
        output_dict = run_inference_for_single_image(model, image_np)

        # Visualization of the results of a detection.
        # show_image(image_np, output_dict, category_index, accuracy)

        return True, make_inference(image_np, output_dict, category_index, accuracy)

    return True, []


def make_inference_for_vtt(model, timestamp, category_index, accuracy):
    utils_ops.tf = tf.compat.v1
    tf.gfile = tf.io.gfile

    cap = cv2.VideoCapture(path.PATH_TO_VIDEOS)
    cap.set(cv2.CAP_PROP_POS_MSEC, timestamp*1000)

    while cap.isOpened():
        ret, image_np = cap.read()
        if not ret:
            # print("\n[make_inference] returning FALSE\n")
            return None

        # Actual detection.
        output_dict = run_inference_for_single_image(model, image_np)

        # Visualization of the results of a detection.
        # show_image(image_np, output_dict, category_index, accuracy)

        # print("\nCAP RELEASED AND DESTROYED\n")
        found_tools = make_inference(image_np, output_dict, category_index, accuracy)
        cap.release()
        cv2.destroyAllWindows()

        return True, found_tools

    return True, []
