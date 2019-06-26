import sys
import subprocess
sys.path.append('Scripts/')
import gdal_merge
import zipfile  
import os
import time
import readline, glob
from pathlib import Path
#import gdal_merge
from PIL import Image
import numpy as np

def complete(text, state):
    return (glob.glob(text+'*')+[None])[state]


def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]


def generate_geotiffs(inputProductPath, outputPath):
      basename =  os.path.basename(inputProductPath)
      if os.path.isdir(outputPath + basename[:-3] + "SAFE") :
        print('Already extracted')
      else:
        zip = zipfile.ZipFile(inputProductPath) 
        zip.extractall(outputPath) 
        print("Extracting Done") 
      
      directoryName = outputPath + basename[:-3] + "SAFE/GRANULE"
      productName = os.path.basename(inputProductPath)[:-4]
      outputPathSubdirectory = outputPath + productName + "_PROCESSED"
      
      if not os.path.exists(outputPathSubdirectory):
        os.makedirs(outputPathSubdirectory)
      
      subDirectorys = get_immediate_subdirectories(directoryName)
      
      
      for granule in subDirectorys:
          print('granule',granule)
          unprocessedBandPath = outputPath + productName + ".SAFE/GRANULE/" + granule + "/" + "IMG_DATA/"
          image_file_name=os.listdir(unprocessedBandPath)[0][:-7]
          generate_all_bands(unprocessedBandPath, image_file_name, outputPathSubdirectory)



def generate_all_bands(unprocessedBandPath, granule, outputPathSubdirectory):
      #granuleBandTemplate =  granule[4:11]+granule[19:-1]+'1_'
      outputPathSubdirectory = outputPathSubdirectory
      if not os.path.exists(outputPathSubdirectory+ "/IMAGE_DATA"):
        os.makedirs(outputPathSubdirectory+ "/IMAGE_DATA")
      results = [] 
      outPutTiff = granule[:-1]+'1' + '16Bit'
      #outPutVRT =  granule[:-1]+'1' + '16Bit-AllBands.vrt'
      outPutFullPath = outputPathSubdirectory + "/IMAGE_DATA/"
      #outPutFullVrt = outputPathSubdirectory + "/IMAGE_DATA/" + outPutVRT
      #inputPath = unprocessedBandPath + granuleBandTemplate
      inputPath = unprocessedBandPath + granule
    
      bands = {"band_04" :  inputPath + "B04.jp2",
               "band_03" :  inputPath + "B03.jp2",
               "band_02" :  inputPath + "B02.jp2"}
      #cmd = ['gdalbuildvrt', '-resolution', 'user', '-tr' ,'20', '20', '-separate' ,outPutFullVrt]
      #cmd = ['gdalbuildvrt','-ot','Byte','-scale','0','10000','0','255',outPutFullVrt]
      
      for key, value in bands.items():
          outPutFullPath_image = outPutFullPath+ outPutTiff+'_'+key+'.tif'
          cmd = ['gdal_translate','-ot','Byte','-scale','0','4096','0','255']
          cmd.append(value)
          cmd.append(outPutFullPath_image)
          results.append(outPutFullPath_image)
          my_file = Path(outPutFullPath_image)
          #if not my_file.is_file():
           #   subprocess.call(cmd)
#      my_file = Path(outPutFullVrt)
#      if not my_file.is_file():
#        # file exists
      merged = outputPathSubdirectory + "/merged.tif"
      jpg_out = outputPathSubdirectory + "/merged.jpg"
      
      
      #params = ['',"-of", "GTiff", "-o", merged]
      params = ['','-v','-ot','Byte','-separate','-of','GTiff','-co','PHOTOMETRIC=RGB','-o',merged]
      
      for granule in results:
          params.append(granule)



      gdal_merge.main(params)
      
      subprocess.call(['gdal_translate','-of','JPEG',merged,jpg_out])
      #gdal_translate -of JPEG -scale -co worldfile=yes input.tiff output.jpg
        
      #, '-a_srs', 'EPSG:3857'
      #cmd = ['gdal_translate', '-of' ,'GTiff', outPutFullVrt, outPutFullPath]
      #cmd = ['gdal_translate','-scale_1','0','4096','-scale_2','0','4096','-scale_3','0','4096','-ot','Byte' ,outPutFullVrt, outPutFullPath]
#      cmd = ['gdal_translate','-scale_1','0','3801','0','255','-scale_2','0','4206','0','255','-scale_3','0','4818','0','255','-ot','Byte' ,outPutFullVrt, outPutFullPath]
#      
#      
#      
#      my_file = Path(outPutTiff)
#      if not my_file.is_file():
#        # file exists
#        subprocess.call(cmd)
