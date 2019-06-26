"""
Sentinel images automatic downloader
"""

from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import datetime, timedelta
import time, datetime
import glob,os,sys
import json
import configparser
import zipfile
import shutil
import pickle

# Importing S1/S2 modules
sys.path.append('./modules')
sys.path.append('./modules/S2_treatment')
import treatS1
import sentinel2_data_processing

import mysql.connector
import datetime
from pymongo import MongoClient

class Downloader():
    def __init__(self, configFile = './config.ini', ignoreStart=False):
        print("Server initializing...")
        
        
        
        print("Checking for geoJSON files")
        self.geoJSONList = []
        
        #Connect MYSQL
        db = mysql.connector.connect(host="localhost",user="ps4",passwd="ps4",database="ps4")
        cursor = db.cursor()
        
        cursor.execute("TRUNCATE TABLE Localisation")
        sql = "INSERT INTO Localisation(localisation) VALUES (%s)"
        for file in glob.glob("*.geojson"):
            self.geoJSONList.append(file)
            cursor.execute(sql,(file,))
            
        db.commit()
        print("Inserted succcesfully")
        #connect avec Mongo
        #Mongo doesn't take into consideration multiple geoJSONs

        self.footprints = [geojson_to_wkt(read_geojson(footprintPath)) for footprintPath in self.geoJSONList]
        print("This is the list of detected geoJSONs, the database has been updated. Obsolete images with non-existing geoJSONs won't be show in the interface.")
        print(self.geoJSONList)
        
        
        print("Resetting workdir")
        os.system("rm -rf "+os.getcwd()+"/workdir")
        os.makedirs(os.getcwd()+'/workdir')
        
        
        self.configParsing(configFile)
        self.api = SentinelAPI(self.login, self.password, self.link)
        self.ignoreStart = ignoreStart
        
    def configParsing(self,configFile):
        """ Parses the config file """
        config = configparser.ConfigParser()
        config.read('config.ini')
        
        if(config.sections() != ['CONNEXION', 'DIRECTORIES', 'DATA', 'SUMO LOCATION']):
            raise Exception("Configuration file missing elements")
            
        self.login = config['CONNEXION']['Login']
        self.password = config['CONNEXION']['Password']
        self.link = config['CONNEXION']['Link']
        self.historyPath = config['DIRECTORIES']['History']
        self.startDate = config['DATA']['StartDate']
        
    def searchCopernicus(self,startDate,footprint,sentinelType):
        if sentinelType == '1':
            products = self.api.query(footprint,date=(startDate, 'NOW'),platformname='Sentinel-'+sentinelType,order_by='IngestionDate',producttype='GRD')
        else:
            products = self.api.query(footprint,date=(startDate, 'NOW'),platformname='Sentinel-'+sentinelType,cloudcoverpercentage=(0, 0),order_by='IngestionDate')
        return products
        
    def downloadAndTreatProduct(self, product,geojson,platform):
        print("Downloading the S"+platform+" image")
        productId = product['uuid']
        productTitle = product['title']
        self.api.download(productId,'./workdir')
        print("Download finished, treating...")
        pathToZip = './workdir/'+productTitle+'.zip'
        
        if(platform == '1'):
            treatS1.treatS1(pathToZip,productTitle,geojson)
        else:
            sentinel2_data_processing.main_sentinel_2(pathToZip,'./workdir/',geojson,productTitle)
        
        print("Done.. Not releasing workdir going to sleep")
        time.sleep(100000)
        
        
        print("S"+platform+" treatment done. Releasing workdir...")
        os.system("rm -rf "+os.getcwd()+"/workdir")
        os.makedirs(os.getcwd()+'/workdir')

        print("Updating history")
        # Update history
        with open (self.historyPath, 'r+b') as fp:
            try:
                historyList = pickle.load(fp)
            except EOFError:
                historyList = []
                
            historyList.append(product)
            pickle.dump(historyList, fp)
            
        print("Done.")
        
    def queryImagesByPlatform(self,startDate,platform):
        for locationIndex in range(len(self.geoJSONList)):
            print("Querying all S"+platform+ "images for location :",self.geoJSONList[locationIndex],"since: ", startDate)
            products = self.searchCopernicus(startDate,self.footprints[locationIndex],platform)
            
            if(len(products) > 0):
                with open(self.historyPath,'w+') as fp: # Creates history if it was deleted
                    fp.close()
                with open (self.historyPath, 'r+b') as fp:
                    try:
                        historyList = pickle.load(fp)
                    except EOFError:
                        historyList = []
                        
                for uuid in products:
                    simpleDict = {'uuid':uuid, 'title':products[uuid]['title']}
                    if simpleDict not in historyList:
                        print("Found an image that is not treated : ", simpleDict['title'])
                        self.downloadAndTreatProduct(simpleDict,self.geoJSONList[locationIndex],platform)
                        print("DEBUG MODE, done treating, check outputs, going to sleep")
                        time.sleep(1000000)
                            
            else:
                print("No images found!")
        
    def start(self):
        if not self.ignoreStart:
            print("ignoreStart == False, will search for old images since : ", self.startDate)
            self.queryImagesByPlatform(self.startDate,'1')
            self.queryImagesByPlatform(self.startDate,'2')
                    
        while True:
            print("Querying new images in last 24 hours")
            startTime = datetime.datetime.now() - timedelta(hours = 24)
            self.queryImagesByPlatform(startTime,'1')
            self.queryImagesByPlatform(startTime,'2')
                        
            time.sleep(100)
        

# TEST PRODUCT 7b4a3321-4522-4ecd-bee2-72efae194be9
# test = Downloader(ignoreStart = True)
# test.startAPI()

# test = Downloader()
# startTime = datetime.datetime.now() - timedelta(hours = 1)
# pdcts = test.searchCopernicus(startDate = startTime)

test = Downloader(ignoreStart=True)
test.start()














