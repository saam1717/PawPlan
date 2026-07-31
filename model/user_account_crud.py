import logging
from setup.firebase_setup import db

logger = logging.getLogger(f"pawplan.{__name__}")

def get_data(uid):
    doc_ref = db.collection("users").document(uid).collection("details").document("user details")

    doc = doc_ref.get()
    if doc.exists:
        logger.debug(f"Document data: {doc.to_dict()}")  # just print for now
        return doc.to_dict()
    else:
        logger.debug(f"No such document!")