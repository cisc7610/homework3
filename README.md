# Homework 3: MongoDB database of image analysis from Google Cloud Vision API
### Due: November 12, 2018
### Prof Michael Mandel `mim@sci.brooklyn.cuny.edu`

## Introduction

For this assignment, you will be interacting with a set of JSON documents in 
MongoDB. The JSON documents are the output of the Google Cloud Vision API applied 
to images returned from a Flickr API query for interesting images related
to the text "New York".

I have provided starter code in python, but you may will write code in a language
of your choice (Python, Java, Bash, etc) to load the JSON into the database
and query it. You will submit your code, the output of your queries, and a brief
report describing your approach.


### Install and setup MongoDB

1. Install MongoDB Community Edition for your platform following the instructions on
   https://docs.mongodb.com/manual/administration/install-community/ 
1. Follow the instructions on the same page to run `mongod` and a `mongo` shell


### Install `pymongo` driver

Use `pip` to install the `pymongo` package:

```bash
pip install pymongo
```

The following code should run from the commandline and print "Worked!" without generating any errors.  If it doesn't, then you have a problem with your python configuration or the installation of the `pymongo` package.

```bash
python -c 'import pymongo; print("Worked!")'
```


### Introduction to the data (same as homeworks 1 and 2)

The data is the same as for homeworks 1 and 2.  It is provided again in this repository in the `data/` directory for your convenience.

The file `example.json` contains
a JSON document that has all of the fields that may be present in the
individual JSON documents. Note that this is not a valid JSON document
itself because in lists it only contains a single entry followed by "...". 
Although individual JSON documents may not contain all of these fields, if
they do, they will be in the structure shown in `example.json`. 

The annotations come from the Google Cloud Vision API and are described at this link https://cloud.google.com/vision/docs/reference/rest/v1/images/annotate#AnnotateImageResponse .
I have only included the following subset of those annotations, however:

 * `landmarkAnnotations` -- identify geographical landmarks in photographs. 
   For the purposes of discussing entities in the database
   schema, this will add `Landmarks`, each of which can have zero or more
   `Locations`.
 * `labelAnnotations` -- predict descriptive labels for images. This will
   add `Label` entities to the schema.
 * `webDetection` -- predict the presence of web entities (things with
   names) in images along with pages that contain the image and other
   images that are similar. This will add `WebEntity`, `Page`, and `Image`
   entities to the schema.
   
### Introduction to starter code

All of the python code is contained in the file [`runMongo.py`](https://github.com/cisc7610/homework3/blob/master/runMongo.py).
If you have all of the necessary dependencies installed, you should be able to run the script as it is to populate the database and perform a basic aggregation query on it.

If it is working, it should print out (among other things):
```
    Query 0. List all of the Images that are associated with the
    Label with an id of "/m/015kr" (which has the description
    "bridge") ordered by the score of the association between them
    from highest score to lowest
    
***************** Aggregate pipeline ****************
[{'$unwind': '$response.labelAnnotations'},
 {'$project': {'mid': '$response.labelAnnotations.mid',
               'score': '$response.labelAnnotations.score',
               'url': 1}},
 {'$match': {'mid': '/m/015kr'}},
 {'$sort': {'score': -1}},
 {'$project': {'_id': 0}}]
********************** Results **********************
{'mid': '/m/015kr',
 'score': 0.9771296381950378,
 'url': 'https://farm4.staticflickr.com/3394/5828289828_9f9bb8a45a.jpg'}
{'mid': '/m/015kr',
 'score': 0.976899266242981,
 'url': 'https://farm5.staticflickr.com/4238/34310239173_43c51169db.jpg'}
{'mid': '/m/015kr',
 'score': 0.9619123339653015,
 'url': 'https://farm9.staticflickr.com/8618/16654352517_49b28d1dfc.jpg'}
{'mid': '/m/015kr',
 'score': 0.9518634676933289,
 'url': 'https://farm5.staticflickr.com/4254/34994427273_cac7762f17.jpg'}
{'mid': '/m/015kr',
 'score': 0.9269035458564758,
 'url': 'https://farm3.staticflickr.com/2850/32712158102_ecc8f2cec3.jpg'}
{'mid': '/m/015kr',
 'score': 0.9240447282791138,
 'url': 'https://farm8.staticflickr.com/7585/17156902591_cebb2df72c.jpg'}
{'mid': '/m/015kr',
 'score': 0.9238502979278564,
 'url': 'https://farm4.staticflickr.com/3667/12640493983_c82eb338c3.jpg'}
{'mid': '/m/015kr',
 'score': 0.9145718812942505,
 'url': 'https://farm1.staticflickr.com/590/33188022342_1eeb39857f.jpg'}
{'mid': '/m/015kr',
 'score': 0.9077485799789429,
 'url': 'https://farm4.staticflickr.com/3725/33062489846_e6c505493d.jpg'}
{'mid': '/m/015kr',
 'score': 0.800078272819519,
 'url': 'https://farm9.staticflickr.com/8574/15926352399_3ff75a6c31.jpg'}
{'mid': '/m/015kr',
 'score': 0.7653062343597412,
 'url': 'https://farm5.staticflickr.com/4282/35024953080_c130ef296c.jpg'}
*****************************************************
```

### Introduction to MongoDB

We covered an overview of what you need to know to get started with MongoDB in [lecture 4](http://m.mr-pc.org/t/cisc7610/2018fa/lecture04.pdf) starting on slide 40 of 74.  This section will provide more specifics.

MongoDB stores *documents* in *collections* within *databases*.  A document is a valid JSON object and is comparable to a row in a relational database.  A collection is a group of related documents that don't necessarily share identical schemas.  A database is a group of related collections.  For the purposes of this assignment, we will be using a single collection within a single database.  Each document will be the analysis result of one image from the Google cloud vision API.

There are three different frameworks that you can use for querying MongoDB collections (in order from simplest to most complex):
1. Single-purpose aggregation operations
1. Aggregation pipeline
1. Map-reduce framework

#### Single-purpose aggregation operations

These operations are very simple, but not very flexible.  Useful operations for the purposes of this assignment are [`db.collection.count()`](https://docs.mongodb.com/manual/reference/method/db.collection.count/#db.collection.count), which counts the number of documents in a collection, and [`db.collection.distinct()`](https://docs.mongodb.com/manual/reference/method/db.collection.distinct/#db.collection.distinct), which identifies the distinct elements in a given field. These functions that are [discussed](https://docs.mongodb.com/manual/aggregation/#single-purpose-aggregation-operations) in the official documentation.  These are called directly in python on the `collection` object.

Note that `distinct()` takes as its argument the name of a field to analyze for unique values in each document in the collection.  Dots in this name are interpreted as nested fields, so in `example.json` you could refer to the field `"response.labelAnnotations.mid"` to find all of the unique values of the `mid` fields in the `labelAnnotations` array in all documents.  This [field path syntax](https://docs.mongodb.com/manual/meta/aggregation-quick-reference/#field-path-and-system-variables) also applies to the operators in the aggregation pipeline.

#### Aggregation pipeline

Queries using the aggregation pipeline are moderately easy to write and provide a good amount of flexibility.  They are constructed using a sequence of *stages*, where each stage modifies or filters the set of documents as they "flow" through the pipeline.  See the documentation [here](https://docs.mongodb.com/manual/meta/aggregation-quick-reference/) for a full list of stages.  Note that in MongoDB syntax, stage and operator names are prefixed with the dollar sign character.  Useful stages include:

| Stage | Operation |
| ------- | ---- |
| [`$unwind`](https://docs.mongodb.com/manual/reference/operator/aggregation/unwind/#pipe._S_unwind) | Create a separate document for each value in a nested array with all other fields the same as the original document |
| [`$project`](https://docs.mongodb.com/manual/reference/operator/aggregation/project/#pipe._S_project) | Select a subset of fields from documents (also useful for renaming fields) |
| [`$match`](https://docs.mongodb.com/manual/reference/operator/aggregation/match/#pipe._S_match) | Keep only documents matching provided criteria |
| [`$group`](https://docs.mongodb.com/manual/reference/operator/aggregation/group/#pipe._S_group) | Aggregate documents on a field and summarize entries in other fields |
| [`$sort`](https://docs.mongodb.com/manual/reference/operator/aggregation/sort/#pipe._S_sort) | Order the resulting documents |
| [`$limit`](https://docs.mongodb.com/manual/reference/operator/aggregation/limit/#pipe._S_limit) | Limit the number of results returned |

Note that there are some slight differences between the pure JavaScript syntax of the stages provided in the official MongoDB documentation with the python syntax used in the python code via the `pymongo` library.  For an example aggregation query in python on our data, see [Query 0 in runMongo.py](https://github.com/cisc7610/homework3/blob/master/runMongo.py#L51).

#### Map-reduce framework

The most complex, but most flexible query framework for MongoDB is the map-reduce framework.  As discussed in [lecture 02b](http://m.mr-pc.org/t/cisc7610/2018fa/lecture02b.pdf) starting on slide 7, map-reduce consists of four stages, although you only need to write two of them: a mapper and a reducer.  In the context of `pymongo`, you write these as two JavaScript functions within strings within `bson.code.Code` objects.  See the documentation [here](https://api.mongodb.com/python/2.0/examples/map_reduce.html).

The important points are that the map JavaScript function takes no arguments, but extracts data from the `this` object.  It then uses the `emit(k,v)` function to emit as many key-value pairs as it wants to extract from each `this` object.  The reduce JavaScript function takes two arguments: a key and an array of values and summarizes this array into a single return value that will be associated with that key in the overall output.

Debugging these queries is rather cumbersome, but there is documentation for [troubleshooting the map function](https://docs.mongodb.com/manual/tutorial/troubleshoot-map-function/) and [troubleshooting the reduce function](https://docs.mongodb.com/manual/tutorial/troubleshoot-reduce-function/) in the official documentation.  These are part of the complete [Map-Reduce documentation](https://docs.mongodb.com/manual/core/map-reduce/) which might also be useful.


## Tasks

To complete the assignment, perform the following tasks.

Note that because MongoDB doesn't use an explicit schema, there is no schema creation step, as there was in homework 1.  Note also that inserting into the database is just a matter of inserting each of the JSON documents into a single collection and I have done it for you in the `populateMongo()` function in the starter code.


### Write code to query the database

Implement the missing TODO entries in the [`queryMongo()` function](https://github.com/cisc7610/homework3/blob/master/runMongo.py#L46).
For aggregation queries, you should use the supplied [`aggregateMongoAndPrintResults()`](https://github.com/cisc7610/homework3/blob/master/runMongo.py#L164) function to query the database.  The queries should be as follows:

1. Count the total number of JSON documents in the database
2. Count the number of unique Labels, Landmarks, Locations,
   Pages, and WebEntities in the database.
3. Count the total number of unique images in the database.
   This should include both those that have been directly submitted
   to the google cloud vision API as well as those that are referred
   to in the returned analyses.  
4. List the 10 most frequent WebEntities that are applied
   to the same Images as the Label with an id of "/m/015kr" (which
   has the description "bridge"). List them in descending order of
   the number of times they appear together, followed by their entityId
   alphabetically
5. Find Images associated with Landmarks that are not "New
   York" (id "/m/059rby") or "New York City" (id "/m/02nd_") with
   an association score of at least 0.6 ordered alphabetically by
   landmark description and then by image URL.
6. List the 10 Labels that have been applied to the most
   Images along with the number of Images each has been applied to
   sorted by the number of Images each has been applied to from
   most to least.
7. List the 10 Pages that are linked to the most Images
   through the webEntities.pagesWithMatchingImages JSON property
   along with the number of Images linked to each one. Sort them by
   count (descending) and then by page URL.
8. List the 10 pairs of Images that appear on the most
   Pages together through the webEntities.pagesWithMatchingImages
   JSON property. Order them by the number of pages that they
   appear on together (descending), then by the URL of the
   first. Make sure that each pair is only listed once regardless
   of which is first and which is second.


### Update the file README.md in this repository with a description of your approach and code (here)

 1. Describe the language that you implemented your code in
 1. Describe any problems that you ran into in the course of this project
 1. Include instructions for how I can run your code to populate my mongo database and to query it
 1. Paste the results from each of the queries
