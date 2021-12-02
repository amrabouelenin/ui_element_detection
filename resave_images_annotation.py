# UI Element Detection
"""
Generate XML file annotations
Elementate bound boxes for non-selected labels.
Save new xml files

Usage:
    $ python path/to/resave_images_annotation.py --data data.yaml --range 10 --copy false --limit_bounds yes
"""

import json
import cv2 as cv
import numpy as np
import xml.etree.cElementTree as ET
import numpy as np
from shutil import copyfile
import argparse
import yaml

from ast import literal_eval

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

def write_xml_annotation(filename, label_list, bb_list, source_imgs, destination, copy=False, limit_bounds='no'):
  
  root = ET.Element("annotation")
  ET.SubElement(root, "filename", name="filename").text = f'{filename}.jpg'
  ET.SubElement(root, "path", name="path").text = f'{source_imgs}/{filename}.jpg'

  source = ET.SubElement(root, "source")
  ET.SubElement(source, "database", name="database").text = "Unknown"

  size = ET.SubElement(root, "size")
  ET.SubElement(size, "width", name="width").text = '1440'
  ET.SubElement(size, "height", name="height").text = '2560'
  ET.SubElement(size, "depth", name="depth").text = '3'

  selected_classes = label_list
  if (limit_bounds == 'yes') :
    # Define list of classes that will be only used 
    selected_classes =  [
      'Image','Icon', 'Map View', 'Video',
      'Checkbox','Date Picker','Input', 'List Item',
      'Multi-Tab', 'Radio Button','On-Off Switch',
      'Map View', 'Pager Indicator','Text Button','Slider',
      'Text'
    ]

  print(limit_bounds)
  k=0
  saved_labels = []
  for label in label_list:
    if label in selected_classes:
     
      # check for relabled labels
      if label == 'Icon':
        label = 'Image'
      if label == 'Video':
        label = 'Image'
      
      saved_labels.append(label)

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
    tree.write(f'{destination}/{filename}.xml')
    if copy!='true':
      copyfile(f'{source_imgs}/{filename}.jpg', f'{destination}/{filename}.jpg')
      print(f'copying {filename} to {destination}')

    
    print('saved labels')
    print(np.unique(saved_labels))
    saved_labels = []
    print(f'Saved image {filename}.xml')
  else:
    print(f'image is not saved, as there is no label match selected')

def parse_opt(known=False):
  parser = argparse.ArgumentParser()
  parser.add_argument('--data', type=str, default='data.yaml', help='dataset.yaml path')
  parser.add_argument('--range', type=str, default=(1,4), help='range of images to process')
  parser.add_argument('--limit_bounds', type=str, default='yes', help='range of images to process')
  parser.add_argument('--copy', type=str, default='false', help='Copy image to the new folder with annotation')

  opt = parser.parse_known_args()[0] if known else parser.parse_args()
  return opt
  
def main(opt):

  # Read data YAML file
  with open(opt.data, 'r') as stream:
    data_dict = yaml.safe_load(stream)
  
  source_imgs = data_dict['source_imgs']
  source_annot = data_dict['source_annot']
  destination_annot = data_dict['destination_annot']
  
  # Read arguments for configuration
  # data.yml to contain paths to images, and path to json files and paths to save
  # Check data.yml file
  # Read range parameter
  # Read limit_bounts in case to activate selected bounds
  imgs_range = literal_eval(opt.range)
  for i in range(imgs_range[0], imgs_range[1]):
    print(f'processing # {i} ...........................................................')
    print('                                                                             ')
    try:
        
        img_name = f'{source_imgs}/{i}.jpg'
        json_name = f'{source_annot}/{i}.json'
        img_exmp = cv.imread(img_name)
        #height, width, channels = img_exmp.shape
        with open(json_name, 'r') as j:
            json_exmp = json.loads(j.read())
            json_exmp = json.dumps(json_exmp)

        bb_list = find_values('bounds', json_exmp)
        label_list = find_values('componentLabel', json_exmp)

        ## Write annotation in XML file format
        write_xml_annotation(i,label_list,bb_list, source_imgs, destination_annot, opt.copy, opt.limit_bounds)

        print("detected labels")
        print(np.unique(label_list))
    except Exception as e:
        print(e)

if __name__ == "__main__":
    opt = parse_opt()
    main(opt)