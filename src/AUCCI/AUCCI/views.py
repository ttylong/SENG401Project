# REST API endpoints for listings

from email.mime import image
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
<<<<<<< HEAD
        json_data.append({"_id" : str(datum['_id']), "username" : str(datum['username']), "item" : datum['item']})

=======
        json_data.append({"_id" : str(datum['_id']), "username" : datum['username'], "item" : datum['item'], "brand" : datum['brand'], "category" : datum['category'], "gender" : datum['gender'], "size" : datum['size'], "listtime" : str(datum['listtime']), "initprice" : str(datum['initprice']), "timelimit" : str(datum['timelimit']), "image" : datum['image']})
>>>>>>> 8c72a4d16dc5566a8a6d33d8485b2257a3d967fd
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
                return HttpResponse("you messed up: " ,e)

   
        if(len(urls) == 0):
            return HttpResponse("Upload error: it appears nothing was uploaded")
        for thing in urls:
            print (thing)
        urls_json = json.dumps(urls)
        print (urls_json)

        return JsonResponse(urls_json, safe=False)

# create bidding item
@api_view(['POST'])
def create_bid_item(request):
    if request.method != "POST":
        return HttpResponse("Unrecognized request. This URL only accepts POST methods.")
    # first check to see if listing exists
    # pull listing ID out of JSON
    listingid = request.data['_id']
    

    cursor = db_collection("listings")
    result = cursor.find_one(ObjectId(listingid))

    if result == None:
        return HttpResponse("The listing does not exist.")
    
    jsonitem = {
        'listingid' : listingid,
        'highestbid' : 0,
        'highestbidder' : None,
        'bidders' : {

        }
    }

    bidid = db_collection("bids").insert_one(jsonitem).inserted_id
    return JsonResponse({"id" : str(bidid)})
    
#  get highest bid


# update bidder list, update highest bidder and highest bid only if that bidder has the highest bid
# not complete
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
    # username = request.data['username']
    # userbid = request.data['bid']
    return HttpResponse("something happened.")
    


# delete user from list of bidders
# search for user in mybids. if they have the highest bid, then update the highest bidder to the next highest
@api_view(['PATCH'])
def delete_bidder(request, userid = ""):
    if request.method != "PATCH":
        return HttpResponse("Unrecognized request. This URL only accepts PATCH methods.")
    if userid == "":
        return HttpResponse("User field empty.")







