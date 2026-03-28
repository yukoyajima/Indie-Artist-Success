"""
RQ2: Question 2: Within indie and electronic genres, do track-level audio features (such as danceability, 
energy, and tempo) predict track popularity on Spotify?

External libraries: pymongo, pandas, matplotlib, sklearn, numpy
"""

import pandas as pd
from pymongo import MongoClient
import matplotlib.pyplot as plt
from sklearn.linear_model import Lasso 
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.compose import  make_column_transformer
from sklearn.model_selection import train_test_split

# RQ2: Within indie and electronic genres, do track-level audio features (such as danceability, 
# energy, and tempo) predict track popularity on Spotify?


# FOR GRADERS
# To replicate results,
#   1. Run load_mongodb.py with your CWL/SNUM to upload the database
#   2. Set CWL and SNUM below to your own credentials
#   3. Open an SSH tunnel: ssh -l CWL -L localhost:27017:nosql.students.cs.ubc.ca:27017 remote.students.cs.ubc.ca
#   4. Run this script

CWL = "abes1602"
SNUM = "42466268"

connection_string = f"mongodb://{CWL}:a{SNUM}@localhost:27017/{CWL}"
client = MongoClient(connection_string)

db = client[CWL]
artists_collection = db["artists"]

# Query to MongoDB
query = [
    {"$unwind": "$tracks"},
    {
        "$match": {
            "tracks.popularity": {"$ne": None},
            "tracks.duration_ms": {"$ne": None},
            "tracks.explicit": {"$ne": None},
            "tracks.danceability": {"$ne": None},
            "tracks.acousticness": {"$ne": None},
            "tracks.valence": {"$ne": None},
            "tracks.tempo": {"$ne": None}
        }
    },
    {
        "$project": {
            "_id": 0,
            "popularity": "$tracks.popularity",
            "duration_ms": "$tracks.duration_ms",
            "explicit": "$tracks.explicit",
            "danceability": "$tracks.danceability",
            "acousticness": "$tracks.acousticness",
            "valence": "$tracks.valence",
            "tempo": "$tracks.tempo"
        }
    }
]
results = list(db["artists"].aggregate(query))
df = pd.DataFrame(results)

#datasplit
X = df.drop(columns= "popularity")
y = df["popularity"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size= 0.2, random_state= 123)

# Feature Scaling 
numeric_cols = ['duration_ms', 'danceability', 'acousticness', 'valence',
       'tempo']
scaler = StandardScaler()
preprocessor = make_column_transformer(
    (
        scaler, numeric_cols,
    ),
    (
        "passthrough", ["explicit"] #binary
    ),
)
# Model Pipeline
pipe = make_pipeline(preprocessor, Lasso())

pipe.fit(X_train, y_train)

predicted_y = pipe.predict(X_test) #predicted values
actual_y = y_test
residuals = actual_y - predicted_y #residuals for plotting

# Residual Plot
plt.scatter(actual_y, residuals)
plt.title("Track Popularity: Actual vs Residual")
plt.xlabel("Actual Track Popularity")
plt.ylabel("Residual (actual - predicted)");
# Saving Plot
plt.savefig("phase4-q2-residuals.png", dpi=300, bbox_inches="tight")
plt.show()


# Tabulating Model Coefficients
coef_df = pd.DataFrame({
    "feature": X.columns,
    "coefficient": pipe.named_steps['lasso'].coef_
})

coef_df.to_csv("phase4-q2-coefficients.csv", index=False)

# Tabulating intercept and R-Squared values

intercept = pipe.named_steps['lasso'].intercept_
r2 = pipe.score(X_test, y_test)

int_r2_df_PHASE_4 = pd.DataFrame({
    'Metric': ['Intercept', 'R-Squared'],
    'Values': [intercept, r2]
})
int_r2_df_PHASE_4.to_csv("phase4-q2-r2int.csv", index = False)

