# sql file replace & with "and" 

input_file = "bandcamp_spotify_data.sql"
output_file = "bandcamp_spotify_data_clean.sql"

with open(input_file, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("&", " and ")

with open(output_file, "w", encoding="utf-8") as f:
    f.write(content)

