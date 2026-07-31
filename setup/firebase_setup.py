import json
import os
import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    cred_json = os.environ.get("FIREBASE_CREDENTIALS_JSON")
    if cred_json:
        # Production (Railway): load from env var
        cred_dict = json.loads(cred_json)
        cred = credentials.Certificate(cred_dict)
    else:
        # Local development: fall back to the file
        cred = credentials.Certificate("./pawplan_account.json")
    firebase_admin.initialize_app(cred)

db = firestore.client(database_id="pawplan")