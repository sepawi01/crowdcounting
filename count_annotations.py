# Just a simple script to count the number of annotations in a given annotation file from label-studio.

import json

with open("temp_annotationfille.json", "r") as f:
    data = json.load(f)
    annotations = data["annotations"][0]["result"]
    head_annotations = [a for a in annotations if "Head" in a["value"]["keypointlabels"]]
    print(f"Number of annotations: {len(head_annotations)}")