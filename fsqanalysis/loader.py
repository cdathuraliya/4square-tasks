# -*- coding: utf-8 -*-
import foursquare
from pymongo import MongoClient
import csv
import sys
reload(sys)


sys.setdefaultencoding('utf-8')


c = MongoClient()
fsqdb = c.fsqdb
ctgys= fsqdb.categories
vns = fsqdb.venues


with open('credentials.txt', 'r') as f:
       credentials = []
       for i, line in enumerate(f):
             values = line.rstrip('\r\n').split(",")

client = foursquare.Foursquare(client_id=values[0]
                    , client_secret=values[1])


def setup_category(category,parents,ctgys_col):
    ctgys_col .update({'category': category['name']},{"$set" :{'parents' : parents,'id' : category['id']}},upsert = True)
    new_parents = list(parents)
    new_parents.append(category['name'])
    if 'categories' in category.keys():
        for sub in category['categories']:
            setup_category(sub,new_parents,ctgys_col)


def get_venues():
    with open('cmb_grid_centroids.csv', 'rb') as csvfile:
        locreader =csv.DictReader(csvfile)
        for row in locreader:
          print(row)
          venueResponse = client.venues.search(params={'ll': row['latitude']+','+row['longitude'],'radius': 715,'intent':'browse'})
          venues=venueResponse['venues']
          for venue in venues:
              vns.update({'id': venue['id']},venue,upsert = True)


def generate_venue_list():
    venues = vns.find()
    for venue  in venues:
        for category in venue['categories']:
            if category['primary']==True:
                ctgy = category['name']

        p_ctgy = ''
        try:
            p_ctgy = ctgys.find({'category' : ctgy})[0]['parents'][0]
        except IndexError:
            p_ctgy = ctgy
            print 'top level category'

        venue_str = '"'+venue['name']+'",'+'%5f'% venue['location']['lat']+','+'%5f'% venue['location']['lng']+',"'+ctgy+'","'+p_ctgy+'",'+u','.join((str(venue['stats']['checkinsCount']),str(venue['stats']['usersCount']))).encode('utf-8')
        with open('venues.csv','a') as file:
            file.write(venue_str+'\n')


#flow
categoryResponse = client.venues.categories()
for category in categoryResponse['categories']:
    setup_category(category,[],ctgys)

get_venues()
generate_venue_list()
