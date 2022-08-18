#given a photoset id (just get it manually from the flickr website)
#get a list of photos in the photo set.
#flickr.photosets.getPhotos returns the title of the photo set and a list of photos (id's and titles)
    #foreach photo in the set
        #flickr.photos.getInfo. returns the title and unix timestamp of original upload (and other stuff)
        #flickr.photos.getSizes. get the sizes and the corresponding url of each size for each photo
            #use the url and urllib to download the photo

#https://stuvel.eu/software/flickrapi/
#https://www.flickr.com/services/api/
#https://stuvel.eu/flickrapi-doc/2-calling.html#response-format-json
#https://stackoverflow.com/questions/41139124/how-to-download-photos-from-flickr-by-flickr-api-in-python-3
#https://stuvel.eu/flickrapi-doc/7-util.html#walking-through-all-photos-in-a-set
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


#just hard code my flickr id for now.
flickr_id = '95394384@N00'
path_to_photos = 'C:\\Users\\mark\\Desktop\\bulkr\\'
#let's just hard code a flickr album / photoset id for now.
# here's the url
# https://www.flickr.com/photos/nocklebeast/albums/72177720299591991
# and that last bit is the id
my_photoset_id = 72177720299591991  #750 photos
#my_photoset_id = 72177720301027838  #45 photos
my_photoset_id = 72177720300589225 #5 phtoos.

#open a text file in json format with my flickr app's keys.
path_to_file = 'M:\\python\\flickr'
filename = 'api_keys.txt'
with open(path_to_file + '\\' + filename, 'r') as file:
    line = file.readline()
app_keys = json.loads(line)
#print(app_keys)

app_name = app_keys['App']
api_key = app_keys['Key']
api_secret = app_keys['Secret']

#open flickr api.  choose parsed-json as return format.
flickr = flickrapi.FlickrAPI(api_key, api_secret, format='parsed-json' )
#print(flickr)

#note will need to get several pages... max per_page is 500, our target sets may have up to 750 photos.
pageSize = 500
set_photos = flickr.photosets.getPhotos(user_id= flickr_id, photoset_id= my_photoset_id, per_page=pageSize, page=1)
#returns a dictionary with keys: photoset, stat.  The value corresponding to the photoset key is a dictionary.
#the photoset dictionary has a number of keys such as 'photo', 'page', 'perpage', 'pages', 'title'
# 'total', 'title'
#print(set_photos)
#let's grab some stuff about the photo set/album.
iPage = int(set_photos['photoset']['page'])
perPage = int(set_photos['photoset']['perpage'])
nPages = int(set_photos['photoset']['pages']) #the number of pages need to fetch the entire album.
album_title = set_photos['photoset']['title']
album_title.strip()

path = os.path.join(path_to_photos, album_title)
try:
    os.makedirs(path, exist_ok = True)
    print("Directory '%s' created successfully" % album_title)
except OSError as error:
    print("Directory '%s' can not be created" % album_title)

#2nd directory for photos.
path = os.path.join(path, album_title)
try:
    os.makedirs(path, exist_ok = True)
    print("Directory '%s' created successfully" % album_title)
except OSError as error:
    print("Directory '%s' can not be created" % album_title)

total_album_photos = int(set_photos['photoset']['total'])
print(iPage, perPage, nPages, album_title, total_album_photos)

#set_photos['photoset']['photo'] is a list of dictionaries, 
#with each list member/dictionary representing a single photo.
lstPhotoSet = set_photos['photoset']['photo']
#keys of interest in the individual photo dictionaries: id (id of the photo), title, ispublic.
#print(lstPhotoSet[0]['id'])
#print(lstPhotoSet[0]['title'])

FullPhotoSet = []
FullPhotoSet.extend(lstPhotoSet)
print(len(FullPhotoSet))

if iPage < nPages:
    #get the other pages and extend to the list of photos (we already have page 1)
    for jPage in range(iPage+1 , nPages+1):
        set_photos = flickr.photosets.getPhotos(user_id= flickr_id, 
                                                photoset_id= my_photoset_id, 
                                                per_page= pageSize, page= jPage)
        lstPhotoSet = set_photos['photoset']['photo']
        FullPhotoSet.extend(lstPhotoSet)

print(len(FullPhotoSet))

#convert a list of dictionaries into a datafame!
dfPhotoSet = pd.DataFrame(FullPhotoSet)
#drop any non-public photos,
#without logging in as a flickr user, can only get public photos,
#but drop just in case (keep public photos)
dfPhotoSet = dfPhotoSet.loc[ dfPhotoSet['ispublic'] == 1 ]
#only need id and title from this dataframe.
dfPhotoSet = dfPhotoSet[['id','title']]
dfPhotoSet = dfPhotoSet.rename(columns={'id':'photoId'})
print(dfPhotoSet.head())

#foreach photo in the set
    #flickr.photos.getInfo. returns the title and unix timestamp of original upload (and other stuff)
    #check out https://www.flickr.com/services/api/explore/flickr.photos.getInfo
    #flickr.photos.getSizes. get the sizes and the corresponding url of each size for each photo
    #check out https://www.flickr.com/services/api/explore/flickr.photos.getSizes
        #use the url and urllib to download the photo

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

    #photoInfo  is a dictionary. with various dictionaries within that too.
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
    #if the original size is too small so that a medium photos (width 500 pixels) doesn't exist
    # the original size will always exist.
    if len(dfDesiredSize) == 0 :
        dfDesiredSize = dfPhotoSizes.loc[ dfPhotoSizes['label'] == 'Original' ]
        sSizeLabel = '_o'
    url = dfDesiredSize.iloc[0]['source']
    media = dfDesiredSize.iloc[0]['media']
    sFilename = row['title'] + '_' + str(photoId) + sSizeLabel
    #strip file name of any weird characters.
    sFilename.strip() #trim whitepace
    #badCharacters = ['#', '%', '&', '{', '}', '\\', '$', '!', "'", '<', '>', '*', '/',  '+', '`', '|', '=', ':', '@', '?']
    badCharacters = ['<', '>', ':', '"', '\/', '\\', '|', '?', '*']
    for badCh in badCharacters:
        sFilename = sFilename.replace(badCh,'')
    
    #print(url)
    #print(dfDesiredSize)

    mycolumns = ['photoId', 'Title of Photograph', 'Month', 'sMonth', 'dateuploaded',  'Full Publication Date',  
                'Month/Year of Publication','owner', 'size', 'url', 'media', 'File Name of Photograph']
    myvalues = [photoId, row['title'], Month, sMonth, dateuploaded, FullDatePublished,  MonthYear, realname, sSizeLabel, url, media, sFilename]
    dfMyPhoto = pd.DataFrame([myvalues],columns=mycolumns)
    dfAllPhotoDetails = pd.concat([dfAllPhotoDetails,dfMyPhoto], ignore_index=True)
    #print(dfMyPhoto)

print(dfAllPhotoDetails.head())
print(len(dfAllPhotoDetails))

#merge with dfPhotoSet, to make sure all the photos are public (dfPhotoSet has private photos weeded out)
print(dfPhotoSet.head())
dfFullPhotoSet = pd.merge(dfPhotoSet, dfAllPhotoDetails, on='photoId', how='inner' )
dfFullPhotoSet.sort_values(by=['Full Publication Date','File Name of Photograph'], inplace=True)

#keep photos that are photos (not videos)
dfFullPhotoSet = dfFullPhotoSet.loc[ dfFullPhotoSet['media'] == 'photo' ]
print(dfFullPhotoSet.head())
print(dfFullPhotoSet.tail())
print(dfFullPhotoSet.index)
print(dfFullPhotoSet['sMonth'])

if len(aFailedGetPhotos) > 0 | len(aFailedGetSizes) > 0:
    print("failed get photos photo id's: ", aFailedGetPhotos)
    print("failed get sizes photo_id's: ", aFailedGetPhotos)
#######################now prepare materials for submission to eco copyright office website.
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
    if (len(sTitles) + len(row['Title of Photograph']) < MaxTitleLength) | (lastMonth != currentMonth):
        sTitles = sTitles + row['Title of Photograph'] + ", \n"
        nPhotos = nPhotos + 1
    else:
        #write the title file to disk and reset title info.
        nTitlesFiles = nTitlesFiles + 1
        FileName = album_title + '_' + str(nTitlesFiles).zfill(3) + '_' 
        FileName = FileName + str(last_num_month).zfill(2) + lastMonth + '_'
        FileName = FileName + str(nPhotos).zfill(3) + '_photos.txt'
        print(FileName)
        destination_dir = path_to_photos + album_title + '\\' 
        with open( destination_dir + FileName, 'w') as title_file:
            title_file.write(sTitles)
        #print(sTitles)
        #reset sTitles. with current row.
        sTitles = "" + row['Title of Photograph'] + ", \n"
        nPhotos = 1


#get last titles that didn't run out of month or space, if it exists.
if len(sTitles) > 0:
    nTitlesFiles = nTitlesFiles + 1
    FileName = album_title + '_' + str(nTitlesFiles).zfill(3) + '_' 
    FileName = FileName + str(current_num_month).zfill(2) + currentMonth + '_'
    FileName = FileName + str(nPhotos).zfill(3) + '_photos.txt'
    print(FileName)
    destination_dir = path_to_photos + album_title + '\\' 
    with open( destination_dir + FileName, 'w') as title_file:
        title_file.write(sTitles)
    #print(sTitles)

if len(aFailedGetPhotos) > 0 | len(aFailedGetSizes) > 0:
    print("failed get phtotos photo id's: ", aFailedGetPhotos)
    print("failed get sizes photo_id's: ", aFailedGetPhotos)

######################let's write the speadsheet for eco copyright office here.
#columns to keep for pretty output.
dfPretty = dfFullPhotoSet.copy(deep=True)
print(dfPretty.head())
dfPretty.drop(['title', 'photoId', 'Month', 'sMonth','dateuploaded','media','url','owner','size'], axis= 1, inplace=True)
dfPretty['Photograph Number'] = np.arange(len(dfPretty)) + 1

dfPretty = dfPretty.reindex(columns=['Photograph Number', 'Title of Photograph', 'File Name of Photograph',
                                     'Month/Year of Publication', 'Full Publication Date'])

maxPretty = dfPretty.max()
minPretty = dfPretty.min()
minPublicationDate = minPretty['Full Publication Date']
maxPublicationDate = maxPretty['Full Publication Date']

csv_path = path_to_photos + album_title + '\\'
#save csv file to a string, as we're going to add some special headers to the file.
csv_data = dfPretty.to_csv(index=False, sep='\t', encoding='utf-8')

#add places to put group title and case number in the excel file.
sAllTheTitles = "title of the group registration of published photos:" + '\t' + '\n' \
        + "This is the complete list of photgraphs for" + '\t' + "[insert case registration number here]" + '\t' + '\n' \
        + "total number of photos: " + '\t' + str(len(dfPretty)) + '\n' \
        + "earliest publication date: " + '\t' + minPublicationDate.strftime("%b %d %Y") + '\n' \
        + "latest publication date: " + '\t' + maxPublicationDate.strftime("%b %d %Y") + '\n' \



txt_file = sAllTheTitles + '\n\n' + csv_data
print(txt_file)

with open(csv_path + album_title + '.txt', 'w') as txtfile:
    txtfile.write(txt_file)

"""
#could try again at some point, but this output looks ugly (number formated as text and blank lines between real lines)
import openpyxl
import csv
wb = openpyxl.Workbook()
ws = wb.active
with open(csv_path + album_title + '.txt') as f:
    reader = csv.reader(f, delimiter='\t')
    for row in reader:
        ws.append(row)
wb.save(csv_path + album_title + '.xlsx')
"""

############################### get photos from flickr ##############################################
#for each photo in dfFullPhotoSet, fetch the medium sized image from flickr.com using the url
#and save the file... and embed a few things in the exif data. skip exif for now.
#notes on exif https://www.linkedin.com/pulse/manipulating-image-exif-data-python-natasha-kacoroski/

#get and save the photos (jpg) from flickr
nPhotoSet = len(dfFullPhotoSet)
nURLPhotos = 0
for index, row in dfFullPhotoSet.iterrows():
    url = row['url']
    sFilename = row['File Name of Photograph'] + '.jpg'
    nURLPhotos = nURLPhotos + 1
    print(nURLPhotos, "/", nPhotoSet, url)
    destination_dir = path_to_photos + album_title + '\\' + album_title + '\\' 
    filepath = os.path.join(destination_dir, sFilename)
    urllib.request.urlretrieve(url, filepath)
    #don't bother with additional exif for now.. the copyright/artist info is in the flickr photos.





 



    





