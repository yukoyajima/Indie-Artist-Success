import pandas as pd
from pymongo import MongoClient

CWL = "PUT_YOUR_CWL_HERE"
SNUM = "PUT_YOUR_STUDENT_NUMBER_HERE"

connection_string = f"mongodb://{CWL}:a{SNUM}@localhost:27017/{CWL}"
client = MongoClient(connection_string)

db = client[CWL]
artists_collection = db["artists"]

# query here
results = list(...)

df = pd.DataFrame(results)