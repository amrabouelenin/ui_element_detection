import json
import cv2 as cv
import numpy as np
import os
import time

import xml.etree.cElementTree as ET
import numpy as np

import random
from shutil import copyfile


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

def write_xml_annotation(filename, label_list):
  
  root = ET.Element("annotation")
  ET.SubElement(root, "filename", name="filename").text = f'{filename}.jpg'
  ET.SubElement(root, "path", name="path").text = f'../combined/{filename}.jpg'

  source = ET.SubElement(root, "source")
  ET.SubElement(source, "database", name="database").text = "Unknown"

  size = ET.SubElement(root, "size")
  ET.SubElement(size, "width", name="width").text = '1440'
  ET.SubElement(size, "height", name="height").text = '2560'
  ET.SubElement(size, "depth", name="depth").text = '3'

  # Define list of classes that will be only used 
  selected_classes =  [
    'Bottom Navigation','Button Bar', 'Checkbox',
    'Date Picker','Icon', 'Input', 'List Item',
    'Map View','On-Off Switch', 'Pager Indicator',
    'Radio Button','Text Button', 'Text', 'Toolbar'
  ]
  # Check if the lablel belong to any of those classes
  # increase number of saved_labels
  # check if saved_lables is not empty 
  # then save the new xml

  k=0
  saved_labels = []
  for label in label_list:
    if label in selected_classes:
      saved_labels.append(label)
      # Object
      # 		<name>Web View</name>
      #     <pose>Unspecified</pose>
      #     <truncated>0</truncated>
      #     <difficult>0</difficult>
      #     <bndbox>
      #       <xmin>0</xmin>
      #       <ymin>291</ymin>
      #       <xmax>1440</xmax>
      #       <ymax>2392</ymax>
      #     </bndbox>        
      object = ET.SubElement(root, "object")
      ET.SubElement(object, "name", name="name").text = label
      ET.SubElement(object, "pose", name="pose").text = 'Unspecified'
      ET.SubElement(object, "truncated", name="truncated").text = '0'
      ET.SubElement(object, "difficult", name="difficult").text = '0'

      bndbox = ET.SubElement(object, "bndbox")
      ET.SubElement(bndbox, "xmin", name="xmin").text = str(bb_list[k][0])
      ET.SubElement(bndbox, "ymin", name="ymin").text = str(bb_list[k][1])
      ET.SubElement(bndbox, "xmax", name="xmax").text = str(bb_list[k][2])
      ET.SubElement(bndbox, "ymax", name="ymax").text = str(bb_list[k][3])
      k = k+1

  if saved_labels:
    tree = ET.ElementTree(root)
    tree.write(f'../limited_rico/{filename}.xml')
    copyfile(f'../combined/{filename}.jpg', f'../limited_rico/{filename}.jpg')

    
    print('saved labels')
    print(np.unique(saved_labels))
    saved_labels = []
    print(f'Saved image {filename}.xml')
  else:
    print(f'image is not saved, as there is no label match selected')
  
# using list comprehension + randrange()
# to generate random number list
randomrange = [random.randrange(1, 66000, 1) for i in range(6000)]
for i in randomrange:
  
    print(f'processing # {i} ...........................................................')
    print('                                                                             ')
    try:
        
        img_name = f'../combined/{i}.jpg'
        json_name = f'../semantic_annotations/{i}.json'
        img_exmp = cv.imread(img_name)
        height, width, channels = img_exmp.shape
        with open(json_name, 'r') as j:
            json_exmp = json.loads(j.read())
            json_exmp = json.dumps(json_exmp)

        bb_list = find_values('bounds', json_exmp)
        label_list = find_values('componentLabel', json_exmp)

        ## Write annotation in XML file format
        write_xml_annotation(i,label_list)

        print("detected labels")
        print(np.unique(label_list))
    except Exception as e:
        print(e)