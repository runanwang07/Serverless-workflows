import logging
import json
import azure.functions as func
from datetime import datetime
import logging
import os
import io
from urllib.request import urlopen
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
    image_url = json.loads(req.get_body())
    logging.info("Predicting from url: " + image_url)
    headers = {
        "Content-type": "application/json",
        "Access-Control-Allow-Origin": "*"
    }
    try:
        with urlopen(image_url) as testImage:
            image = Image.open(testImage)

    except:
        response_content = 'Bad input'
        return func.HttpResponse(json.dumps(response_content), headers = headers)
    if image.mode == "RGB":
        response_content = 'RGB'
        return func.HttpResponse(json.dumps(response_content), headers = headers)
    else:
        response_content = 'convert'
        return func.HttpResponse(json.dumps(response_content), headers = headers)