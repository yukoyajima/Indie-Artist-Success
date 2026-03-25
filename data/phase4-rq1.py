import pandas as pd
from pymongo import MongoClient

CWL = "isaac184"
SNUM = "97241418"

connection_string = f"mongodb://{CWL}:a{SNUM}@localhost:27017/{CWL}"
client = MongoClient(connection_string)

db = client[CWL]
artists_collection = db["artists"]

# query here
#results = list(...)

#df = pd.DataFrame(results)

result = artists_collection.find_one({}, {"_id": 0, "artist_name": 1, "spotify.popularity": 1})
print(result)

print("Total artist documents:", artists_collection.count_documents({}))
