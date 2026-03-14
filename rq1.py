"""
RQ1: What factors affect the success of indie and electronic musicians across different streaming platforms?
"""

import oracledb
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np

# FOR GRADERS
# To replicate results, 
#   1. Upload bandcamp_spotify_data.sql to Oracle server
#   2. Set USER and PASSWORD below to your own credentials
#   3. Open an SSH tunnel: ssh -L 1522:localhost:1521 {TARGET SERVER} -N
#   4. Run this script
USER     = "isaac184"
PASSWORD = "a97241418"

# Connect to Oracle server
dsn = oracledb.makedsn("localhost", 1522, service_name="stu")
connection = oracledb.connect(user=USER, password=PASSWORD, dsn=dsn)

# SQL Query:
# Joins Artists and Sales on artist_name
# Aggregates per-artist sales metrics for artists with at least 2 transactions

# The reason for all three metrics is that I had originally looked at more relationships between
# artist popularity and sales metrics, but the only one with a significant correlation was average item price.
# Analysis on that correlation is shown below.

RQ3_QUERY = """
SELECT
    artist_name,
    popularity,
    followers,
    total_releases,
    years_active,
    releases_per_year
FROM Artistss
WHERE popularity IS NOT NULL
  AND followers IS NOT NULL
  AND total_releases IS NOT NULL
  AND years_active IS NOT NULL
  AND releases_per_year IS NOT NULL;
"""

df = pd.read_sql(RQ3_QUERY, connection)
connection.close()

artists = df
artists.head()

# Linear regression - base model
y = artists['POPULARITY'].to_numpy()
N = len(y)

x1 = artists['FOLLOWERS'].to_numpy()
x2 = artists['TOTAL_RELEASES'].to_numpy()
x3 = artists['YEARS_ACTIVE'].to_numpy()
x4 = artists['RELEASES_PER_YEAR'].to_numpy()

X = np.column_stack([np.ones(N), x1, x2, x3, x4])

beta = np.linalg.solve(X.T @ X, X.T @ y)
y_pred = X @ beta
residuals = y - y_pred

R2 = 1 - np.sum(residuals**2) / np.sum((y - np.mean(y))**2)
R2adj = 1 - (1 - R2) * (N - 1) / (N - 5)

# linear regression - log model
x1_log = np.log1p(artists['FOLLOWERS'].to_numpy())
x2_log = np.log1p(artists['TOTAL_RELEASES'].to_numpy())
x3_log = np.log1p(artists['YEARS_ACTIVE'].to_numpy())
x4_log = np.log1p(artists['RELEASES_PER_YEAR'].to_numpy())

X_log = np.column_stack([np.ones(N), x1_log, x2_log, x3_log, x4_log])

beta_log = np.linalg.solve(X_log.T @ X_log, X_log.T @ y)
y_pred_log = X_log @ beta_log
residuals_log = y - y_pred_log

R2_log = 1 - np.sum(residuals_log**2) / np.sum((y - np.mean(y))**2)
R2adj_log = 1 - (1 - R2_log) * (N - 1) / (N - 5)

# actual vs predicted

plt.figure(figsize=(6, 6))
plt.scatter(y, y_pred_log, alpha=0.5)
plt.xlabel('Actual Popularity')
plt.ylabel('Predicted Popularity')
plt.title('Actual vs Predicted Popularity (Log Transformed)')
plt.grid(True)

min_val = min(np.min(y), np.min(y_pred_log))
max_val = max(np.max(y), np.max(y_pred_log))
plt.plot([min_val, max_val], [min_val, max_val], color='black')

plt.tight_layout()
plt.savefig("actual_vs_predicted_popularity.png", dpi=150, bbox_inches="tight")
plt.show()

# resid hist

plt.figure(figsize=(7, 4))
plt.hist(residuals_log, bins=30)
plt.xlabel('Residual')
plt.ylabel('Frequency')
plt.title('Residual Distribution (Log Transformed)')
plt.grid(True)

plt.tight_layout()
plt.savefig("residual_distribution_log_transformed.png", dpi=150, bbox_inches="tight")
plt.show()

# final models

model_summary = pd.DataFrame({
    'Model': ['Linear', 'Log-transformed'],
    'R2': [R2, R2_log],
    'Adjusted R2': [R2adj, R2adj_log]
})

coef_table = pd.DataFrame({
    'Variable': ['Intercept', 'FOLLOWERS', 'TOTAL_RELEASES', 'YEARS_ACTIVE', 'RELEASES_PER_YEAR'],
    'Linear model': beta,
    'Log model': beta_log
})

print(model_summary)
print()
print(coef_table)