import keras.models

import keras.backend as K
from keras.optimizers import Adam
from keras.losses import binary_crossentropy
from keras.preprocessing.image import ImageDataGenerator
from skimage.io import imread,imshow
import numpy as np
from PIL import Image
import os
import matplotlib.pyplot as plt
import sys
import shutil
from pymongo import MongoClient
import datetime
import mysql.connector
sys.path.insert(0, '/media/rudresh/New Volume 1/Air_bus/Airbus_S4/Code_Airbus')

import locateImg
K.clear_session()

#### customized loss function to evaluate the loss of model#############

def dice_loss(y_true, y_pred):
    smooth = 1.
    y_true_f = K.flatten(y_true)
    y_pred_f = K.flatten(y_pred)
    intersection = y_true_f * y_pred_f
    score = (2. * K.sum(intersection) + smooth) / (K.sum(y_true_f) + K.sum(y_pred_f) + smooth)
    return 1. - score

def bce_logdice_loss(y_true, y_pred):
    return binary_crossentropy(y_true, y_pred) - K.log(1. - dice_loss(y_true, y_pred))

def dice_p_bce(in_gt, in_pred):
    return 1e-3*binary_crossentropy(in_gt, in_pred) - dice_coef(in_gt, in_pred)

def true_positive_rate(y_true, y_pred):
    return K.sum(K.flatten(y_true)*K.flatten(K.round(y_pred)))/K.sum(y_true)

def dice_coef(y_true, y_pred, smooth=1):
    intersection = K.sum(y_true * y_pred, axis=[1,2,3])
    union = K.sum(y_true, axis=[1,2,3]) + K.sum(y_pred, axis=[1,2,3])
    return K.mean( (2. * intersection + smooth) / (union + smooth), axis=0)


##########load the trained model my_model.h5 with the weight and configuration loaded on top of it  #########




def load_model(inputPath,geojson,image_name):
    model = keras.models.load_model('./modules/S2_treatment/my_model.h5', custom_objects={'bce_logdice_loss': bce_logdice_loss,'dice_coef':dice_coef,'true_positive_rate':true_positive_rate})
    client = MongoClient('localhost', 27017)
    my_db = client["ps4_test_1_May"]
    
    # MySQL db
    db = mysql.connector.connect(host="localhost",user="ps4",passwd="ps4",database="ps4")
    cursor = db.cursor()
    
    
    
    safe_file_name= inputPath[:-4]+ ".SAFE"
    file_name = inputPath[:-4]+ "_PROCESSED"
    cropped_image = file_name+"/ChopedImages"
    test_paths = os.listdir(cropped_image)

    if not os.path.exists(file_name+"/resultImages"):os.makedirs(file_name+"/resultImages")

    result_path = inputPath[:-4]+ "_PROCESSED"+"/resultImages"

    desired_batch_size=2
    test_datagen = ImageDataGenerator(rescale=1./255)
    test_generator = test_datagen.flow_from_directory(
        cropped_image,
        target_size=(768, 768),
        color_mode="rgb",
        shuffle = False,
        class_mode='categorical',
        batch_size=desired_batch_size)
    print("test_generator successfully declared")
    filenames = test_generator.filenames
    print("filenames are:",filenames[0])
    nb_samples = len(filenames)
    print("There are ", nb_samples," samples")
    test_generator.reset()
    print("Successfully .reset() Calculating probabilites, will take some time...")
    probabilities = model.predict_generator(test_generator, steps = 
                        np.ceil(nb_samples/desired_batch_size))
    K.clear_session()
    test_generator.reset()
    print("probs calculated suuccefully")
    sql = "INSERT INTO Detection(target_number,lat,lon,ImId) VALUES ('{}','{}','{}','{}');"
    j=1
    for i in range(0,nb_samples):
        generated_image=np.reshape(probabilities[i], (768, 768))
        
        if(np.amax(generated_image)>0.7):
            dictDet = {}
            dictDet["target_number"]=j 
            print("target_number",dictDet["target_number"])
            cordinate_x =int(filenames[i][43:-11])
            cordinate_y =int(filenames[i][50:-4])
            x,y =(np.where(generated_image==np.amax(generated_image)))
            Actual_cordinate_x=cordinate_x+x[0]
            Actual_cordinate_y=cordinate_y+y[0]
            detection_location = locateImg.getCoordinatesOfpixel(safe_file_name,Actual_cordinate_x,Actual_cordinate_y,10980,10980)
            dictDet["lat"]= detection_location[0]
            #print("lat",dictDet["lat"])    
            dictDet["lon"]= detection_location[1]
            #print("lon",dictDet["lon"])  
            dictDet["length"]= 0
            #print("length",dictDet["length"])
            dictDet["reliability"]= 0
            #print("reliability",dictDet["reliability"])
            dictDet["ImId"]= image_name
            #print("ImId",dictDet["ImId"])
            dictDet["date"]= int((safe_file_name.split("_"))[2][:-7])
            #print("date",dictDet["date"])
            #charge database
            tableImage = my_db["Detection"]
            tableImage.insert_one(dictDet)
            datetimeObject = datetime.datetime.strptime((safe_file_name.split("_"))[2][:-7], "%Y%m%d")
            cursor.execute(sql.format(j,detection_location[0],detection_location[1],image_name))
            
            if not os.path.exists('/var/www/html/'+image_name):
                os.makedirs('/var/www/html/'+image_name)
            shutil.copy(cropped_image+'/'+filenames[i], '/var/www/html/'+image_name+'/'+str(j)+'.jpg')
            plt.imsave(result_path+'/'+filenames[i][13:-4]+'_location_'+str(Actual_cordinate_x)+','+str(Actual_cordinate_y)+'.jpg', generated_image)
            j=j+1
    
    dictImage = {}
    dictImage["ImId"]= image_name
    #print(dictImage["ImId"])
    if(safe_file_name[0] == '/'):
        safe_file_name = safe_file_name[1:]
    dictImage["image_name"]= safe_file_name.split("workdir/")[1]
    #print(dictImage["image_name"])
    numberimg = os.listdir('/var/www/html/'+image_name)
    dictImage["nr_detections"]= len(numberimg)
    dictImage["localisation"] = geojson
    #print(dictImage["nr_detections"])
    #charge database
    tableImage = my_db["Image"]
    tableImage.insert_one(dictImage)
    
    datetimeObject = datetime.datetime.strptime((safe_file_name.split("_"))[2][:-7], "%Y%m%d")
    sql = "INSERT INTO Image(ImId, image_name, nr_detections, localisation, date,type) VALUES('{}','{}','{}','{}','{}','S2');"
    cursor.execute(sql.format(image_name,image_name,len(numberimg),geojson,datetimeObject.strftime('%Y-%m-%d %H:%M:%S')))
    db.commit()
    
    





















