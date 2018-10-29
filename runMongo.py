#!/usr/bin/python3

""" Insert data from collectData.py into a mongodb database and query it.
"""

import glob
import json
import os.path
import pprint

from bson.code import Code
from pymongo import MongoClient

dataDir = "data/"
fullJsonDir = os.path.join(dataDir, "fullJson")
jsonDir = os.path.join(dataDir, "json")
jpgDir = os.path.join(dataDir, "jpg")
flickrFile = os.path.join(dataDir, "flickr.pkl")
urlFile = os.path.join(dataDir, "urls.txt")

def main():
    populateMongo(jsonDir)
    queryMongo()


def populateMongo(jsonDir, clearDb=True):
    "Load the JSON results from google into mongo"

    client = MongoClient()
    db = client.homework2
    collection = db.googleTagged

    if clearDb:
        client.homework2.googleTagged.delete_many({})

    for jsonFile in glob.glob(os.path.join(jsonDir, '*.json')):
        print("Loading", jsonFile, "into mongo")
        with open(jsonFile) as jf:
            jsonData = json.load(jf)
        key = {'url': jsonData['url']}
        collection.update_one(key, {"$set": jsonData}, upsert=True);

    print("Mongo now contains", collection.count(), "documents")


def queryMongo():
    client = MongoClient()
    db = client.homework2
    collection = db.googleTagged
    
    # Example aggregation
    desc_0 = """
    Query 0. List all of the Images that are associated with the
    Label with an id of "/m/015kr" (which has the description
    "bridge") ordered by the score of the association between them
    from highest score to lowest
    """
    pipeline_0 = [
        { "$unwind": "$response.labelAnnotations"},
        { "$project": {"url": 1,
                       "mid": "$response.labelAnnotations.mid",
                       "score": "$response.labelAnnotations.score"}},
        { "$match": {"mid": "/m/015kr"}},
        { "$sort": {"score": -1}},
        { "$project": {"_id": 0}},
    ]
    aggregateMongoAndPrintResults(pipeline_0, collection, desc_0)


    # TODO: This does not require the aggregation framework
    print("""
    Query 1. Count the total number of JSON documents in the database
    """)
    res_1 = ""
    print(res_1)


    # TODO: This does not require the aggregation framework
    desc_2 = """
    Query 2. Count the number of unique Labels, Landmarks, Locations,
    Pages, and WebEntities in the database.
    """
    # Can do everything except image URLs using distinct()
    print(desc_2)
    res_2 = ""
    print(res_2)


    # TODO: This may require the map-reduce framework
    desc_3 = """ 
    Query 3. Count the total number of unique images in the database.
    This should include both those that have been directly submitted
    to the google cloud vision API as well as those that are referred
    to in the returned analyses.  
    """
    print(desc_3)
    res_3 = ""
    print(res_3)


    # TODO: I recommend the aggregation framework for this
    desc_4 = """
    Query 4. List the 10 most frequent WebEntities that are applied
    to the same Images as the Label with an id of "/m/015kr" (which
    has the description "bridge"). List them in descending order of
    the number of times they appear together, followed by their entityId
    alphabetically
    """
    pipeline_4 = [
    ]
    aggregateMongoAndPrintResults(pipeline_4, collection, desc_4)


    # TODO: I recommend the aggregation framework for this
    desc_5 = """
    Query 5. Find Images associated with Landmarks that are not "New
    York" (id "/m/059rby") or "New York City" (id "/m/02nd_") with
    an association score of at least 0.6 ordered alphabetically by
    landmark description and then by image URL.
    """
    pipeline_5 = [
    ]
    aggregateMongoAndPrintResults(pipeline_5, collection, desc_5)


    # TODO: I recommend the aggregation framework for this
    desc_6 = """
    Query 6. List the 10 Labels that have been applied to the most
    Images along with the number of Images each has been applied to
    sorted by the number of Images each has been applied to from
    most to least.
    """
    pipeline_6 = [
    ]
    aggregateMongoAndPrintResults(pipeline_6, collection, desc_6)


    # TODO: I recommend the aggregation framework for this
    desc_7 = """
    Query 7. List the 10 Pages that are linked to the most Images
    through the webEntities.pagesWithMatchingImages JSON property
    along with the number of Images linked to each one. Sort them by
    count (descending) and then by page URL.
    """
    pipeline_7 = [
    ]
    aggregateMongoAndPrintResults(pipeline_7, collection, desc_7)
    

    # TODO: I recommend the aggregation framework for this
    desc_8 = """
    Query 8. List the 10 pairs of Images that appear on the most
    Pages together through the webEntities.pagesWithMatchingImages
    JSON property. Order them by the number of pages that they
    appear on together (descending), then by the URL of the
    first. Make sure that each pair is only listed once regardless
    of which is first and which is second.
    """
    pipeline_8 = [
    ]
    aggregateMongoAndPrintResults(pipeline_8, collection, desc_8)


def aggregateMongoAndPrintResults(pipeline, collection, desc="Running query:"):
    print()
    print(desc)
    print("***************** Aggregate pipeline ****************")
    pprint.pprint(pipeline)
    print("********************** Results **********************")
    if len(pipeline) > 0:
        for result in collection.aggregate(pipeline):
            pprint.pprint(result)
    print("*****************************************************")

        
if __name__ == '__main__':
    main()
