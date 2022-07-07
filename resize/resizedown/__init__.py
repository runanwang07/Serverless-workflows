import logging
import json
import azure.functions as func
from .handler import _log_msg, load_img, dump_img
from PIL import Image
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
    image = load_img(image_content)
    w,h = image.size
    _log_msg("Image size: " + str(w) + "x" + str(h))
    
    if h < 1600 and w < 1600:
        img_data = dump_img(image)
        headers = {
            "Content-type": "application/json",
            "Access-Control-Allow-Origin": "*"
        }

        return func.HttpResponse(img_data, headers = headers)
    new_size = (1600 * w // h, 1600) if (h > w) else (1600, 1600 * h // w)
    _log_msg("resize: " + str(w) + "x" + str(h) + " to " + str(new_size[0]) + "x" + str(new_size[1]))
    if max(new_size) / max(image.size) >= 0.5:
        method = Image.BILINEAR
    else:
        method = Image.BICUBIC
    image = image.resize(new_size, method)

    img_data = dump_img(image)
    logging.info(img_data)
    headers = {
        "Content-type": "application/json",
        "Access-Control-Allow-Origin": "*"
    }

    return func.HttpResponse(img_data, headers = headers)
