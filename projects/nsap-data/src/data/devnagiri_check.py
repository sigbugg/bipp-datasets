import json
from pathlib import Path
import pandas as pd

dir_path = Path.cwd()
interim_path = Path.joinpath(dir_path, "data", "interim")
all_names_path = Path.joinpath(interim_path,"all_names.json")

with open(str(all_names_path), "r", errors="ignore", encoding="utf-8") as outfile:
        #print(all_names_path)
        all_subdistricts = json.load(outfile)

all_subdistricts = pd.DataFrame(all_subdistricts)
#print(all_subdistricts['sub_district_name'])
count = 0
for sub_district in all_subdistricts['sub_district_name']:
    if not str.isascii(sub_district):
        print(
            f"Devanagari in sub_district name at {sub_district}"
        )
        count=count+1
print(count)
print(count/len(all_subdistricts['sub_district_name'])*100)
