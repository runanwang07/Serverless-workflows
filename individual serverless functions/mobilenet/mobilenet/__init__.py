import logging
import json
import azure.functions as func
from .handler import _log_msg, load_img, dump_img
import os
import onnxruntime
import onnx
import numpy as np
from customized_LP import MyLineProfiler

scriptpath = os.path.abspath(__file__)
scriptdir = os.path.dirname(scriptpath)
filename = os.path.join(scriptdir, 'mobilenetv2-7.onnx')
labels_filename = os.path.join(scriptdir, 'synset.txt')

def preprocess(ximg):
    ximg_resize = ximg.resize((224, 224))
    ximg224 = np.array(ximg_resize)
    ximg224 = ximg224 / 255
    x = ximg224.transpose(2, 0, 1)
    x = x[np.newaxis, :, :, :]
    x = x.astype(np.float32)
    return x 

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
    ximg = image.convert('RGB')
    x = preprocess(ximg)
    session= onnxruntime.InferenceSession(filename)

    session.get_modelmeta()
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name

    probs = session.run([output_name], {input_name: x})
    results = np.argsort(-(probs[0][0]))
    with open(labels_filename, 'r') as f:
        labels = [l.rstrip() for l in f]
    result = labels[results[0]]
    headers = {
              "Content-type": "application/json",
              "Access-Control-Allow-Origin": "*"
             }
    return func.HttpResponse(json.dumps(result), headers = headers)
