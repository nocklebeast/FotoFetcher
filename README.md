# FotoFetcher
fetching photos from flickr and copyright registration preparation

This python script downloads photos from a photo set/album from flickr.com and the information necessary for submitting an application for copyright registration with the US Copyright Office for the group of published photos. (https://www.copyright.gov/registration/photographs/).

A spreadsheet of numbered titles, filenames, and dates of publication of photographs is compiled for the copyright application. Several text files with the titles of photos (and the number of photo titles in the file and the month of publication in the filename) for the online application are generated.
 
More info about the flickr api and the python package can be found [here](https://stuvel.eu/software/flickrapi/)   and [here](https://www.flickr.com/services/api/).

Inputs to the program are
config.txt and api_keys.txt 
to be found at path_to_app  

app_keys.txt contain the name of the app (registered with flickr) and it's keys. The keys are necessary to access the flickr api.
app_keys.txt takes on the form
{"App":"RegisteredAppNameHere","Key":"FlickrKeyHere","Secret":"FlickrSecretHere"}

config.txt takes on the following form. 
{"flickr_id":"12345678@N00","path_to_photos":"C:\\Users\\me\\Desktop\\flickr\\","my_photoset_id":"72177720300589225"}
where flickr_id is the user's flickr id.  The flickr photo set id may be obtained 
from the flickr url for that photo set/album.

