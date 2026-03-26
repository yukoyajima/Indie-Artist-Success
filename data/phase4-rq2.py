import pandas as pd
from pymongo import MongoClient

CWL = "abes1602"
SNUM = "42466268"

connection_string = f"mongodb://{CWL}:a{SNUM}@localhost:27017/{CWL}"
client = MongoClient(connection_string)

db = client[CWL]
artists_collection = db["artists"]

# query here
results = db["artists"].find_one(
    {"tracks.0": {"$exists": True}},
    {
        "artist_name": 1,
        "spotify": 1,
        "tracks": {"$slice": 2},
        "bandcamp_sales": {"$slice": 2}
    }
)

print(results)
# df = pd.DataFrame(results)
