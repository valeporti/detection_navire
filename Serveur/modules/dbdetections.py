import os
import pymongo
from pymongo import MongoClient
from xmljson import Yahoo  
from json import dumps, loads
from xml.etree.ElementTree import fromstring
from xmljson import badgerfish as bf
from collections import OrderedDict

def insererInfoImageEtDetectionsSUMO(output_dir):
  results = getJsonDetections(output_dir)
  infoImage = results['metadata']
  infoIntermediaire = results['vds_analysis']
  
  #faire dictionnaire dictImage
  dictImage = {}
  dictImage["ImId"]= infoImage["ImId"]
  dictImage["image_name"]= infoImage["image_name"] 
  dictImage["nr_detections"]= infoIntermediaire["nr_detections"]

  #connect avec Mongo
  client = MongoClient('localhost', 27017)
  my_db = client["ps4_test_1_May"]

  #charge database
  tableImage = my_db["Image"]
  tableImage.insert_one(dictImage)
  
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


def getJsonDetections(output_dir):

  path_xml = '/home/ps4/ps4/Downloader/Output/S1_20190511_091646.xml'
  for file in os.listdir(output_dir):
    if file.endswith(".xml"):
      path_xml = os.path.join(output_dir, file) # should be just one
  
  xml_string = ''
  print(xml_string)
  with open(path_xml, 'r') as myfile:
    xml_string = myfile.read().replace('\n', '')
  
  bf = Yahoo(dict_type=OrderedDict, xml_fromstring=True)
  json = loads(dumps(bf.data(fromstring(xml_string))))

  detections_arr = json['analysis']['vds_target']['boat']
  metadata = json['analysis']['sat_image_metadata']
  vds_analysis = json['analysis']['vds_analysis']
  
  
  return { 'detected': detections_arr, 'metadata': metadata, 'vds_analysis': vds_analysis }

insererInfoImageEtDetectionsSUMO('/home/ps4/ps4/Downloader/Output')
