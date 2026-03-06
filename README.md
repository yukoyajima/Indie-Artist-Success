#  *What factors affect the success of indie and electronic musicians across different streaming platforms?* # 

**Authors:**\
Malcolm Isaac\
Britton Helfert\
Alexander Beschea\
Yuko Yajima 

## Research Questions ##

**Main Question:** What factors affect the success of indie and electronic musicians across different streaming platforms?

### Question 1: ### 
Which artist-level attributes (such as catalog size, release frequency, and follower count) are most predictive of popularity for indie and electronic artists on Spotify? (Lasso regression? Linear regression?)

**Hypotheses:** We predict that when controlling for follower count, larger catalogs and more frequent releases will correlate with higher popularity but with diminishing returns. This is because the algorithmic exposure mechanisms that Spotify employs favor artists with a steady output of content, but output alone does not guarantee success.

**Methodology:** To test our hypothesis, we will first filter the spotify playlist for songs only performed by artists who pertain to the genre of “indie” or “alternative rock”. Then we will use a linear regression model, extracting the artist level attributes as our features, and use popularity as our target class. The most important aspects of our methodology will be (1) controlling for follower count, and (2) testing our prediction for diminishing returns. For (1), we will include follower count as a covariate in the regression model, thus isolating its effect on the target from the features we are focusing on. For (2), we can fit two different models, the first with a log transformation on our artist-level attributes, and the second without, and investigate which model predicts the popularity more accurately. If there are diminishing returns in artist attributes with regards to the popularity, our model fitted with 
log-transformed data would yield a more accurate popularity prediction, supporting our hypothesis.

### Question 2: ### 
Within indie and electronic genres, do track-level audio features (such as danceability, energy, and tempo) predict track popularity on Spotify?

**Hypotheses:** We predict that danceability and energy will have a positive correlation with popularity, while other predictors may have little to no significant effect. We anticipate small effect sizes overall because within a single genre, audio features are relatively homogeneous and thus external features are likely more predictive of success.

**Methodology:** Similarly to our RQ1, we will begin by filtering out tuples pertaining to artists in the indie and electronic genres. Then to test this hypothesis, we will extract the track-level audio features as attributes in our relations, and fit a linear regression model using song popularity as our target class. When investigating the coefficients of our linear model, we predict coefficients for “danceability” and “energy” will be highest in comparison to our other features, hence supporting our hypothesis.

### Question 3: ### 
Among indie and electronic artists, are those who are currently more popular on Spotify associated with higher Bandcamp sales activity (such as total sales, average price of releases, and tips from fans) during the observed 2020 period?

**Hypotheses:** We predict that artists with greater success on Spotify will have higher Bandcamp sales overall but lower average voluntary overpayment from fans. We expect this because smaller artists may have more dedicated fans that are willing to pay above the asking price to support the artist.

**Methodology:** Like previous RQs, we will first begin by filtering tuples for artists only pertaining to genres of indie rock and electronic music from both the Spotify and Bandcamp datasets. To quantify popularity in this RQ we will be using popularity score in the Spotify playlist, and total sales in the Bandcamp dataset. Since we are only comparing a single feature of each dataset, our statistical analysis will be simpler for this RQ. Namely, we will plot popularity score as our independent variable, with Bandcamp sales as our dependent variable. Since the popularity metrics will be extremely skewed in their distributions, we will use Spearman’s correlation to quantify the relationship, and support our hypothesis, since it is significantly more robust in the face of skewed distributions.

### Data Sets ###

Bandcamp Sales Dataset (Kaggle): https://www.kaggle.com/datasets/mathurinache/1000000-bandcamp-sales 

1,000,000 individual Bandcamp sales transactions between Sept 9, 2020 - Oct 2, 2020.
Number of records: 1,000,000 transactions.
Number of attributes: 23 (although we won’t need every single one).

**Relevant variables to our analysis:**\
artist_name \
amount_paid_usd\
item_price\
amount_over_fmt (fan overpayment)\
item_type (album, track, merch)\
country\
utc_date


Spotify Tracks Dataset (Kaggle):
https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset 

This dataset contains Spotify’s track data, including track/artist meta-data, popularity scores, genres, and audio features.
Number of records: 114,000 tracks.
Number of attributes: 21 (again, we will not need to utilize every single one).

**Relevant variables to our analysis:**\
track_id\
artists\
track_name\
track_genre\
popularity\
danceability\
energy\
valence\
tempo\


Spotify Web API:
https://developer.spotify.com/documentation/web-api 

This official API contains Spotify content data (artists, tracks, albums, popularity) as a JSON file.
The number of records is based on our queries to the API, so until we make such queries we do not have a fixed number to report.
The number of attributes will also be based on our queries to the API; we will extract only those relevant to our analysis 

**Relevant variables to our analysis:**\
artist identifier\
follower counts\
popularity scores\
genre labels


### Keys and standardization ###

**Keys:** the common linking attribute across all three datasets is the artist name. However, since artist names are not guaranteed to be unique identifiers, we will retrieve Spotify’s unique artist IDs through the API and use those as our primary keys. Bandcamp artists will be mapped to Spotify artist IDs using standardized string matching (e.g., lowercasing, removing punctuation and delimiters), and if necessary, we will manually verify ambiguous matches.
The artist names from the (Kaggle) Spotify Tracks dataset will be used to query the Spotify Web API.
Since the Bandcamp dataset also includes artist names, we will map these to Spotify artist names to compare across platforms.

**Standardization:** The (Kaggle) Spotify Tracks dataset lists artist names separated by a delimiter for each value, so we’ll have to split this attribute up (likely duplicating rows where more than one artist is featured on a song). If Spotify’s Web API uses a different date-time format than that of Bandcamps, we must convert it to be consistent for our project. Popularity and sales variables may be highly skewed; we will consider log transformations where appropriate.


*We used AI to review the structure and clarity of this proposal, however all final decisions and analysis plans were determined by the group.*

