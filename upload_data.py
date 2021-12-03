import json
import cv2 as cv
import numpy as np
import pickle
import os
import time

import xml.etree.cElementTree as ET
import requests
import base64
import io
from PIL import Image

import logging
import time

ts = time.time()
logging.basicConfig(filename=f"roboflow-upload-{ts}.log")



start = time.time()
def find_values(id, json_repr):
    results = []

    def _decode_dict(a_dict):
        try:
            results.append(a_dict[id])
        except KeyError:
            pass
        return a_dict

    json.loads(json_repr, object_hook=_decode_dict) # Return value ignored.
    return results


x = []
y = []
saved_images = []
images_error = []
for i in range(300,310):
    try:
        
        img_name = f'../test_images/{i}.jpg'

        # upload image to roboflow
        # Load Image with PIL
        image = Image.open(img_name).convert("RGB")
        # Convert to JPEG Buffer
        buffered = io.BytesIO()
        image.save(buffered, quality=90, format="JPEG")
        # Base 64 Encode
        img_str = base64.b64encode(buffered.getvalue())
        img_str = img_str.decode("ascii")
        # Construct the URL
        upload_url = "".join([
            "https://api.roboflow.com/dataset/rico_test/upload",
            "?api_key=Gzb7gSGZFzYYClG6FEpa",
            "&name=",img_name,
            "&split=train"
        ])
        # upload_url = "".join([
        #     "https://api.roboflow.com/dataset/rico-dataset-batch-6600--1/upload",
        #     "?api_key=GVbATw7bRll4z3eTh6GF",
        #     "&name=",img_name,
        #     "&split=train"
        # ])
        # POST to the API
        r = requests.post(upload_url, data=img_str, headers={
            "Content-Type": "application/x-www-form-urlencoded"
        })
        # Output result
        print(r.json())
        img_id = r.json()['id']
        logging.warning(f'Uploaded image #{i} with Id {img_id}')
        logging.warning(f'Uploaded annotation for image #{i} with Id {img_id}')
        saved_images.append(i)
       
        # upload annotation
        print("Uploading Annotation ....................")
        annotation_filename = f'../test_images/{i}.xml'
        # Read Annotation as String
        annotation_str = open(annotation_filename, "r").read()
        # Construct the URL
        upload_url = "".join([
            "https://api.roboflow.com/dataset/rico_test/annotate/"+img_id,
            "?api_key=Gzb7gSGZFzYYClG6FEpa",
            "&name=", annotation_filename
        ])
        # upload_url = "".join([
        #     "https://api.roboflow.com/dataset/rico-dataset-batch-6600--1/annotate/"+img_id,
        #     "?api_key=GVbATw7bRll4z3eTh6GF",
        #     "&name=", annotation_filename
        # ])
        # POST to the API
        r = requests.post(upload_url, data=annotation_str, headers={
            "Content-Type": "text/plain"
        })
        # Output result
        print(r.json())
        print(f'Finished uploading image #{i}')
        logging.warning(f'Finished uploading image #{i}')

    except Exception as e:
        logging.error(f'error saving image/annotation for image {i}')
        print(e)
        images_error.append(i)

total_upload = len(saved_images)
error_upload = len(images_error)
logging.warning(f'total images uploaded: {total_upload}')
logging.error(f'total images errors: {error_upload}')
