import logging
import json
import azure.functions as func
from .handler import _log_msg, load_img, dump_img
import os
import onnxruntime
import onnx
import numpy as np
import cv2
from customized_LP import MyLineProfiler
scriptpath = os.path.abspath(__file__)
scriptdir = os.path.dirname(scriptpath)
filename = os.path.join(scriptdir, 'resnet50-v1-12.onnx')
labels_filename = os.path.join(scriptdir, 'synset.txt')

def preprocess(img):
    img = img / 255.
    img = cv2.resize(img, (256, 256))
    h, w = img.shape[0], img.shape[1]
    y0 = (h - 224) // 2
    x0 = (w - 224) // 2
    img = img[y0 : y0+224, x0 : x0+224, :]
    img = (img - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
    img = np.transpose(img, axes=[2, 0, 1])
    img = img.astype(np.float32)
    img = np.expand_dims(img, axis=0)
    return img


profile = MyLineProfiler()
def main(req: func.HttpRequest) -> func.HttpResponse:
        profile.start()
        result = wrapper_function(req)
        profile.stop()
        return result

@profile
def wrapper_function(req: func.HttpRequest):
    image_content = json.loads(req.get_body())
    image = load_img(image_content)
    img = np.array(image.convert('RGB'))
    x = preprocess(img)
    session= onnxruntime.InferenceSession(filename)

    session.get_modelmeta()
    ort_inputs = {session.get_inputs()[0].name: x}
    preds = session.run(None, ort_inputs)[0]
    preds = np.squeeze(preds)
    with open(labels_filename, 'r') as f:
        labels = [l.rstrip() for l in f]
    a = np.argsort(preds)[::-1]
    result = [labels[a[0]],str(preds[a[0]])]
    logging.info(result)
    headers = {
              "Content-type": "application/json",
              "Access-Control-Allow-Origin": "*"
             }
    return func.HttpResponse(json.dumps(result), headers = headers)
