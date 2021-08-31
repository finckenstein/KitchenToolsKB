#!/usr/bin/env python
# coding: utf-8

# '%pip install -U --pre tensorflow=="2.*"'
# '%pip install tf_slim'
# '%pip install pycocotools'

# if "models" in pathlib.Path.cwd().parts:
#     while "models" in pathlib.Path.cwd().parts:
#         os.chdir('..')

# '%cd models/research/\nprotoc object_detection/protos/*.proto --python_out=.'
# '%cd models/research\npip install .'
import math

import numpy as np
import tensorflow as tf

import pathlib
import cv2
import os

from tensorflow_object_detection_utils import ops as utils_ops
from tensorflow_object_detection_utils import label_map_util
from tensorflow_object_detection_utils import visualization_utils as vis_util


def load_model(model_path):
    model_dir = pathlib.Path(model_path) / "saved_model"
    model = tf.saved_model.load(str(model_dir))
    return model


def run_inference_for_single_image(model, image):
    image = np.asarray(image)
    # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
    input_tensor = tf.convert_to_tensor(image)
    # The model expects a batch of images, so add an axis with `tf.newaxis`.
    input_tensor = input_tensor[tf.newaxis, ...]

    # Run inference
    model_fn = model.signatures['serving_default']
    output_dict = model_fn(input_tensor)

    print(output_dict['detection_classes'])

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


def make_inference(capture, model, fr):
    frame_id = capture.get(1)  # current frame number
    ret, image_np = capture.read()
    if not ret:
        return False

    if frame_id % math.floor(fr) == 0:
        # Actual detection.
        output_dict = run_inference_for_single_image(model, image_np)
        # Visualization of the results of a detection.
        vis_util.visualize_boxes_and_labels_on_image_array(
            image_np,
            output_dict['detection_boxes'],
            output_dict['detection_classes'],
            output_dict['detection_scores'],
            category_index,
            instance_masks=output_dict.get('detection_masks_reframed', None),
            use_normalized_coordinates=True,
            line_thickness=8,
            min_score_thresh=0.5)

        cv2.imshow('object_detection', cv2.resize(image_np, (640, 640)))

        while True:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
    return True


def get_video_id(f):
    file_parts_array = f.split('_')
    tmp_id = ''

    for file_part in file_parts_array:
        if '(' in file_part:
            start_index = file_part.index('(') + 1
            while not file_part[start_index] == ')':
                tmp_id += file_part[start_index]
                start_index += 1
    return int(tmp_id)


if __name__ == '__main__':
    utils_ops.tf = tf.compat.v1
    tf.gfile = tf.io.gfile

    PATH_TO_LABELS = 'CV_Kitchen_Tools/kitchen_tools_label_map.pbtxt'
    category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)

    # model_name = 'CV_COCO/ssd_resnet50_v1_fpn_640x640_coco17_tpu-8/'
    model_name = 'CV_Kitchen_Tools/CV_KT_detection_model_B8'
    detection_model = load_model(model_name)

    print("\n\n\nHELLO: ", detection_model.signatures['serving_default'].inputs, "\n")

    PATH_TO_USB_VIDEOS = "/media/leander/1F1C-606E/videos/"
    files = os.listdir(PATH_TO_USB_VIDEOS)
    i = 0

    for file in files:
        if '.mp4' in file and get_video_id(file) == 15:
            cap = cv2.VideoCapture(PATH_TO_USB_VIDEOS + file)
            frame_rate = cap.get(5)

            while cap.isOpened():
                if not make_inference(cap, detection_model, frame_rate):
                    break

            cap.release()
            cv2.destroyAllWindows()
            i += 1
