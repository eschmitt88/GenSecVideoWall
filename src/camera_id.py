import cv2
from PIL import Image
from tesserocr import PyTessBaseAPI
import time
import numpy as np

tesser_api = PyTessBaseAPI(path='resources/tessdata', lang='eng', psm=6, oem=3)
id_box = (203, 1028, 60, 42)


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


def screenshot_to_ID(image, typ='int', show=False):
    return id_from_text(OCR_image(crop_image(image, id_box), show=show), typ=typ)


def write_id_to_image(image, string):
    """Write the string to the image in the upper left."""
    if isinstance(image, Image.Image):
        image = np.array(image)
    font_height = int(image.shape[0] / 5)
    fscale = image.shape[0] / 150
    line_width = int(image.shape[0] / 50)
    cv2.putText(image, string, (0, font_height), cv2.FONT_HERSHEY_DUPLEX, fscale, (255, 255, 255), line_width)
    return image


if __name__ == "__main__":
    image = cv2.imread("tests/examples/camera_01.png")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    start = time.time()
    print('ID:', screenshot_to_ID(image, show=False))
    print('OCR time:', time.time()-start)

    image = cv2.imread("tests/examples/camera_45.png")
    image = write_id_to_image(image, 'Camera 45')
    cv2.imshow('labeled image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()