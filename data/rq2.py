"""
RQ2: Question 2: Within indie and electronic genres, do track-level audio features (such as danceability, 
energy, and tempo) predict track popularity on Spotify?

External libraries: oracledb, pandas, matplotlib, scipy, numpy
"""

import pandas as pd 
import oracledb
import matplotlib.pyplot as plt
import numpy as np
#External Libraries for Regression Model
from sklearn.model_selection import cross_val_score, cross_validate, train_test_split, RandomizedSearchCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from scipy.stats import loguniform
from sklearn.compose import  make_column_transformer
from sklearn.metrics import r2_score


# FOR GRADERS
# To replicate results, 
#   1. Upload bandcamp_spotify_data.sql to Oracle server
#   2. Set USER and PASSWORD below to your own credentials
#   3. Open an SSH tunnel: ssh -L 1522:localhost:1521 {TARGET SERVER} -N
#   4. Run this script
USER     = "ora_abes1602@stu"
PASSWORD = "a42466268"


# db query 
dsn = oracledb.makedsn("localhost", 1522, service_name="stu")
connection = oracledb.connect(user="ora_abes1602", password="a42466268", dsn=dsn)
cur = connection.cursor()

query = """
SELECT popularity, duration_ms, explicit, danceability, acousticness, valence, tempo
FROM Tracks
WHERE popularity IS NOT NULL 
    AND duration_ms IS NOT NULL
    AND explicit  IS NOT NULL
    AND danceability IS NOT NULL
    AND acousticness IS NOT NULL
    AND valence IS NOT NULL 
    AND tempo IS NOT NULL
"""
df = pd.read_sql(query, con=connection)
print(df.head())
connection.close()

# Datasplit 
X = df.drop(columns=["POPULARITY"])
y= df["POPULARITY"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size= 0.3, random_state= 123
)

#Scaling numeric columns 
numeric_cols = ['DURATION_MS', 'DANCEABILITY', 'ACOUSTICNESS', 'VALENCE',
       'TEMPO']
scaler = StandardScaler()
preprocessor = make_column_transformer(
    (
        scaler, numeric_cols,
    ),
    (
        "passthrough", ["EXPLICIT"] #binary
    ),
)

# tuning alpha
# feaature transformation pipeline
pipe_ridge= make_pipeline(preprocessor, Ridge())

param_dist = {
    "ridge__alpha": loguniform(1e-4, 1e3)
}

random_search = RandomizedSearchCV(pipe_ridge,
                                   param_distributions= param_dist,
                                   n_iter= 1000,
                                   n_jobs= -1,
                                   return_train_score = True)

random_search.fit(X_train, y_train)
pd.DataFrame(random_search.cv_results_)[
    [
        "mean_test_score",
        "param_ridge__alpha",
        "rank_test_score",
    ]
].set_index("rank_test_score").sort_index().T

# Best Alpha: 188.75535

# Making Predictions with best alpha 
test_pipe = make_pipeline(preprocessor, Ridge(alpha=188.75535))
test_pipe.fit(X_train, y_train)
predictions = test_pipe.predict(X_test)
actual = y_test

#Plotting Results
plt.scatter(actual, predictions, alpha=0.3)
grid = np.linspace(actual.min(), actual.max(), 1000)
plt.plot(grid, grid, "--k")
plt.grid(True)
plt.title("Track Popularity: Actual vs Predicted")
plt.xlabel("Actual Track Popularity")
plt.ylabel("Predicted Track Popularity");
plt.savefig("q2-scatter.png", dpi=300, bbox_inches="tight")
plt.show()

# Coefficients and Intercept Values
ridge_model = test_pipe.named_steps["ridge"]
r2 = r2_score(y_test, predictions)
print(r2)
print(ridge_model.coef_)
print(ridge_model.intercept_)
coefs_df = pd.DataFrame({'DURATION_MS': [-0.55267527],
                        'DANCEABILITY': [0.23134919],
                        'ACOUSTICNESS': [0.69454486],
                        'VALENCE': [-1.88549835],
                        'TEMPO' : [0.02637506],
                        'EXPLICIT': [1.9753053],
})
coefs_df.to_csv("coefficients.csv", index=False)

int_r2_df = pd.DataFrame({'Intercept': [44.793]},
                         {'R-Squared': [0.0131]})

int_r2_df.to_csv("r2_int.csv", index = False)