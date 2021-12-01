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

for i in range(1000, 11000):
    try:
        
        img_name = f'../rico_limited/{i}.jpg'
        json_name = f'../semantic_annotations/{i}.json'

        img_exmp = cv.imread(img_name)
        
        height, width, channels = img_exmp.shape
        with open(json_name, 'r') as j:
            json_exmp = json.loads(j.read())
            json_exmp = json.dumps(json_exmp)


        bb_list = find_values('bounds', json_exmp)
        label_list = find_values('componentLabel', json_exmp)

        #tree.write(f'./combined/{i}.xml')

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
            "https://api.roboflow.com/dataset/rico_dataset_limited/upload",
            "?api_key=Gzb7gSGZFzYYClG6FEpa",
            "&name=",img_name,
            "&split=train"
        ])
        # POST to the API
        r = requests.post(upload_url, data=img_str, headers={
            "Content-Type": "application/x-www-form-urlencoded"
        })
        # Output result
        print(r.json())
        img_id = r.json()['id']
        print("Uploading Annotation ....................")
        # upload annotation
        annotation_filename = f'../rico_limited/{i}.xml'
        # Read Annotation as String
        annotation_str = open(annotation_filename, "r").read()
        # Construct the URL
        upload_url = "".join([
            "https://api.roboflow.com/dataset/rico_dataset_limited/annotate/"+img_id,
            "?api_key=Gzb7gSGZFzYYClG6FEpa",
            "&name=", annotation_filename
        ])
        # POST to the API
        r = requests.post(upload_url, data=annotation_str, headers={
            "Content-Type": "text/plain"
        })
        # Output result
        print(r.json())
        print(f'Finished uploading image #{i}')

    except Exception as e:
        print(e)

# print(len(x))
# print(len(y))

# x_np = np.asarray(x, dtype=object)
# y_np = np.asarray(y, dtype=object)

# # with open('x.pickle', 'wb') as fp:
# #     pickle.dump(x_np, fp)

# # with open('y.pickle', 'wb') as fp:
# #     pickle.dump(y_np, fp)

# print('started pickling')
# for i in range(11):
#     with open(f'x_{i}.pickle', 'wb') as fp:
#         pickle.dump(x_np[i*100000:(i+1)*100000], fp)

#     with open(f'y_{i}.pickle', 'wb') as fp:
#         pickle.dump(y_np[i*100000:(i+1)*100000], fp)

#     print(f'pickling between {i} and {i+1}')


# with open('x_11.pickle', 'wb') as fp:
#     pickle.dump(x_np[1100000:1121198], fp)

# with open('y_11.pickle', 'wb') as fp:
#     pickle.dump(y_np[1100000:1121198], fp)


# end = time.time()

# print(f'The process took {end-start} seconds')