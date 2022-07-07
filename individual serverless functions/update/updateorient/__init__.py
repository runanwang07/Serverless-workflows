import logging
import json
import azure.functions as func
from .handler import _log_msg, load_img, dump_img

from customized_LP import MyLineProfiler
from PIL import Image
profile = MyLineProfiler()

def main(req: func.HttpRequest) -> func.HttpResponse:
    profile.start()
    result = wrapper_function(req)
    profile.stop()
    return result

@profile
def wrapper_function(req: func.HttpRequest):
    image_content = json.loads(req.get_body())
    logging.info(image_content)
    image = load_img(image_content)
    logging.info(image)
    w,h = image.size
    _log_msg("Image size: " + str(w) + "x" + str(h))
    exif_orientation_tag = 0x0112
    if hasattr(image, '_getexif'):
        exif = image._getexif()
        if exif != None and exif_orientation_tag in exif:
            orientation = exif.get(exif_orientation_tag, 1)
            _log_msg('Image has EXIF Orientation: ' + str(orientation))
            # orientation is 1 based, shift to zero based and flip/transpose based on 0-based values
            orientation -= 1
            if orientation >= 4:
                image = image.transpose(Image.TRANSPOSE)
            if orientation == 2 or orientation == 3 or orientation == 6 or orientation == 7:
                image = image.transpose(Image.FLIP_TOP_BOTTOM)
            if orientation == 1 or orientation == 2 or orientation == 5 or orientation == 6:
                image = image.transpose(Image.FLIP_LEFT_RIGHT)
    img_data = dump_img(image)
    headers = {
        "Content-type": "application/json",
        "Access-Control-Allow-Origin": "*"
    }

    return func.HttpResponse(img_data, headers = headers)