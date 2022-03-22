# REST API endpoints for listings

from email.mime import image
import string
from pymongo import MongoClient
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from bson import ObjectId
import pyuploadcare as PuC
from pyuploadcare import Uploadcare
import json
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

connection_string = "mongodb+srv://auccibids:Seng401!@aucci.eqyli.mongodb.net/aucciDB"

def db_collection(collection):
    client = MongoClient(connection_string)
    db = client.aucciDB

    return db[collection]

# Prepares for jsonResponse
# Only works for listings
def listing_jsonify(data):
    json_data = []
    for datum in data:
        json_data.append({"_id" : str(datum['_id']), "username" : datum['username'], "item" : datum['item'], "brand" : datum['brand'], "category" : datum['category'], "gender" : datum['gender'], "size" : datum['size'], "listtime" : str(datum['listtime']), "initprice" : str(datum['initprice']), "timelimit" : str(datum['timelimit']), "image" : datum['image']})
    return json_data

# Prepares for jsonResponse
# Only works for lists of items
def categories_jsonify(data):
    json_data = []
    for datum in data:
        json_data.append({"_id" : str(datum['_id']), "name" : str(datum['name'])})

    return json_data

# GET listings by name or GET all listings
def listing(request, name = ""):
    if request.method == "GET":
        cursor = db_collection("listings")

        if name != "":
            listings = cursor.find({"item" : name})
        else:
            listings = cursor.find({})

        json_content = listing_jsonify(listings)

        return JsonResponse(json_content, safe=False)
    else:
        return HttpResponse("Unrecognized request. This URL only accepts GET methods.")

# GET listings by username
def listing_by_user(request, username = ""):
    if request.method == "GET":
        cursor = db_collection("listings")

        if username != "":
            listings = cursor.find({"username" : username})
        else:
            listings = cursor.find({"none": "none"}) # Returns empty

        json_content = listing_jsonify(listings)

        return JsonResponse(json_content, safe=False)
    else:
        return HttpResponse("Unrecognized request. This URL only accepts GET methods.")


# GET listings by category
def listing_by_category(request, category = ""):
    if request.method == "GET":
        cursor = db_collection("listings")

        if category != "":
            listings = cursor.find({"category" : category})
        else:
            listings = cursor.find({"none": "none"}) # Returns empty

        json_content = listing_jsonify(listings)

        return JsonResponse(json_content, safe=False)
    else:
        return HttpResponse("Unrecognized request. This URL only accepts GET methods.")

def listing_by_params(request, gender, brand, category, size, pcolor):
    print("in function!")
    if request.method == "GET":
        cursor = db_collection("listings")

        search_params = {}

        if gender != "null":
            search_params.update({"gender" : gender})
        elif brand != "null":
            search_params.update({"brand" : brand})
        elif category != "null":
            search_params.update({"category" : brand})
        elif size != "null":
            search_params.update({"size" : size})
        elif pcolor != "null":
            search_params.update({"primary-color" : pcolor})

        print("params")
        print(search_params)

        if search_params != []:
            listings = cursor.find(search_params)
        else:
            listings = cursor.find({}) # Returns all

        json_content = listing_jsonify(listings)

        return JsonResponse(json_content, safe=False)
    else:
        return HttpResponse("Unrecognized request. This URL only accepts GET methods.")

# DELETE listing by object id
@csrf_exempt 
def delete_listing(request, oid = ""):
    if request.method != "DELETE":
        return HttpResponse("Unrecognized request. This URL only accepts DELETE methods.")
    if oid == "":
        return HttpResponse("Specify one object to delete")
    
    cursor = db_collection("listings")

    query = { "_id": ObjectId(oid) }

    try: 
        cursor.delete_one(query)
    except:
        return HttpResponse("Something went wrong")
    else:
        return HttpResponse("Success")

# POST new listing
@api_view(['POST'])
def create_listing(request):
    if request.method != "POST":
        return HttpResponse("Unrecognized request. This URL only accepts POST methods.")

    id = db_collection("listings").insert_one(request.data).inserted_id

    return JsonResponse({"_id" : str(id)})

# UPDATE listing by id
@api_view(['POST'])
def update_listing(request, oid = ""):
    if request.method != "POST":
        return HttpResponse("Unrecognized request. This URL only accepts POST methods.")
    if oid == "":
        return HttpResponse("Specify one object to update")
    
    cursor = db_collection("listings")

    try:
        cursor.update_one({'_id':ObjectId(oid)}, {"$set": request.data}, upsert=False)
    except:
        print("Something went wrong")
        return HttpResponse("Something went wrong")
    else:
        return HttpResponse("Success")

# GET catagories
def categories(request):
    if request.method == "GET":
        cursor = db_collection("categories")

        listings = cursor.find({})

        json_content = categories_jsonify(listings)

        return JsonResponse(json_content, safe=False)
    else:
        return HttpResponse("Unrecognized request. This URL only accepts GET methods.")

@api_view(['POST'])
def up(request):
    # if imagepath == "":
    #     return HttpResponse("Specify an image path")

    if request.method == "POST":
        urls = []
        Uploadcare = PuC.Uploadcare(public_key =  '20a0df730e28f42bb662', secret_key = '8ad164c8ada8aaf4034f')
        for image in request.data['imagepath']:
            print(image)
            try:
                with open(image, 'rb') as f:
                    url = Uploadcare.upload(f)
                    urls.append(str(url))
            except Exception as e: 
                return HttpResponse(e)

   
        if(len(urls) == 0):
            return HttpResponse("Upload error: it appears nothing was uploaded")
        for thing in urls:
            print (thing)
        urls_json = json.dumps(urls)
        print (urls_json)

        return JsonResponse(urls_json, safe=False)

# create bidding item
@api_view(['POST'])
def create_bid_item(request, listingid = ""):
    if request.method != "POST":
        return HttpResponse("Unrecognized request. This URL only accepts POST methods.")
    # first check to see if listing exists
    # pull listing ID out of JSON
    # listingid = request.data['_id']
    if listingid == "":
        return HttpResponse("Listing field is empty.")
    

    cursor = db_collection("listings")
    result = cursor.find_one(ObjectId(listingid))

    if result == None:
        return HttpResponse("The listing does not exist.")
    
    jsonitem = {
        'listingid' : listingid,
        'highestbid' : 0,
        'highestbidder' : None,
        'bidders' : []
    }

    bidid = db_collection("bids").insert_one(jsonitem).inserted_id
    return JsonResponse({"id" : str(bidid)})
    
#  get highest bid

def get_highest_bidder(request, bidid = ""):
    if request.method != "GET":
        return HttpResponse("Unrecognized request. This URL only accepts GET methods.")
    if bidid == "":
        return HttpResponse("Bid field is empty.")

    cursor = db_collection("bids")
    try:
        result = cursor.find_one(ObjectId(bidid))
    except Exception as e: 
        return HttpResponse(e)
    if result == None:
        return HttpResponse("The bid does not exist.")
    bid = result["highestbid"]
    bidder = result["highestbidder"]
    if bidder == None or bid == 0:
        return HttpResponse("No bid or bidders yet")
    jsonitem = {
        'highestbid' : bid,
        'highestbidder' : bidder
    }

    return JsonResponse(jsonitem)

        

# update bidder list, update highest bidder automatically and highest bid only if that bidder has the highest bid
@api_view(['PATCH'])
def update_bid_item(request, bidid = ""):
    if request.method != "PATCH":
        return HttpResponse("Unrecognized request. This URL only accepts POST methods.")
    if bidid == "":
        return HttpResponse("Bid field is empty.")
 
    cursor = db_collection("bids")
    result = cursor.find_one(ObjectId(bidid))
    if result == None:
        return HttpResponse("The bid does not exist.")
    
    # assumes user exists, idk how to confirm this using the django thing
    try:
        username = request.data['username']
        userbid = request.data['bid']
        cursor.update({
            "highestbid": {
                "$lt": userbid
            }
        }, {
            "$set": {
                "highestbid": userbid,
                "highestbidder": username
            }
        })
        cursor.update(
            {"_id" : ObjectId(bidid)},
            {"$addToSet" : {"bidders" : username}}
        )
    
    except Exception as e: 
        return HttpResponse(e)
    id = result["_id"]
    return JsonResponse({"_id" : str(id)}, safe=False)
    return HttpResponse("success")
    


# may merge this with update bid item tbh
@api_view(['POST'])
def mybids(request, bidid = ""):
    if request.method != "POST":
        return HttpResponse("Unrecognized request. This URL only accepts POST methods.")
    if bidid == "":
        return HttpResponse("Bid field is empty.")
    cursor = db_collection("bids")
    result = cursor.find_one(ObjectId(bidid))
    if result == None:
        return HttpResponse("The bid does not exist.")
    
    cursor = db_collection("mybids")
    
    # assumes user exists
    try:
        username = request.data['username']
        userbid = request.data['bid']

        find = cursor.find_one({"username" : username})
        print("VALUE OF FIND: " , find)
        # if the username does not exist, create
        if find == None:
            jsonitem = {
                "username" : username,
                "allbids" : [
                    {
                        "bidid" : bidid,
                        "bidvalue" : userbid
                    }
                ]
            }
            mybidid = cursor.insert_one(jsonitem).inserted_id
            return JsonResponse({"_id" : str(mybidid)}, safe=False)
        
        else:
            # if user is found, see if they have a bid on the item already
            find = cursor.find_one({"username" : username, "allbids" : {"$elemMatch" : {"bidid" : bidid}}})
            # if not create the dict
            if find == None:
                cursor.update_many(
                    {"username" : username},
                    {
                        "$push" : {
                            "allbids" : {
                                "bidid" : bidid,
                                "bidvalue" : userbid
                            }
                        }
                    }
                )
                print("THE ID IS: " ,find["_id"])

            # if so update the dict
            else:
                cursor.update_many(
                    {"username" : username, "allbids" : {"$elemMatch" : {"bidid" : bidid}}},
                    {
                        "$set" : {
                            "allbids.$.bidvalue" : userbid
                        }
                    },

                )
                print("THE ID IS: " ,find["_id"])
            
            return JsonResponse({"_id" : str(find["_id"])}, safe=False)
    
    except Exception as e: 
        return HttpResponse(e)    


def delete_bidder(request, bidid = ""):

    if request.method != "PATCH":
        return HttpResponse("Unrecognized request. This URL only accepts PATCH methods.")
    # if not request.user.is_authenticated:
    #     return HttpResponse("Authentication error")
    if(bidid == ""):
        return HttpResponse("Bid field is empty.")

    # username = str(request.user.username)
    username = "Bob"
    cursor = db_collection("bids")
    cursor1 = db_collection("mybids")
    try:
        find  = cursor.find_one(
            
                {"_id" : ObjectId(bidid), "bidders" : username}
            
        )

        print(find)

        find1 = cursor1.find_one(
            
                {"username" : username, "allbids" : {"$elemMatch" : {"bidid" : bidid}}}
        )
        

        print(find1)

        if(find1 == None or find == None):
            return HttpResponse("user does not have a bid on this item")

        # delete user from database list
        cursor.update(
            {"_id" : ObjectId(bidid)},
            {
                "$pull" : {
                    "bidders" : username
                }
            }
        )
        # delete users bid from mybids
        cursor1.update(
            
            {"username" : username},
            {
                "$pull" : {
                    "allbids" : {
                        "bidid" : bidid
                    }
                }
            }
        )
        
        highestbidder = find["highestbidder"]
        if(username == highestbidder):
            print("repace highest bidder")
            find3 = cursor1.find(
                {
                    "allbids" : {"$elemMatch" : {"bidid" : bidid}}
                }
            ).sort("allbids.bidvalue", -1).limit(1)
            user = None
            value = None
            for doc in find3:
                print(doc)
                user = doc["username"]
                value = doc['allbids'][0]['bidvalue']

            # if no user was found to be the next highest bidder
            if user == None:
                cursor.update(
                    {"_id" : ObjectId(bidid)},
                    {
                        "$set" : {
                            "highestbidder" : None,
                            "highestbid" : 0
                        }

                    }
                )
            else:
                cursor.update(
                    {"_id" : ObjectId(bidid)},
                    {
                        "$set" : {
                            "highestbidder" : user,
                            "highestbid" : value
                        }
                    }
                )    
            


        else:
            print("do not replace highest bidder")


    except Exception as e: 
        return HttpResponse(e)  

    
    return JsonResponse({"_id" : bidid}, safe=False)

def get_my_bids(request):
    if request.method != "GET":
        return HttpResponse("Unrecognized request. This URL only accepts PATCH methods.")
    # if not request.user.is_authenticated:
    #     return HttpResponse("Authentication error")

    username = request.user.username
    username = "Bob"
    cursor = db_collection("mybids")

    find = cursor.find_one(
       {"username" : username} 
    )

    print(find)

    arr = []
    for doc in find['allbids']:
        print(doc)
        arr.append(doc)

    jsonitem = json.dumps(arr)
    print (jsonitem)

    return JsonResponse(jsonitem, safe=False)


