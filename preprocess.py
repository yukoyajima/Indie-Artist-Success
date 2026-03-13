# This file filters the data to satisfy our schema constraints and creates the SQL file for uploading to Oracle
# 
# External libraries used: regex, pandas

import re
import pandas as pd

# Load cleaned datasets
artists = pd.read_csv("data/spotify_artists_cleaned.csv")
tracks  = pd.read_csv("data/spotify_tracks_cleaned.csv")
bc      = pd.read_csv("data/bandcamp_sales_cleaned.csv")

# Deduplicate artists
artists = artists.drop_duplicates(subset=["artist_name"])

# String normalizing function to help with matching artist names that appear differently on Bandcamp/Spotify 
def normalize(s):
    s = str(s).lower().strip()
    s = s.replace("&", "and")
    s = re.sub(r"[^\w\s]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

# Normalize artist names
artist_norm = {normalize(n): n for n in artists["artist_name"]}

# Filter tracks to only those with an artist_name in Artists
tracks_norm = tracks["artist_name"].apply(normalize)
tracks = tracks[tracks_norm.isin(artist_norm)].copy()

# Set Tracks artist name to "correct" name (the one on spotify)
tracks["artist_name"] = tracks["artist_name"].apply(lambda n: artist_norm[normalize(n)])

# Deduplicate tracks
tracks = tracks.drop_duplicates(subset=["track_id"])
tracks = tracks.drop_duplicates(subset=["track_name", "artist_name"])

# Normalize artist names for matching with Artists table
bc_norm = bc["artist_name"].apply(normalize)
bc = bc[bc_norm.isin(artist_norm)].copy()

# Set BC artist name to "correct" name (the one on spotify)
bc["artist_name"] = bc["artist_name"].apply(
    lambda n: artist_norm[normalize(n)]
)

# Sample to fit Oracle space quota
bc = bc.sample(n=min(2000, len(bc)), random_state=123)

# Make all strings work in oracle
def into_oracle_string(val):
    s = str(val)
    s = s.replace("'", "''")
    s = s.replace("&", " and ")
    s = s.replace("//", "/ /")
    return s

# Return the correct value for oracle (for nulls, strings, and booleans)
def into_oracle_value(val, is_str=False):
    if pd.isnull(val):
        return "NULL"
    if is_str:
        return f"'{into_oracle_string(val)}'"
    if isinstance(val, bool):
        return "1" if val else "0"
    return str(val)

# WRITE SQL FILE
with open("bandcamp_spotify_data.sql", "w", encoding="utf-8") as f:

    f.write("SET DEFINE OFF;\n\n")

    # This just makes the script run correctly if you run it multiple times
    f.write("DROP TABLE Sales   CASCADE CONSTRAINTS;\n")
    f.write("DROP TABLE Tracks  CASCADE CONSTRAINTS;\n")
    f.write("DROP TABLE Artists CASCADE CONSTRAINTS;\n\n")

    # Create Artists table
    f.write("""\
CREATE TABLE Artists (
    artist_name       VARCHAR2(255) PRIMARY KEY,
    spotify_id        VARCHAR2(255) UNIQUE,
    popularity        NUMBER,
    followers         NUMBER,
    genre_type        VARCHAR2(255),
    total_releases    NUMBER,
    first_release     DATE,
    latest_release    DATE,
    years_active      NUMBER,
    releases_per_year NUMBER
);\n""")

    for _, row in artists.iterrows():
        name = into_oracle_value(row["artist_name"], is_str=True)
        sid  = into_oracle_value(row.get("spotify_id"), is_str=True)
        pop  = into_oracle_value(row["popularity"])
        fol  = into_oracle_value(row["followers"])
        gen  = into_oracle_value(row.get("genre_type"), is_str=True)
        tot  = into_oracle_value(row["total_releases"])
        fr   = (f"TO_DATE('{row['first_release']}', 'YYYY-MM-DD')"
                if pd.notnull(row.get("first_release")) else "NULL")
        lr   = (f"TO_DATE('{row['latest_release']}', 'YYYY-MM-DD')"
                if pd.notnull(row.get("latest_release")) else "NULL")
        ya   = into_oracle_value(row["years_active"])
        rpy  = into_oracle_value(row["releases_per_year"])
        f.write(
            f"INSERT INTO Artists VALUES "
            f"({name}, {sid}, {pop}, {fol}, {gen}, {tot}, {fr}, {lr}, {ya}, {rpy});\n"
        )

    f.write("\n")

    # Create Tracks table
    f.write("""\
CREATE TABLE Tracks (
    track_id     VARCHAR2(255) PRIMARY KEY,
    track_name   VARCHAR2(255),
    artist_name  VARCHAR2(255),
    popularity   NUMBER,
    duration_ms  NUMBER,
    explicit     NUMBER,
    danceability NUMBER,
    acousticness NUMBER,
    valence      NUMBER,
    tempo        NUMBER,
    genre_type   VARCHAR2(100),
    UNIQUE (track_name, artist_name),
    FOREIGN KEY (artist_name) REFERENCES Artists(artist_name)
);\n""")

    for _, row in tracks.iterrows():
        tid  = into_oracle_value(row["track_id"], is_str=True)
        tnam = into_oracle_value(row.get("track_name"), is_str=True)
        anam = into_oracle_value(row["artist_name"], is_str=True)
        pop  = into_oracle_value(row["popularity"])
        dur  = into_oracle_value(row["duration_ms"])
        exp  = "1" if row["explicit"] else "0"
        dan  = into_oracle_value(row["danceability"])
        aco  = into_oracle_value(row["acousticness"])
        val  = into_oracle_value(row["valence"])
        tem  = into_oracle_value(row["tempo"])
        gen  = into_oracle_value(row.get("genre_type"), is_str=True)
        f.write(
            f"INSERT INTO Tracks VALUES "
            f"({tid}, {tnam}, {anam}, {pop}, {dur}, {exp}, {dan}, {aco}, {val}, {tem}, {gen});\n"
        )

    f.write("\n")

    # Create Sales table
    f.write("""\
CREATE TABLE Sales (
    bc_transaction_id VARCHAR2(255) PRIMARY KEY,
    artist_name       VARCHAR2(255),
    item_type         VARCHAR2(50),
    item_price        NUMBER CHECK (item_price >= 0),
    amount_paid       NUMBER CHECK (amount_paid >= 0),
    currency          VARCHAR2(10),
    amount_paid_usd   NUMBER CHECK (amount_paid_usd >= 0),
    FOREIGN KEY (artist_name) REFERENCES Artists(artist_name)
);\n""")

    for _, row in bc.iterrows():
        tid  = into_oracle_value(row["bc_transaction_id"], is_str=True)
        anam = into_oracle_value(row["artist_name"], is_str=True)
        ityp = into_oracle_value(row.get("item_type"), is_str=True)
        iprc = into_oracle_value(row.get("item_price"))
        apd  = into_oracle_value(row.get("amount_paid"))
        cur  = into_oracle_value(row.get("currency"), is_str=True)
        usd  = into_oracle_value(row.get("amount_paid_usd"))
        f.write(
            f"INSERT INTO Sales VALUES "
            f"({tid}, {anam}, {ityp}, {iprc}, {apd}, {cur}, {usd});\n"
        )

    f.write("\nCOMMIT;\n")
