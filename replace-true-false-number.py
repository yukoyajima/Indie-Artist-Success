#sql file replace the true false of "explicit" to numbers because oracle doesnt take boolean as type

import re

input_file = "bandcamp_spotify_data_clean.sql"
output_file = "bandcamp_spotify_data_bool.sql"

with open(input_file, "r", encoding="utf-8") as f:
    content = f.read()

content = re.sub(r',\s*True\b', ', 1', content)
content = re.sub(r',\s*False\b', ', 0', content)

with open(output_file, "w", encoding="utf-8") as f:
    f.write(content)

