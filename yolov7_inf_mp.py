import numpy as np
import cv2
import torch
from paddleocr import PaddleOCR
from models.experimental import attempt_load
from utils.general import non_max_suppression
import re

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


class OBJ_DETECTION():
    def __init__(self, model_path, classes, input_width=640):
        self.classes = classes
        self.yolo_model = attempt_load(weights=model_path, map_location=device)
        self.input_width = input_width
        self.ocr = PaddleOCR(use_angle_cls=True, lang='en')
        self.re = re.compile(r'^\d+\.\d$')

    def detect(self, main_img, conf_thresh=0.60, iou_thresh=0.25):
        height, width = main_img.shape[:2]
        new_height = int((((self.input_width / width) * height) // 32) * 32)

        img = cv2.resize(main_img, (self.input_width, new_height))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = np.moveaxis(img, -1, 0)
        img = torch.from_numpy(img).to(device)
        img = img.float() / 255.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        pred = self.yolo_model(img, augment=False)[0]
        pred = non_max_suppression(
            pred, conf_thres=conf_thresh, iou_thres=iou_thresh, classes=None)

        processed_results = []
        processed_objects = []

        if pred is not None and len(pred) > 0:
            for p in pred[0]:
                score = np.round(p[4].cpu().detach().numpy(), 2)
                label = self.classes[int(p[5])]
                xmin = int(p[0] * main_img.shape[1] / self.input_width)
                ymin = int(p[1] * main_img.shape[0] / new_height)
                xmax = int(p[2] * main_img.shape[1] / self.input_width)
                ymax = int(p[3] * main_img.shape[0] / new_height)

                # cropped_img = main_img[ymin:ymax, xmin:xmax]
                # roi = main_img[ymin:ymax, xmin:xmax]
                # blurred_image = main_img.copy()
                # blurred_image = cv2.blur(blurred_image, (25, 25))
                # blurred_image[ymin:ymax, xmin:xmax] = roi
                # cv2.imshow("Blurred Image with ROI", blurred_image)
                # cv2.waitKey(0)

                ocr_result = self.ocr.ocr(main_img, cls=True)
                for line in ocr_result:
                    if line is None:
                        continue
                    for i in line:
                        text = i[1][0]
                        if self.re.search(text):
                            print("Detected Text:", text)
                            processed_objects.append({
                                'class': label,
                                'score': score,
                                'bbox': [xmin, ymin, xmax, ymax],
                                'ocr_text': text,
                            })

        processed_objects.sort(key=lambda x: x['score'], reverse=True)
        if processed_objects:
            processed_results.append(processed_objects[0])

        return processed_results
