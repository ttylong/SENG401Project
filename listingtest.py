from pymongo import MongoClient
from pprint import pprint
import json

# connect to mongoDB
client = MongoClient("mongodb+srv://auccibids:Seng401!@aucci.eqyli.mongodb.net/aucciDB")
db = client.aucciDB
user = db.users
listing = db.listings

# for now assume the user exists, no implementation to handle non user yet
# another assumption, im using the mongo generated IDs for a collection. i dont know if that means the same ID can be repeated across collections, but im assuming no here
doc = user.find_one({"username" : "rapper"})
print(doc)
uniqueid = doc["_id"]

newlisting = {
    "useruniqid" : uniqueid,
    "item" : "Guccibag"

}

listing.insert_one(newlisting)


