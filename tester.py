from pymongo import MongoClient
from pprint import pprint
import json

# connect to mongoDB
client = MongoClient("mongodb+srv://auccibids:Seng401!@aucci.eqyli.mongodb.net/aucciDB")
db = client.aucciDB
user = db.users

with open('users.json') as f:
    fd = json.load(f)

print(json.dumps(fd, indent = 4, sort_keys = True))
user.insert_many(fd)
