import logging
import json
import azure.functions as func
from .handler import _log_msg, load_img, dump_img
import numpy as np
from customized_LP import MyLineProfiler

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
    input_size = int(req.params.get('input'))
    img = np.array(image_content)
    logging.info(type(img))
    h, w = img.shape[:2]
    cropx = input_size
    cropy = input_size
    startx = max(0, w//2-(cropx//2) - 1)
    starty = max(0, h//2-(cropy//2) - 1)
    _log_msg("crop_center: " + str(w) + "x" + str(h) +" to " + str(cropx) + "x" + str(cropy))
    resize_image = img[starty:starty+cropy, startx:startx+cropx]
    headers = {
        "Content-type": "application/json",
        "Access-Control-Allow-Origin": "*"
    }

    return func.HttpResponse(json.dumps(resize_image.tolist()), headers = headers)
