#https://stuvel.eu/flickrapi-doc/2-calling.html
#https://python-flickr.readthedocs.io/en/latest/
import flickrapi
import json
import re

flickr_id = '95394384@N00'

path_to_file = 'M:\\python\\flickr'
filename = 'api_keys.txt'
with open(path_to_file + '\\' + filename, 'r') as file:
    line = file.readline()

#print(line)
app_keys = json.loads(line)
print(app_keys)

#https://stuvel.eu/flickrapi-doc/2-calling.html 
app_name = app_keys['App']
api_key = app_keys['Key']
api_secret = app_keys['Secret']

#need to convert string to unicode for the flickrapi ????
#??? don't seem to need this for the flickr api.
# using sub() to perform substitutions, ord() for conversion.
#res = (re.sub('.', lambda x: r'\u % 04X' % ord(x.group()), api_key))
#print("The unicode converted String : " + str(res)) 

flickr = flickrapi.FlickrAPI(api_key, api_secret, format='parsed-json' )
print(flickr)
photos = flickr.photos.search(user_id=flickr_id, per_page='10')
print(type(photos))
print(len(photos))
#print(photos)
print(photos.keys())

#retrieves info on first 500 photosets by default.
sets = flickr.photosets.getList(user_id=flickr_id)
#sets only has one key/item in the dictionary.
print(type(sets))
print(len(sets))
print(sets.keys())
#title of first photoset (most recent) in the ?list?
title  = sets['photosets']['photoset'][0]['title']['_content']
print(sets['photosets']['photoset'][0])
print(len(sets['photosets']['photoset']))

"""
for k,v in sets.items():
  print(k, v) 
"""



#given a photoset id (just get it manually from the flickr website)
#get a list of photos in the photo set.
#flickr.photosets.getPhotos returns the title of the photo set and a list of photos (id's and titles)
    #foreach photo in the set
        #flickr.photos.getInfo. returns the title and unix timestamp of original upload (and other stuff)
        #flickr.photos.getSizes. get the sizes and the corresponding url of each size for each photo
            #use the url and urllib to download the photo

