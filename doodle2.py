
from time import strftime
import flickrapi
import json
import pandas as pd
from datetime import datetime
import urllib.request
import os
#from pyexif import pyexif
from exif import Image as ExifImage
from PIL import Image as PillowImage
from PIL import ExifTags


image_path = 'C:\\Users\\mark\\Desktop\\bulkr\\Laguna Creek\\laguna_Q1000781_52259797716_m.jpg'

pillow_img = PillowImage.open(image_path)
pillow_img_exif = pillow_img.getexif()
print(pillow_img_exif)

with open(image_path, 'rb') as img_file:
    exif_img = ExifImage(img_file)

print(exif_img)

print(exif_img.artist)
print(exif_img.copyright)

exif_img.title = "my title"
exif_img.flickrid = "123469"
print(exif_img.title)
print(exif_img.flickrid)


print(exif_img.list_all())

with open(image_path, 'wb') as new_image_file:
    new_image_file.write(exif_img.get_file())






"""
import exifread
#pip install exifread

image_path = 'C:\\Users\\mark\\Desktop\\bulkr\\Laguna Creek\\laguna_Q1000781_52259797716_m.jpg'

f = open(image_path, 'rb')

# Return Exif tags
tags = exifread.process_file(f)

print(tags)
"""





"""
from PIL import Image
import PIL.ExifTags
image_path = 'C:\\Users\\mark\\Desktop\\bulkr\\Laguna Creek\\laguna_Q1000781_52259797716_m.jpg'
#pillow
image = Image.open(image_path)
exif_data_PIL = image._getexif()
exif_data = {}

for k, v in PIL.ExifTags.TAGS.items():

    if k in exif_data_PIL:
        value = exif_data_PIL[k]
    else:
        value = None

    if len(str(value)) > 64:
        value = str(value)[:65] + "..."

    if value != None:
        exif_data[v] = {"tag": k,
                        "raw": value,
                        "processed": value}

print(exif_data)



#print('exifData = ' + str(exifData))

#im.save(fileName, exif=exifdata)
"""








"""
print(image.size)
print(image.mode)
print(image.info['exif'])
"""



#metadata = pyexif.ExifEditor(image_path)
#print(metadata)
#metadata.getTags()
#print(metadata)
