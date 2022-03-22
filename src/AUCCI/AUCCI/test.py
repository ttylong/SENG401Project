import json

jsonitem = {'_id': '62391ac90246892d5f63ee43', 'username': 'Jack', 'allbids': [{'bidid': '6237fb9e84ed1ef5bee467bc', 'bidvalue': 2000}]}
print(jsonitem['allbids'][0]['bidvalue'])