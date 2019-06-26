### code to convert the sentinel 2 JP2 images into the tiff format###########

import os
import time
import Jp2_tiff_Converter as cnv
import predict_image_model as p_image


#######Set the Input and output path##################
def main_sentinel_2(input_directory,output_directory,geojson,image_name):
    
    inputPath = input_directory
    outputPath = output_directory
    
    start_time = time.time()
    
    cnv.generate_geotiffs(inputPath, outputPath)
    
    print("--- %s seconds ---" % (time.time() - start_time))
    #############################################################
    
    #### convert the tiff image into jpg image###########
    file_name = inputPath[:-4]+ "_PROCESSED"
    print("file_name=",file_name)
    
    ##### Cut the images in the size of 786*786 and put into the folder###
    
    from PIL import Image
    
    infile = 'merged.jpg'
    file_location = file_name+'/'+infile
    chopsize = 1220
    
    img = Image.open(file_location)
    width, height = img.size
    
    if not os.path.exists(file_name+"/ChopedImages/ChopedImages"):
        os.makedirs(file_name+"/ChopedImages/ChopedImages")
    
    # Save Chops of original image
    for x0 in range(0, width, chopsize):
       for y0 in range(0, height, chopsize):
          box = (x0, y0,
                 x0+chopsize if x0+chopsize <  width else  width - 1,
                 y0+chopsize if y0+chopsize < height else height - 1)
          print('%s %s' % (infile, box))
          img.crop(box).save(file_name+'/ChopedImages/ChopedImages/%s.%s.x%05d.y%05d.jpg' % (image_name[:19],(time.localtime().tm_hour,time.localtime().tm_min), x0, y0))
    p_image.load_model(inputPath,geojson,image_name)

