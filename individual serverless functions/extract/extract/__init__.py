import logging
import json
import azure.functions as func
from .handler import _log_msg, load_img, dump_img, _extract_bilinear_pixel
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
    logging.info(type(image_content))
    img = np.array(image_content)
    h, w = img.shape[:2]
    _log_msg("extract_and_resize_to_256_square: " + str(w) + "x" + str(h) +" and resize to " + str(256) + "x" + str(256))
    targetSize = (256,256)
    determinant = img.shape[1] * targetSize[0] - img.shape[0] * targetSize[1]
    if determinant < 0:
        ratio = float(img.shape[1]) / float(targetSize[1])
        xOrigin = 0
        yOrigin = int(0.5 * (img.shape[0] - ratio * targetSize[0]))
    elif determinant > 0:
        ratio = float(img.shape[0]) / float(targetSize[0])
        xOrigin = int(0.5 * (img.shape[1] - ratio * targetSize[1]))
        yOrigin = 0
    else:
        ratio = float(img.shape[0]) / float(targetSize[0])
        xOrigin = 0
        yOrigin = 0
    resize_image = np.empty((targetSize[0], targetSize[1], img.shape[2]), dtype=np.uint8)
    for y in range(targetSize[0]):
        for x in range(targetSize[1]):
            resize_image[y, x] = _extract_bilinear_pixel(img, x, y, ratio, xOrigin, yOrigin)


    headers = {
        "Content-type": "application/json",
        "Access-Control-Allow-Origin": "*"
    }
    logging.info(resize_image)
    return func.HttpResponse(json.dumps(resize_image.tolist()), headers = headers)