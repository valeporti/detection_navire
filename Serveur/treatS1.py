import subprocess
import os
from xmljson import badgerfish as bf
from xml.etree.ElementTree import fromstring
from json import dumps, loads
from xml.dom import minidom
from collections import OrderedDict
from xmljson import BadgerFish 
from xmljson import Abdera 
from xmljson import Yahoo              # import the class

import os
import pymongo
from pymongo import MongoClient
from xmljson import Yahoo  
from json import dumps, loads
from xml.etree.ElementTree import fromstring
from xmljson import badgerfish as bf
from collections import OrderedDict

import datetime


import json
from PIL import Image, ImageDraw
import numpy as np
import math
import glob

import zipfile
import mysql.connector


output_dir = os.getcwd()+'/workdir'
sumo_dir = os.getcwd()+'/modules/SUMO_Lin64_1.3.5'
s1_file = ''
xmlPath = ''

def runSumo(s1_zip): #s1_dir = SAFE image
  global s1_file
  zip_ref = zipfile.ZipFile(s1_zip, 'r')
  zip_ref.extractall('./workdir')
  zip_ref.close()
  unzipped = s1_zip[:-4] + '.SAFE'
  
  s1_file = os.getcwd()+'/'+unzipped + '/manifest.safe'
  
  thh = tvv = 1.8
  thv = tvh = 1.2
  

  subprocess.check_call(f'cd {sumo_dir}/ && {sumo_dir}/start_batch.sh -i {s1_file} -thh {thh} -thv {thv} -tvh {tvh} -tvv {tvv} -sh {sumo_dir}/resources/coastline/OSMLandPoly_20141001_250/OSMLandPoly_20141001_250m.shp -b 0 -o {output_dir}',shell=True)

  
def getJsonDetections():
  global xmlPath
  xmlPath = glob.glob(output_dir+"/*.xml")[0]
  with open(xmlPath, 'r') as myfile:
    xml_string = myfile.read().replace('\n', '')
  
  bf = Yahoo(dict_type=OrderedDict, xml_fromstring=True)
  json = loads(dumps(bf.data(fromstring(xml_string))))

  detections_arr = json['analysis']['vds_target']['boat']
  metadata = json['analysis']['sat_image_metadata']
  vds_analysis = json['analysis']['vds_analysis']
  
  
  return { 'detected': detections_arr, 'metadata': metadata, 'vds_analysis': vds_analysis }

def compatibilityRevision(sumoImage) :
  
  try: 
    where_images = sumoImage + '/measurement'
    if (os.path.isdir(where_images)) :
      # check if tiff file
      for file in os.listdir(where_images):
        if file.endswith(".tiff"):
          return True
      return False
  except:
    print('Error in compatibility Revision')


#if (compatibilityRevision(s1_dir)):
#	runSumo(output_dir,sumo_dir,s1_dir)
#  results = getJsonDetections()

Image.MAX_IMAGE_PIXELS = 1000000000

def getBoats(imageName):
  results = getJsonDetections()
  tiffImage = glob.glob(s1_file[:-13]+'measurement/*.tiff')[0]
  image = Image.open(tiffImage)
  w, h = image.size
  minimun_size = 60
  count = 1
  
  if not os.path.exists('/var/www/html/'+imageName):
    os.makedirs('/var/www/html/'+imageName)
  
  for detection in results['detected']:
    x_pixel = detection['xpixel']
    y_pixel = detection['ypixel']
    length = detection['length']
    width = detection['width']
    box = (x_pixel - minimun_size, y_pixel - minimun_size, x_pixel + minimun_size, y_pixel + minimun_size) # The crop rectangle, as a (left, upper, right, lower)-tuple
    cropped_img = image.crop(box)
    cropped_img.save('new', format='tiff')
    im = cropped_img.convert('RGBA')
    draw = ImageDraw.Draw(im)
    one = minimun_size - max([length, width])
    two = minimun_size + max([length, width])
    draw.rectangle(((one, one), (two, two)), outline="#ff8888")
    im.save('/var/www/html/'+imageName+'/' + str(count)+'.jpg', format='png')
    count += 1
    
def insererInfoImageEtDetectionsSUMO(geojson,image_name):
  results = getJsonDetections()
  infoImage = results['metadata']
  infoIntermediaire = results['vds_analysis']
  
  #faire dictionnaire dictImage
  dictImage = {}
  dictImage["ImId"]= infoImage["ImId"]
  dictImage["image_name"]= infoImage["image_name"] 
  dictImage["nr_detections"]= infoIntermediaire["nr_detections"]
  dictImage["localisation"] = geojson

  #connect avec Mongo
  client = MongoClient('localhost', 27017)
  my_db = client["ps4_test_1_May"]

  #charge database
  tableImage = my_db["Image"]
  tableImage.insert_one(dictImage)
  
  #charge mysql
  db = mysql.connector.connect(host="localhost",user="ps4",passwd="ps4",database="ps4")
  cursor = db.cursor()
  
  datetimeObject = datetime.datetime.strptime((infoImage["ImId"].split("_"))[1], "%Y%m%d")
  sql = "INSERT INTO Image(ImId, image_name, nr_detections, localisation, date,type) VALUES('{}','{}','{}','{}','{}','{}');"
  cursor.execute(sql.format(image_name,image_name,infoIntermediaire["nr_detections"],geojson,datetimeObject.strftime('%Y-%m-%d %H:%M:%S'),'S1'))
  
  
  sql = "INSERT INTO Detection(target_number,lat,lon,ImId) VALUES ('{}','{}','{}','{}');"
  
  for detection in results['detected']:
    #faire dictionnaire dictDet
    dictDet = {}
    dictDet["target_number"]= detection["target_number"]
    dictDet["lat"]= detection["lat"]
    dictDet["lon"]= detection["lon"]
    dictDet["length"]= detection["length"]
    dictDet["reliability"]= detection["reliability"]
    dictDet["ImId"]= infoImage["ImId"]

    dictDet["date"]= int((infoImage["ImId"].split("_"))[1]) # change par lei
 
    #charge database
    tableImage = my_db["Detection"]
    tableImage.insert_one(dictDet)
    cursor.execute(sql.format(detection["target_number"],detection["lat"],detection["lon"],image_name))
    
  db.commit()

def treatS1(s1_zip,imageName,geojson):
  runSumo(s1_zip)
  getBoats(imageName)
  insererInfoImageEtDetectionsSUMO(geojson,imageName)
  
