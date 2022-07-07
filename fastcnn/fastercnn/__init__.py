import logging
import json
import azure.functions as func
from .handler import _log_msg, load_img, dump_img
import os
import onnxruntime
import onnx
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
from customized_LP import MyLineProfiler
scriptpath = os.path.abspath(__file__)
scriptdir = os.path.dirname(scriptpath)
filename = os.path.join(scriptdir, 'FasterRCNN-10.onnx')
labels_filename = os.path.join(scriptdir, 'coco_classes.txt')

def fig2img(fig):
    """Convert a Matplotlib figure to a PIL Image and return it"""
    import io
    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    img = Image.open(buf)
    return img

def display_objdetect_image(image, boxes, labels, scores,classes, score_threshold=0.7):
    # Resize boxes
    ratio = 800.0 / min(image.size[0], image.size[1])
    boxes /= ratio

    _, ax = plt.subplots(1, figsize=(12,9))
    image = np.array(image)
    ax.imshow(image)

    # Showing boxes with score > 0.7
    for box, label, score in zip(boxes, labels, scores):
        if score > score_threshold:
            rect = patches.Rectangle((box[0], box[1]), box[2] - box[0], box[3] - box[1], linewidth=1, edgecolor='b', facecolor='none')
            ax.annotate(classes[label] + ':' + str(np.round(score, 2)), (box[0], box[1]), color='w', fontsize=12)
            ax.add_patch(rect)
    plt.show()
    
    fig = plt.gcf()
    img = fig2img(fig)
    return img

def preprocess(image):
    # Resize
    ratio = 800.0 / min(image.size[0], image.size[1])
    image = image.resize((int(ratio * image.size[0]), int(ratio * image.size[1])), Image.BILINEAR)

    # Convert to BGR
    image = np.array(image)[:, :, [2, 1, 0]].astype('float32')

    # HWC -> CHW
    image = np.transpose(image, [2, 0, 1])

    # Normalize
    mean_vec = np.array([102.9801, 115.9465, 122.7717])
    for i in range(image.shape[0]):
        image[i, :, :] = image[i, :, :] - mean_vec[i]

    # Pad to be divisible of 32
    import math
    padded_h = int(math.ceil(image.shape[1] / 32) * 32)
    padded_w = int(math.ceil(image.shape[2] / 32) * 32)

    padded_image = np.zeros((3, padded_h, padded_w), dtype=np.float32)
    padded_image[:, :image.shape[1], :image.shape[2]] = image
    image = padded_image

    return image



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
    ort_inputs = {session.get_inputs()[0].name: x}
    preds = session.run(None, ort_inputs)
    classes = [line.rstrip('\n') for line in open(labels_filename)]
    final_img = display_objdetect_image(ximg, preds[0], preds[1], preds[2],classes)
    result = dump_img(final_img)
    headers = {
              "Content-type": "application/json",
              "Access-Control-Allow-Origin": "*"
             }
    return func.HttpResponse(result, headers = headers)
