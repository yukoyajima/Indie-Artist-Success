# This file filters the data to match our MongoDB document structure and loads it into MongoDB.

# MIGHT NEED TO RUN: python3 -m pip install pymongo
# IN YOUR TERMINAL
import re
import pandas as pd
from pymongo import MongoClient


# SETUP INSTRUCTIONS
# 1. Tunnel: ssh -l CWL -L localhost:27017:nosql.students.cs.ubc.ca:27017 remote.students.cs.ubc.ca
# 2. Type in your CWL and SNUM below 
#    (remember to revert it before committing any changes so others can use their own accounts)
# 3. Run this script
# 4. Go to phase4-rq*.py to run query *


# CWL = "PUT_YOUR_CWL_HERE"
# SNUM = "PUT_YOUR_STUDENT_NUMBER_HERE"
CWL = "CWL"
SNUM = "SNUM"

artists = pd.read_csv("data/spotify_artists_cleaned.csv")
tracks  = pd.read_csv("data/spotify_tracks_cleaned.csv")
bc      = pd.read_csv("data/bandcamp_sales_cleaned.csv")


# PREPROCESSING
# Deduplicate artists and remove names with non-ASCII chars
artists = artists.drop_duplicates(subset=["artist_name"])
artists = artists[artists["artist_name"].apply(lambda x: str(x).isascii())]

# String normalizing function to help with matching artist names
# that appear differently on Bandcamp/Spotify
def normalize_artist_name(s):
    s = str(s).lower().strip()
    s = re.sub(r"[^\w\s]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def split_and_normalize_artists(s):
    s = str(s).lower().strip()
    parts = re.split(r"[&,;]", s)

    cleaned = []
    for part in parts:
        part = part.strip()
        part = re.sub(r"[^\w\s]", "", part)
        part = re.sub(r"\s+", " ", part).strip()
        if part:
            cleaned.append(part)

    return cleaned


# map normalized Spotify artist names to originally occurring Spotify artist names
artist_norm = {
    normalize_artist_name(n): n
    for n in artists["artist_name"]
}

## after normalizing artists and creating lists with multi-artists for multi-artist artist names in artist_list
## exploding artist_list and mapping each value to artist_norm for single artist values in artist_name

# ---------- TRACKS ----------
tracks = tracks.copy()
tracks["artist_list"] = tracks["artist_name"].apply(split_and_normalize_artists)
tracks = tracks.explode("artist_list")
tracks = tracks[tracks["artist_list"].isin(artist_norm)].copy()
tracks["artist_name"] = tracks["artist_list"].map(artist_norm)

tracks = tracks[tracks["track_name"].apply(lambda x: str(x).isascii())]
tracks = tracks.drop_duplicates(subset=["track_id", "artist_name"])
tracks = tracks.drop_duplicates(subset=["track_name", "artist_name"])


# ---------- BANDCAMP ----------
bc = bc.copy()
bc["artist_list"] = bc["artist_name"].apply(split_and_normalize_artists)
bc = bc.explode("artist_list")
bc = bc[bc["artist_list"].isin(artist_norm)].copy()
bc["artist_name"] = bc["artist_list"].map(artist_norm)

# Sample to match the Oracle-side preprocessing
bc = bc.sample(n=min(2000, len(bc)), random_state=123)

# Make NaN values work for mongodb
def clean(value):
    if pd.isnull(value):
        return None
    return value


# Artist documents
artist_docs = {}
for _, row in artists.iterrows():
    artist_name = row["artist_name"]
    artist_docs[artist_name] = {
        "artist_name": artist_name,
        "spotify": {
            "spotify_id": clean(row.get("spotify_id")),
            "popularity": clean(row["popularity"]),
            "followers": clean(row["followers"]),
            "genre_type": clean(row.get("genre_type")),
            "total_releases": clean(row["total_releases"]),
            "first_release": clean(row["first_release"]),
            "latest_release": clean(row["latest_release"]),
            "years_active": clean(row["years_active"]),
            "releases_per_year": clean(row["releases_per_year"])
        },
        "tracks": [],
        "bandcamp_sales": [],
    }


# Embed tracks
for _, row in tracks.iterrows():
    artist_name = row["artist_name"]
    if artist_name not in artist_docs:
        continue
    track_doc = {
        "track_id": clean(row["track_id"]),
        "track_name": clean(row["track_name"]),
        "popularity": clean(row["popularity"]),
        "duration_ms": clean(row["duration_ms"]),
        "explicit": clean(row["explicit"]),
        "danceability": clean(row["danceability"]),
        "acousticness": clean(row["acousticness"]),
        "valence": clean(row["valence"]),
        "tempo": clean(row["tempo"]),
        "genre_type": clean(row.get("genre_type"))
    }
    artist_docs[artist_name]["tracks"].append(track_doc)


# Embed Bandcamp sales
for _, row in bc.iterrows():
    artist_name = row["artist_name"]
    if artist_name not in artist_docs:
        continue
    sale_doc = {
        "bc_transaction_id": clean(row["bc_transaction_id"]),
        "item_type": clean(row["item_type"]),
        "item_price": clean(row["item_price"]),
        "amount_paid": clean(row["amount_paid"]),
        "currency": clean(row["currency"]),
        "amount_paid_usd": clean(row["amount_paid_usd"])
    }
    artist_docs[artist_name]["bandcamp_sales"].append(sale_doc)


# Connect to mongodb
connection_string = f"mongodb://{CWL}:a{SNUM}@localhost:27017/{CWL}"
client = MongoClient(connection_string)
db = client[CWL]

artists_collection = db["artists"]


# Load documents into mongodb
artists_collection.drop()

documents = list(artist_docs.values())

if len(documents) > 0:
    artists_collection.insert_many(documents)

print("MongoDB load complete.")
print("Inserted artist documents:", artists_collection.count_documents({}))