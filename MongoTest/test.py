
from pymongo import MongoClient
from pprint import pprint
import json
client = MongoClient("mongodb+srv://auccibids:Seng401!@aucci.eqyli.mongodb.net/aucciDB")
from bson.objectid import ObjectId
import pprint
db = client.aucciDB
user = db.users
listing = db.listings

username = "test"
username1 = "noel"
doc = listing.find_one({"username" : username})
doc1 = listing.find_one({"username" : username1})
print(doc)
print(doc1)

if doc == None:
    print("nothing")

id = doc1["_id"]
print(id)

# id = "62329e1f7f28e4edf0400c9c"

new = listing.find_one({"_id": ObjectId(id)})
print(new)

jsonitem = {
    'listingid' : id,
    'highestbid' : 0,
    'highestbidder' : None,
    'bidders' : {

    }
}

pprint.pprint(jsonitem)