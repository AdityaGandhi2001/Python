import cv2
import numpy as np
import time
import os
from elements.yolo import OBJ_DETECTION
from paddleocr import PaddleOCR
import re

input_folder = "/Users/vinayakgandhi/Downloads/yolov5-master 3/100"
output_folder = "/Users/vinayakgandhi/Downloads/yolov5-master 3/100_results"
Object_classes = [
    "15.0", "15.1", "15.2", "15.3", "15.4", "15.5", "15.6", "15.7", "15.8", "15.9",
    "16.0", "16.1", "16.2", "16.3", "16.4", "16.5", "16.6", "16.7", "16.8", "16.9",
    "17.0", "17.1", "17.2", "17.3", "17.4", "17.5", "17.6", "17.7", "18.9"
]

Object_colors = list(np.random.rand(11, 11) * 255)
Object_detector = OBJ_DETECTION('best_classOrientation.pt', Object_classes)
regex = re.compile(r'^\d+\.\d$')
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

ocr = PaddleOCR(use_angle_cls=True, lang='en')
files = os.listdir(input_folder)
# total_model_time = 0
# total_ocr_time = 0
# ocr_count = 0

for file in files:
    print(file)
    if file == ".DS_Store":
        continue
    frame = cv2.imread(os.path.join(input_folder, file))
    print(frame.shape)
    # frame = cv2.resize(frame, (640, 1280))  # Resize to match YOLOv7 input size

    # model_start_time = time.time()

    objs = Object_detector.detect(frame)
    print(objs)

    model_end_time = time.time()
    # model_inference_time = (model_end_time - model_start_time)

    labelx = []
    labely = []
    character = []

    for obj in objs:
        if obj['score'] > 0.6:
            label = obj['label']  # Adjust to 'class' for YOLOv5 output
            score = obj['score']
            [(xmin, ymin), (xmax, ymax)] = obj['bbox']
            character.append(label)
            labelx.append(xmin)
            labely.append(ymin)
            color = (255, 0, 0)
            # ocr_start_time = time.time()

            # cropped_img = frame[ymin:ymax, xmin:xmax]
            # roi = frame[ymin:ymax, xmin:xmax]
            # blurred_image = frame.copy()
            # blurred_image = cv2.blur(blurred_image, (25, 25))
            # blurred_image[ymin:ymax, xmin:xmax] = roi
            # cv2.imshow("blured image", blurred_image)
            # cv2.waitKey(0)
            # output_filename = os.path.join(output_folder, file)
            # cv2.imwrite(output_filename, frame)
            ocr_result = ocr.ocr(frame, cls=True)

            # ocr_end_time = time.time()
            # ocr_time = ocr_end_time - ocr_start_time
            # ocr_count += 1
            for line in ocr_result:
                if line is None:
                    continue
                for i in line:
                    text = i[1][0]
                    if regex.search(text):
                        print("Detected Text:", text)
                        frame = cv2.rectangle(
                            frame, (xmin, ymin), (xmax, ymax), color, 1)
                        frame = cv2.putText(frame, text, (xmin, ymin),
                                            cv2.FONT_HERSHEY_SIMPLEX, 2, color, 2, cv2.LINE_AA)
                        output_filename = os.path.join(output_folder, file)
                        cv2.imwrite(output_filename, frame)
                        print("Saved")
                        # average_inference_time = model_inference_time + ocr_time
                        # print(average_inference_time)
