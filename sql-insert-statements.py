import pandas as pd

bandcamp_sales = pd.read_csv("data/bandcamp_sales_cleaned.csv")
spotify_artists = pd.read_csv("data/spotify_artists_cleaned.csv")
spotify_tracks = pd.read_csv("data/spotify_tracks_cleaned.csv")

with open('bandcamp_spotify_data.sql', 'w', encoding='utf-8') as f:

    f.write("DROP TABLE Artists PURGE RECYCLEBIN;\n")
    f.write("""
CREATE TABLE Artists (
    artist_name VARCHAR2(255) PRIMARY KEY,
    spotify_id VARCHAR2(255) UNIQUE,
    popularity NUMBER,
    followers NUMBER,
    genre_type VARCHAR2(50),
    total_releases NUMBER,
    first_release DATE,
    latest_release DATE,
    years_active NUMBER,
    releases_per_year NUMBER
);
""")

    for _, row in spotify_artists.iterrows():
        if pd.notnull(row['artist_name']):
            artist_name = row['artist_name'].replace("'", "''")
            spotify_id = row['spotify_id'].replace("'", "''") if pd.notnull(row['spotify_id']) else 'NULL'
            popularity = row['popularity'] if pd.notnull(row['popularity']) else 'NULL'
            followers = row['followers'] if pd.notnull(row['followers']) else 'NULL'
            if pd.notnull(row['genre_type']):
                genre_type = row['genre_type'].replace("'", "''")
                genre_type = f"'{genre_type}'"
            else:
                genre_type = 'NULL'
            total_releases = row['total_releases'] if pd.notnull(row['total_releases']) else 'NULL'
            first_release = f"TO_DATE('{row['first_release']}', 'YYYY-MM-DD')" if pd.notnull(row['first_release']) else 'NULL'
            latest_release = f"TO_DATE('{row['latest_release']}', 'YYYY-MM-DD')" if pd.notnull(row['latest_release']) else 'NULL'
            years_active = row['years_active'] if pd.notnull(row['years_active']) else 'NULL'
            releases_per_year = row['releases_per_year'] if pd.notnull(row['releases_per_year']) else 'NULL'

            f.write(f"INSERT INTO Artists (artist_name, spotify_id, popularity, followers, genre_type, total_releases, first_release, latest_release, years_active, releases_per_year) VALUES ('{artist_name}', '{spotify_id}', {popularity}, {followers}, {genre_type}, {total_releases}, {first_release}, {latest_release}, {years_active}, {releases_per_year});\n")

    f.write("\n")

    f.write("DROP TABLE Tracks PURGE RECYCLEBIN;\n")
    f.write("""
CREATE TABLE Tracks (
    track_id VARCHAR2(255) PRIMARY KEY,
    track_name VARCHAR2(255),
    artist_name VARCHAR2(255),
    popularity NUMBER,
    duration_ms NUMBER,
    explicit NUMBER,
    danceability NUMBER,
    acousticness NUMBER,
    valence NUMBER,
    tempo NUMBER,
    genre_type VARCHAR2(50),
    UNIQUE(track_name, artist_name),
    FOREIGN KEY (artist_name) REFERENCES Artists(artist_name)
);
""")

    for _, row in spotify_tracks.iterrows():
        if pd.notnull(row['track_id']) and pd.notnull(row['artist_name']):
            track_id = row['track_id'].replace("'", "''")
            track_name = row['track_name'].replace("'", "''") if pd.notnull(row['track_name']) else 'NULL'
            artist_name = row['artist_name'].replace("'", "''")
            popularity = row['popularity'] if pd.notnull(row['popularity']) else 'NULL'
            duration_ms = row['duration_ms'] if pd.notnull(row['duration_ms']) else 'NULL'
            explicit = row['explicit'] if pd.notnull(row['explicit']) else 'NULL'
            danceability = row['danceability'] if pd.notnull(row['danceability']) else 'NULL'
            acousticness = row['acousticness'] if pd.notnull(row['acousticness']) else 'NULL'
            valence = row['valence'] if pd.notnull(row['valence']) else 'NULL'
            tempo = row['tempo'] if pd.notnull(row['tempo']) else 'NULL'
            genre_type = row['genre_type'].replace("'", "''") if pd.notnull(row['genre_type']) else 'NULL'

            f.write(f"INSERT INTO Tracks (track_id, track_name, artist_name, popularity, duration_ms, explicit, danceability, acousticness, valence, tempo, genre_type) VALUES ('{track_id}', '{track_name}', '{artist_name}', {popularity}, {duration_ms}, {explicit}, {danceability}, {acousticness}, {valence}, {tempo}, '{genre_type}');\n")

    f.write("\n")

    f.write("DROP TABLE Sales PURGE RECYCLEBIN;\n")
    f.write("""
CREATE TABLE Sales (
    bc_transaction_id VARCHAR2(255) PRIMARY KEY,
    artist_name VARCHAR2(255),
    item_type VARCHAR2(50),
    item_price NUMBER CHECK(item_price >= 0),
    amount_paid NUMBER CHECK(amount_paid >= 0),
    currency VARCHAR2(10),
    amount_paid_usd NUMBER CHECK(amount_paid_usd >= 0),
    FOREIGN KEY (artist_name) REFERENCES Artists(artist_name)
);
""")

    for _, row in bandcamp_sales.iterrows():
        if pd.notnull(row['bc_transaction_id']) and pd.notnull(row['artist_name']):
            bc_transaction_id = row['bc_transaction_id'].replace("'", "''")
            artist_name = row['artist_name'].replace("'", "''")
            item_type = row['item_type'].replace("'", "''") if pd.notnull(row['item_type']) else 'NULL'
            item_price = row['item_price'] if pd.notnull(row['item_price']) and row['item_price'] >=0 else 'NULL'
            amount_paid = row['amount_paid'] if pd.notnull(row['amount_paid']) and row['amount_paid'] >=0 else 'NULL'
            currency = row['currency'].replace("'", "''") if pd.notnull(row['currency']) else 'NULL'
            amount_paid_usd = row['amount_paid_usd'] if pd.notnull(row['amount_paid_usd']) and row['amount_paid_usd'] >=0 else 'NULL'

            f.write(f"INSERT INTO Sales (bc_transaction_id, artist_name, item_type, item_price, amount_paid, currency, amount_paid_usd) VALUES ('{bc_transaction_id}', '{artist_name}', '{item_type}', {item_price}, {amount_paid}, '{currency}', {amount_paid_usd});\n")

    f.write("\nCOMMIT;\n")

print("SQL file 'bandcamp_spotify_data.sql' created successfully!")
