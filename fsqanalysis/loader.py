# -*- coding: utf-8 -*-

import foursquare
from pymongo import MongoClient

c = MongoClient() 
fsqdb = c.fsqdb
ctgys= fsqdb.categories
venues = fsqdb.venues

with open('credentials.txt', 'r') as f:
       credentials = []
       for i, line in enumerate(f):
             values = line.rstrip('\r\n').split(",")

client = foursquare.Foursquare(client_id=values[0]
                    , client_secret=values[1])

#venues = client.venues.search(params={'ll': '6.9344,79.8428'})
categoryResponse = client.venues.categories()

def setup_category(category,parents,ctgys_col):
    parents.append(category['name'])
    if 'categories' in category.keys():
        for sub in category['categories']:        
            setup_category(sub,parents,ctgys_col)    
    else:        
        ctgys_col .update({'user': category['name']},{"$set" :{'parents' : parents}},upsert = True)

for category in categoryResponse['categories']:
    setup_category(category,[],ctgys)


    
        

