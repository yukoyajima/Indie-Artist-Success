"""
RQ3: Among indie and electronic artists, are those who are currently more popular
on Spotify associated with higher average Bandcamp item prices during the 2020 period?

External libraries: oracledb, pandas, matplotlib, scipy
"""

import oracledb
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

# FOR GRADERS
# To replicate results, 
#   1. Upload bandcamp_spotify_data.sql to Oracle server
#   2. Set USER and PASSWORD below to your own credentials
#   3. Open an SSH tunnel: ssh -L 1522:localhost:1521 {TARGET SERVER} -N
#   4. Run this script
USER     = "ora_bhelfert"
PASSWORD = "a87264206"

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
    a.artist_name,
    a.popularity,
    COUNT(s.bc_transaction_id)        AS total_sales,
    AVG(s.item_price)                 AS avg_item_price,
    AVG(s.amount_paid - s.item_price) AS avg_overpayment
FROM Artists a
JOIN Sales s ON a.artist_name = s.artist_name
WHERE s.item_type IN ('a', 't')
GROUP BY a.artist_name, a.popularity
HAVING COUNT(s.bc_transaction_id) >= 2
ORDER BY a.popularity DESC
"""

df = pd.read_sql(RQ3_QUERY, connection)
connection.close()

# Spearman correlation between spotify popularity and avg item price
corr, p_val = stats.spearmanr(df["POPULARITY"], df["AVG_ITEM_PRICE"])

# Make and save plot
fig, ax = plt.subplots(figsize=(7, 5))
ax.scatter(df["POPULARITY"], df["AVG_ITEM_PRICE"], alpha=0.6, color="darkorange",
           edgecolors="white", linewidths=0.4)
ax.set_xlabel("Spotify Popularity")
ax.set_ylabel("Avg Item Price (original currency)")
ax.set_title(
    f"RQ3: Spotify Popularity vs Avg Bandcamp Item Price\n"
    f"Spearman r={corr:.3f}, p={p_val:.3f}  (n={len(df)} artists)"
)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("rq3_visualization.png", dpi=150, bbox_inches="tight")
plt.show()
