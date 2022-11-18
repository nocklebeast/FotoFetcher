"""
This python script downloads photos from a photo set/album from flickr.com 
and the information necessary for submitting an application for copyright 
registration with the US Copyright Office for the group of published 
photos. (https://www.copyright.gov/registration/photographs/).

A spreadsheet of numbered titles, filenames, and dates of publication 
of photographs is compiled for the copyright application. Several text 
files with the titles of photos (and the number of photo titles in the 
file and the month of publication in the filename) for the online 
application are generated.

"""

# inputs to the program are
# config.txt and api_keys.txt 
# to be found at
path_to_app = 'M:\\python\\flickr'
#
# app_keys.txt contain the name of the app (registered with flickr) and it's keys.
# the keys are necessary to access the flickr api.
# app_keys.txt takes on the form
# {"App":"RegisteredAppNameHere","Key":"FlickrKeyHere","Secret":"FlickrSecretHere"}
#
# config.txt takes on the following form. 
# {"flickr_id":"12345678@N00","path_to_photos":"C:\\Users\\me\\Desktop\\flickr\\","my_photoset_id":"72177720300589225"}
# flickr_id is the user's flickr id.  The flickr photo set id may be obtained 
# from the flickr url for that photo set/album.

# info on the flickr api and python flickrapi:
# https://stuvel.eu/software/flickrapi/
# https://www.flickr.com/services/api/

# script logic:
# given a photoset id (just get it manually from the flickr website)
# get a list of photos in the photo set.
# flickr.photosets.getPhotos returns the title of the photo set and a list of photos (id's and titles)
    #foreach photo id in the set
        #flickr.photos.getInfo. returns the title and unix timestamp of original upload (and other stuff)
        #flickr.photos.getSizes. get the sizes and the corresponding url of each size for each photo
            #urllib.request.urlretrieve(url, filepath) retrieves the photo from the flickr url and saves it.

from io import DEFAULT_BUFFER_SIZE
from msilib import MSIDBOPEN_CREATEDIRECT
from msilib.schema import File
from time import strftime
import flickrapi
import json
import pandas as pd
from datetime import datetime
import urllib.request
import os
import time
import numpy as np

# open a text file in json format with flickr_id, path to photos (where downloaded) and 
# the photo set id obtained from the url of the flickr photo set
# here's the url
# https://www.flickr.com/photos/nocklebeast/albums/72177720299591991
# and that last bit, 72177720299591991, is the photo set/album id

filename = 'config.txt'
with open(path_to_app + '\\' + filename, 'r') as file:
    line = file.readline()
config = json.loads(line)
#https://www.flickr.com/services/api/explore/flickr.urls.lookupUser # one way to find flickr id.
flickr_id = config['flickr_id']
path_to_photos = config['path_to_photos']
my_photoset_id = config['my_photoset_id']
print(flickr_id, path_to_photos, my_photoset_id)

#open a text file in json format with my flickr app's keys.
path_to_file = 'M:\\python\\flickr'
filename = 'api_keys.txt'
with open(path_to_file + '\\' + filename, 'r') as file:
    line = file.readline()
app_keys = json.loads(line)
app_name = app_keys['App']
api_key = app_keys['Key']
api_secret = app_keys['Secret']

#open flickr api.  choose parsed-json as return format.
flickr = flickrapi.FlickrAPI(api_key, api_secret, format='parsed-json' )

# We will need to get several pages... 
# max photos per_page is 500.
# our target sets for the copyright office may have up to 750 photos.
pageSize = 500
set_photos = flickr.photosets.getPhotos(user_id= flickr_id, photoset_id= my_photoset_id, per_page=pageSize, page=1)
# returns a dictionary with keys: photoset, stat.  The value corresponding to the photoset key is a dictionary.
# the photoset dictionary has a number of keys such as 'photo', 'page', 'perpage', 'pages', 'title'
# 'total', 'title'
#print(set_photos)
#let's grab some stuff about the photo set/album.
iPage = int(set_photos['photoset']['page'])
perPage = int(set_photos['photoset']['perpage'])
nPages = int(set_photos['photoset']['pages']) #the number of pages needed to fetch the entire album.
album_title = set_photos['photoset']['title']
album_title.strip()

#create a directory for downloaded info and photos within path_to_photos named after the album_title.
path = os.path.join(path_to_photos, album_title)
try:
    os.makedirs(path, exist_ok = True)
    print("Directory '%s' created successfully" % album_title)
except OSError as error:
    print("Directory '%s' can not be created" % album_title)

#create 2nd directory for photos.
path = os.path.join(path, album_title)
try:
    os.makedirs(path, exist_ok = True)
    print("Directory '%s' created successfully" % album_title)
except OSError as error:
    print("Directory '%s' can not be created" % album_title)

total_album_photos = int(set_photos['photoset']['total'])
#print(iPage, perPage, nPages, album_title, total_album_photos)

#set_photos['photoset']['photo'] is a list of dictionaries, 
#with each list member/dictionary representing a single photo.
lstPhotoSet = set_photos['photoset']['photo']
#keys of interest in the individual photo dictionaries: id (id of the photo), title, ispublic.
#print(lstPhotoSet[0]['id'])
#print(lstPhotoSet[0]['title'])

#get additional pages if necessary and extend to the list of photos (we already have the first page)
FullPhotoSet = []
FullPhotoSet.extend(lstPhotoSet)
if iPage < nPages:
    for jPage in range(iPage+1 , nPages+1):
        set_photos = flickr.photosets.getPhotos(user_id= flickr_id, 
                                                photoset_id= my_photoset_id, 
                                                per_page= pageSize, page= jPage)
        lstPhotoSet = set_photos['photoset']['photo']
        FullPhotoSet.extend(lstPhotoSet)

#convert a list of dictionaries into a datafame!
dfPhotoSet = pd.DataFrame(FullPhotoSet)
#drop any non-public photos,
#without logging in as a flickr user, can only get public photos,
#but drop just in case (keep public photos)
dfPhotoSet = dfPhotoSet.loc[ dfPhotoSet['ispublic'] == 1 ]
#only need id and title from this dataframe.
dfPhotoSet = dfPhotoSet[['id','title']]
dfPhotoSet = dfPhotoSet.rename(columns={'id':'photoId'})

################################# get info about each photo in the photo set/album. ###########
#foreach photo in the set
    #flickr.photos.getInfo. returns the title and unix timestamp of original upload (and other stuff)
    #check out https://www.flickr.com/services/api/explore/flickr.photos.getInfo
    #flickr.photos.getSizes. get the sizes and the corresponding url of each size for each photo
    #check out https://www.flickr.com/services/api/explore/flickr.photos.getSizes
        #then use the url and urllib to download the photo later on.
print("")
print("get information about the photos in the album: " + album_title)
dfAllPhotoDetails = pd.DataFrame()
aFailedGetPhotos = []
aFailedGetSizes = []
nGetInfos = 0
nPhotoSet = len(dfPhotoSet)
for index, row in dfPhotoSet.iterrows():
    photoId = row['photoId']
    nGetInfos = nGetInfos + 1
    print(photoId, nGetInfos, "/", nPhotoSet)
    getInfoSuccess = 0
    nTries = 0
    maxTries = 5
    while getInfoSuccess == 0 & nTries <= maxTries:
        nTries = nTries + 1
        try:
            photoInfo = flickr.photos.getInfo(photo_id= photoId)  ### get info on a single photos.
            getInfoSuccess = 1
        except:
            if nTries <= maxTries:
                time.sleep(3)
            else:
                aFailedGetPhotos.append(photoId)
                print("failed get photo photo_id's: ", aFailedGetPhotos)

    #photoInfo is a dictionary. with various dictionaries within that too.
    #the item corresponding to the "photo" key is a dictonary with the 'dateuploaded' value we wish for.
    photoInfo_photo = photoInfo['photo']
    dateuploaded = int(photoInfo['photo']['dateuploaded'])
    FullDatePublished = datetime.date(datetime.fromtimestamp(dateuploaded)) #defaults to local time on machine (not utc)
    MonthYear = FullDatePublished.strftime('%b') + '-' + FullDatePublished.strftime('%Y')  #Aug-2022 format.
    Month = int(FullDatePublished.month)
    sMonth = FullDatePublished.strftime('%b')
    realname = photoInfo['photo']['owner']['realname']

    getSizesSuccess = 0
    nTries = 0
    while getSizesSuccess == 0 & nTries <= maxTries:
        nTries = nTries + 1
        try:
            photoSize = flickr.photos.getSizes(photo_id= photoId) # get sizes (and urls) for a single photo
            getSizesSuccess = 1
        except:
            if nTries <= maxTries:
                time.sleep(3)
            else:
                aFailedGetSizes.append(photoId)
                print("failed get sizes photo_id's: ", aFailedGetPhotos)

    #print(photoSize) #list of all the sizes available. list of json strings
    listPhotoSizes = photoSize['sizes']['size']
    #print(listPhotoSizes)
    dfPhotoSizes = pd.DataFrame(listPhotoSizes)
    #print(dfPhotoSizes)
    dfDesiredSize = dfPhotoSizes.loc[ dfPhotoSizes['label'] == 'Medium 800' ]
    sSizeLabel = '_m'
    # if the original size is too small so that a medium photos (width 800 pixels) doesn't exist
    # older photos won't have the 800 size.... try 640 instead.... then try original size.
    if len(dfDesiredSize) == 0 :
        dfDesiredSize = dfPhotoSizes.loc[ dfPhotoSizes['label'] == 'Medium 640' ]
        sSizeLabel = '_m'   
    #500 size even older than 640 in flickr history.
    if len(dfDesiredSize) == 0 :
        dfDesiredSize = dfPhotoSizes.loc[ dfPhotoSizes['label'] == 'Medium' ]
        sSizeLabel = '_m'   
    # the original size may always exist. Get that instead.
    if len(dfDesiredSize) == 0 :
        dfDesiredSize = dfPhotoSizes.loc[ dfPhotoSizes['label'] == 'Original' ]
        sSizeLabel = '_o'
    url = dfDesiredSize.iloc[0]['source']
    media = dfDesiredSize.iloc[0]['media']
    # this will give a unique filename (even with two photos with the same title)
    # by adding the unique flickr photoId.
    sFilename = row['title'] + '_' + str(photoId) + sSizeLabel
    # strip file name of any weird characters.
    sFilename.strip() #trim whitepace
    badCharacters = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for badCh in badCharacters:
        sFilename = sFilename.replace(badCh,'')
    
    mycolumns = ['photoId', 'Title of Photograph', 'Month', 'sMonth', 'dateuploaded',  'Full Publication Date',  
                'Month/Year of Publication','owner', 'size', 'url', 'media', 'File Name of Photograph']
    myvalues = [photoId, row['title'], Month, sMonth, dateuploaded, FullDatePublished,  MonthYear, realname, sSizeLabel, url, media, sFilename]
    dfMyPhoto = pd.DataFrame([myvalues],columns=mycolumns)
    dfAllPhotoDetails = pd.concat([dfAllPhotoDetails,dfMyPhoto], ignore_index=True)
    #print(dfMyPhoto)

#print(dfAllPhotoDetails.head())

#merge with dfPhotoSet, to make sure all the photos are public (dfPhotoSet has private photos weeded out)
#print(dfPhotoSet.head())
dfFullPhotoSet = pd.merge(dfPhotoSet, dfAllPhotoDetails, on='photoId', how='inner' )
dfFullPhotoSet.sort_values(by=['Full Publication Date','File Name of Photograph'], inplace=True)

#keep photos that are photos (not videos)
dfFullPhotoSet = dfFullPhotoSet.loc[ dfFullPhotoSet['media'] == 'photo' ]
print(dfFullPhotoSet.tail())



####################### now prepare materials for submission to eco U.S. copyright office website.  ####
MaxTitleLength = 1990 #eco website says 1995
#make spreadsheet
#make titles files.
sTitles = ""
nPhotos = 0
nTitlesFiles = 0
FileName = ""

lastMonth = dfFullPhotoSet.loc[0]['sMonth']
last_num_month = dfFullPhotoSet.loc[0]['Month']
for index, row in dfFullPhotoSet.iterrows():
    currentMonth = row['sMonth']
    current_num_month = row['Month']
    if (len(sTitles) + len(row['Title of Photograph']) < MaxTitleLength) and (lastMonth == currentMonth):
        sTitles = sTitles + row['Title of Photograph'] + ", \n"
        nPhotos = nPhotos + 1
    else:
        #write the title file to disk and reset title info.
        nTitlesFiles = nTitlesFiles + 1
        FileName = album_title + '_' + str(nTitlesFiles).zfill(3) + '_' 
        FileName = FileName + str(last_num_month).zfill(2) + lastMonth + '_'
        FileName = FileName + str(nPhotos).zfill(3) + '_photos.txt'
        destination_dir = path_to_photos + album_title + '\\' 
        with open( destination_dir + FileName, 'w') as title_file:
            title_file.write(sTitles)
        #reset sTitles. with current row.
        sTitles = "" + row['Title of Photograph'] + ", \n"
        nPhotos = 1
    lastMonth = currentMonth
    last_num_month = current_num_month 

#get last titles that didn't run out of month or space, if it exists.
if len(sTitles) > 0:
    nTitlesFiles = nTitlesFiles + 1
    FileName = album_title + '_' + str(nTitlesFiles).zfill(3) + '_' 
    FileName = FileName + str(last_num_month).zfill(2) + lastMonth + '_'
    FileName = FileName + str(nPhotos).zfill(3) + '_photos.txt'
    destination_dir = path_to_photos + album_title + '\\' 
    with open( destination_dir + FileName, 'w') as title_file:
        title_file.write(sTitles)

if len(aFailedGetPhotos) > 0 | len(aFailedGetSizes) > 0:
    print("failed get phtotos photo id's: ", aFailedGetPhotos)
    print("failed get sizes photo_id's: ", aFailedGetPhotos)

###################### let's write the speadsheet for eco copyright office here.
#columns to keep for pretty output.
dfPretty = dfFullPhotoSet.copy(deep=True)
dfPretty.drop(['title', 'photoId', 'Month', 'sMonth','dateuploaded','media','url','owner','size'], axis= 1, inplace=True)
dfPretty['Photograph Number'] = np.arange(len(dfPretty)) + 1

dfPretty = dfPretty.reindex(columns=['Photograph Number', 'Title of Photograph', 'File Name of Photograph',
                                     'Month/Year of Publication', 'Full Publication Date'])

print(dfPretty.head())
maxPretty = dfPretty.max()
minPretty = dfPretty.min()
minPublicationDate = minPretty['Full Publication Date']
maxPublicationDate = maxPretty['Full Publication Date']

csv_path = path_to_photos + album_title + '\\'
#save csv as text file.  This doesn't have extra line feeds in the file.
dfPretty.to_csv(csv_path + 'raw csv data' + '.txt', index=False, sep='\t', encoding='utf-8')
with open(csv_path + 'raw csv data' + '.txt', 'r', encoding='utf8') as txtfile:
    csv_data = txtfile.read()

#print(csv_data)
### for some reason this method to get csv_data produces extra line feeds, and looks icky.
#csv_data = dfPretty.to_csv(index=False, sep='\t', encoding='utf-8')
#print(csv_data)


#add places to put group title and case registration number from the copyright office in the excel file.
sAllTheTitles = "title of the group registration of published photos:" + '\t' + '\n' \
        + "This is the complete list of photgraphs for" + '\t' + "[insert case registration number here, remember to place # in file name.]" + '\t' + '\n' \
        + "total number of photos: " + '\t' + str(len(dfPretty)) + '\n' \
        + "earliest publication date: " + '\t' + minPublicationDate.strftime("%b %d %Y") + '\n' \
        + "latest publication date: " + '\t' + maxPublicationDate.strftime("%b %d %Y") + '\n' \

finished_spreadsheet = sAllTheTitles + '\n\n' + csv_data
with open(csv_path + album_title + '.txt', 'w') as txtfile:
    txtfile.write(finished_spreadsheet)

#print(finished_spreadsheet)

#convert finished_spreadsheet text file into an xlsx file.
import openpyxl
import csv
wb = openpyxl.Workbook()
ws = wb.active
with open(csv_path + album_title + '.txt') as f:
    reader = csv.reader(f, delimiter='\t')
    for row in reader:
        ws.append(row)
wb.save(csv_path + album_title + '.xlsx')


### remove temp txt files.
remove_me = csv_path + 'raw csv data' + '.txt'
if os.path.exists(remove_me):
  os.remove(remove_me)
remove_me = csv_path + album_title + '.txt'
if os.path.exists(remove_me):
  os.remove(remove_me)


############################### get photos from flickr ##############################################
#for each photo in dfFullPhotoSet, fetch the medium sized image from flickr.com using the url
#and save the file... and embed a few things in the exif data. skip exif for now.
#notes on exif https://www.linkedin.com/pulse/manipulating-image-exif-data-python-natasha-kacoroski/
destination_dir = path_to_photos + album_title + '\\' + album_title + '\\' 
print("")
print("download photos from flickr and save to... ")
print(destination_dir)

#get and save the photos (jpg) from flickr
nPhotoSet = len(dfFullPhotoSet)
nURLPhotos = 0
for index, row in dfFullPhotoSet.iterrows():
    url = row['url']
    sFilename = row['File Name of Photograph'] + '.jpg'
    nURLPhotos = nURLPhotos + 1
    print(nURLPhotos, "/", nPhotoSet, url)
    filepath = os.path.join(destination_dir, sFilename)

    #urllib.request.urlretrieve(url, filepath)
    aFailedSaveJPGs = []
    saveJPGSuccess = 0
    nTries = 0
    maxTries = 5
    while saveJPGSuccess == 0 & nTries <= maxTries:
        nTries = nTries + 1
        try:
            urllib.request.urlretrieve(url, filepath)
            saveJPGSuccess = 1
        except:
            if nTries <= maxTries:
                time.sleep(3)
            else:
                aFailedSaveJPGs.append(sFilename)
                print("failed get jpgs filename's: ", aFailedSaveJPGs)
    #don't bother with additional exif for now.. the copyright/artist info is in the flickr photos.


if len(aFailedGetPhotos) > 0:
    print("failed get photos photo id's: ", aFailedGetPhotos)

if len(aFailedGetSizes) > 0:
    print("failed get sizes photo_id's: ", aFailedGetPhotos)

if len(aFailedSaveJPGs) > 0:
    print("failed get jpgs filename's: ", aFailedSaveJPGs)