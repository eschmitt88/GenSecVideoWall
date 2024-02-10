import cv2
from PIL import Image
from tesserocr import PyTessBaseAPI
import time
import numpy as np
import json
import os

tesser_api = PyTessBaseAPI(path='resources/tessdata', lang='eng', psm=6, oem=3)
default_id_box = (215, 1028, 50, 43)


def load_id_box_from_config(file='config.json'):
    with open(file, 'r') as f:
        data = json.load(f)
    return data['id_box']


def save_id_box_to_config(box, file='config.json'):
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump({'id_box': box}, f)
    else:
        with open(file, 'r') as f:
            data = json.load(f)
        data['id_box'] = box
        with open(file, 'w') as f:
            json.dump(data, f)


def crop_image(image, box):
    # handle PIL image or numpy array
    if isinstance(image, Image.Image):
        image = np.array(image)
    x, y, w, h = box
    return image[y:y+h, x:x+w]


def OCR_image(image, show=False):
    tesser_api.SetImage(Image.fromarray(image))
    if show:
        cv2.imshow('image', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return tesser_api.GetUTF8Text()


def id_from_text(text, typ='int'):
    if typ == 'int':
        return int(text.split()[-1])
    elif typ == 'str':
        return text.split()[-1]
    else:
        raise ValueError('Invalid type. Must be "int" or "str".')


def screenshot_to_ID(image, box=default_id_box, typ='int', show=False):
    return id_from_text(OCR_image(crop_image(image, box), show=show), typ=typ)


def write_id_to_image(image_input, string, color=(255, 255, 255)):
    """Write the string to the image in the upper left."""
    if isinstance(image_input, Image.Image):
        image = np.array(image_input)
    else:
        image = image_input.copy()
    text_bot_loc = int(image.shape[0] / 5)
    fscale = image.shape[0] / 150
    line_width = int(image.shape[0] / 50)
    cv2.putText(image, string, (0, text_bot_loc), cv2.FONT_HERSHEY_DUPLEX, fscale, color, line_width)
    return image


def write_details_to_image(image_input, string, color=(255, 255, 255)):
    """Write the string to the image in the lower left."""
    if isinstance(image_input, Image.Image):
        image = np.array(image_input)
    else:
        image = image_input.copy()
    text_bot_loc = int(image.shape[0] - image.shape[0] / 6)
    fscale = image.shape[0] / 250
    line_width = int(image.shape[0] / 200)
    cv2.putText(image, string, (0, text_bot_loc), cv2.FONT_HERSHEY_DUPLEX, fscale, color, line_width)
    return image


def write_box_to_image(image_input, box=default_id_box, color=(255, 255, 255, 255), line_width=1):
    """Write a bounding box onto the image. Box is (x, y, w, h)"""
    if isinstance(image_input, Image.Image):
        image = np.array(image_input)
    else:
        image = image_input.copy()
    x, y, w, h = box
    cv2.rectangle(image, (x, y), (x+w, y+h), color, line_width)
    return image
    

if __name__ == "__main__":
    image = cv2.imread("tests/examples/camera_01.png")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    start = time.time()
    print('ID:', screenshot_to_ID(image, show=False))
    print('OCR time:', time.time()-start)

    image = cv2.imread("tests/examples/camera_45.png")
    image = write_id_to_image(image, 'Camera 45')
    cv2.imshow('labeled image', cv2.resize(image, (0, 0), fx=0.5, fy=0.5))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    image = cv2.imread("tests/examples/camera_45.png")
    image = write_box_to_image(image, color=(0, 0, 255, 255))
    cv2.imshow('boxed image', cv2.resize(image, (0, 0), fx=0.5, fy=0.5))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    image = cv2.imread("tests/examples/camera_45.png")
    image = write_details_to_image(image, 'mean latency: 3.1123123')
    cv2.imshow('details image', cv2.resize(image, (0, 0), fx=0.5, fy=0.5))
    cv2.waitKey(0)
    cv2.destroyAllWindows()
