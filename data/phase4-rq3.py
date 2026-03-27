"""
RQ3: Among indie and electronic artists, are those who are currently more popular
on Spotify associated with higher total sales on Bandcamp during the 2020 period?

External libraries: pymongo, pandas, matplotlib, scipy, numpy
"""

import pandas as pd
from pymongo import MongoClient
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np

# FOR GRADERS
# To replicate results,
#   1. Run load_mongodb.py with your CWL/SNUM to upload the database
#   2. Set CWL and SNUM below to your own credentials
#   3. Open an SSH tunnel: ssh -l CWL -L localhost:27017:nosql.students.cs.ubc.ca:27017 remote.students.cs.ubc.ca
#   4. Run this script
CWL  = "bhelfert"
SNUM = "87264206"

# Connect to MongoDB
connection_string = f"mongodb://{CWL}:a{SNUM}@localhost:27017/{CWL}"
client = MongoClient(connection_string)

db = client[CWL]
artists_collection = db["artists"]


# For each artist with > 1 sale, count Bandcamp sales ([a]lbums and [t]racks) and get Spotify popularity
pipeline = [
    {"$unwind": "$bandcamp_sales"},
    {"$match": {"bandcamp_sales.item_type": {"$in": ["a", "t"]}}},
    {"$group": {
        "_id": {
            "artist_name": "$artist_name",
            "popularity":  "$spotify.popularity"
        },
        "total_sales": {"$sum": 1}
    }},
    {"$match": {"total_sales": {"$gte": 2}}},
    {"$sort": {"_id.popularity": -1}}
]

results = list(artists_collection.aggregate(pipeline))
client.close()

# Results dataframe
df = pd.DataFrame([{
    "popularity":  r["_id"]["popularity"],
    "total_sales": r["total_sales"]
} for r in results])

df = df.dropna(subset=["popularity", "total_sales"])

# Get correlation between Bandcamp sales and Spotify popularity
corr, p_val = stats.spearmanr(df["popularity"], df["total_sales"])

def make_plot(data, filename, title_suffix=""):
    # Make scatter plot
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(data["popularity"], data["total_sales"], alpha=0.6, color="steelblue",
               edgecolors="white", linewidths=0.4)

    # Add line of best fit
    m, b = np.polyfit(data["popularity"], data["total_sales"], 1)
    x_line = np.linspace(data["popularity"].min(), data["popularity"].max(), 100)
    ax.plot(x_line, m * x_line + b, color="firebrick", linewidth=1.5)

    # Label and save plot
    ax.set_xlabel("Spotify Popularity")
    ax.set_ylabel("Bandcamp Sales Count")
    ax.set_title(
        f"RQ3: Spotify Popularity vs Bandcamp Sales Volume{title_suffix}\n"
        f"Spearman r={corr:.3f}, p={p_val:.3f}  (n={len(data)} artists)"
    )
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()

# Plot with full dataset
make_plot(df, "phase4_rq3_visualization.png")

# Plot with outliers removed
df_filtered = df[df["total_sales"] <= 120]
make_plot(df_filtered, "phase4_rq3_visualization_no_outliers.png", title_suffix=" (outliers removed)")
