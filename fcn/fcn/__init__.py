import logging
import json
import azure.functions as func
from .handler import _log_msg, load_img, dump_img
import numpy as np
from PIL import Image
import onnxruntime as ort
from matplotlib.colors import hsv_to_rgb
import cv2
import os
from torchvision import transforms
scriptpath = os.path.abspath(__file__)
scriptdir = os.path.dirname(scriptpath)
filename = os.path.join(scriptdir, 'fcn-resnet50-12.onnx')

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
    ximg = image.convert('RGB')
    preprocess = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    input_tensor = preprocess(ximg)
    session = ort.InferenceSession(filename)
    input_tensor = input_tensor.unsqueeze(0)
    input_tensor = input_tensor.detach().cpu().numpy()
    ort_inputs = {session.get_inputs()[0].name: input_tensor}
    preds = session.run(["out"], ort_inputs)[0]
    headers = {
              "Content-type": "application/json",
              "Access-Control-Allow-Origin": "*"
             }
    return func.HttpResponse(json.dumps("trained model"), headers = headers)
