import pandas as pd
from pymongo import MongoClient
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import seaborn as sns
import matplotlib.pyplot as plt

# RQ1: Which artist-level attributes (such as catalog size, release frequency, and follower count) 
# are most predictive of popularity for indie and electronic artists on Spotify?  

# FOR GRADERS
# To replicate results,
#   1. Run load_mongodb.py with your CWL/SNUM to upload the database
#   2. Set CWL and SNUM below to your own credentials
#   3. Open an SSH tunnel: ssh -l CWL -L localhost:27017:nosql.students.cs.ubc.ca:27017 remote.students.cs.ubc.ca
#   4. Run this script

CWL = "yyajima"
SNUM = "24715716"

connection_string = f"mongodb://{CWL}:a{SNUM}@localhost:27017/{CWL}"
client = MongoClient(connection_string)

db = client[CWL]
artists_collection = db["artists"]

# query
data = list(artists_collection.find(
    {"spotify.genre_type": {"$in": ["indie", "electronic"]}},
    {
        "spotify.popularity": 1,
        "spotify.followers": 1,
        "spotify.total_releases": 1,
        "spotify.releases_per_year": 1,
        "spotify.years_active": 1
    }
))

df = pd.DataFrame([{
    "popularity": d["spotify"]["popularity"],
    "followers": d["spotify"]["followers"],
    "total_releases": d["spotify"]["total_releases"],
    "releases_per_year": d["spotify"]["releases_per_year"],
    "years_active": d["spotify"]["years_active"]
} for d in data])

# get coefficients from linear regression

X = df[["followers", "total_releases", "releases_per_year", "years_active"]]
y = df["popularity"]

# scale coefficeints because followers is very small coefficient
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df[["followers", "total_releases", "releases_per_year", "years_active"]])
y = df["popularity"]

# fit model
model = LinearRegression()
model.fit(X_scaled, y)

coefs = pd.DataFrame({
    "attribute": X.columns,
    "coefficient": model.coef_
})

print(coefs)

plt.figure(figsize=(7,4))
sns.barplot(x="attribute", y="coefficient", data=coefs, palette="viridis")
plt.title("predictive strength of artist attribute on popularity")
plt.ylabel("reg coef")
plt.xlabel("artist attribute")
plt.savefig("yuko_phase4_vis.png")
