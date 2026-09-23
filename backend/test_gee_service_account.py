import json
from pathlib import Path

import ee

PROJECT_ID = "inlaid-reach-509012-c3"
KEY_PATH = Path("credentials/inlaid-reach-509012-c3-4af425befbb4.json")

with KEY_PATH.open("r", encoding="utf-8") as f:
    credentials_info = json.load(f)

credentials = ee.ServiceAccountCredentials(
    credentials_info["client_email"],
    key_file=str(KEY_PATH),
)

ee.Initialize(
    credentials=credentials,
    project=PROJECT_ID,
)

print("Service account authentication successful!")

print(
    "Earth Engine test:",
    ee.Number(1).add(2).getInfo()
)