# python script to replace // with / / for Oracle

input_file = "bandcamp_spotify_data.sql"        
output_file = "bandcamp_spotify_data_fixed.sql" 

with open(input_file, "r", encoding="utf-8") as f:
    sql_content = f.read()

sql_content = sql_content.replace("//", "/ /")

with open(output_file, "w", encoding="utf-8") as f:
    f.write(sql_content)

print(f"Fixed SQL file written to '{output_file}'")