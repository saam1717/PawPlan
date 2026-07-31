import logging
import os
import requests

from dotenv import load_dotenv

from model.json.create_account_json import NewAccountStore
from model.json.uid_json import UserIdStore
from setup.firebase_setup import db

load_dotenv()
create_account = NewAccountStore()
uid_account = UserIdStore()
logger = logging.getLogger(f"pawplan.{__name__}")


def seed_uid_from_auth(auth):
    """Mirror an authenticated user's email into the local uid store.

    The model CRUD modules (task_crud, pet_crud) read their uid from this
    store, and main.py clears it on startup. Views that load while a session
    is already active (e.g. page refresh / navigating back to "/") must call
    this so Firestore reads/writes hit the right user document.

    Returns the seeded uid, or None if there is no usable auth context.
    """
    try:
        email = auth.user["email"]
    except (AttributeError, KeyError, TypeError):
        return None
    if not email:
        return None
    uid_account.set(str(email))
    return str(email)
API_KEY = os.getenv("FIREBASE_API_KEY") or os.getenv("FIREBASE_WEB_API_KEY")
if not API_KEY:
    raise ValueError("Missing FIREBASE_API_KEY in .env file")

BASE_URL = "https://identitytoolkit.googleapis.com/v1/accounts"

# For new accounts (register and oauth)
def create_user_doc():
    """Create the Firestore document for a newly registered user.

    The document is keyed by the user's email, which is the same identity used
    by the OAuth flow (seed_uid_from_auth / create_oauth_user_doc) and by
    log_in below, so every sign-in path resolves the same Firestore doc.
    """
    user_data = create_account.get()
    if not user_data or not user_data.get("email"):
        logger.debug("create_user_doc: no session data, skipping")
        return

    uid = user_data["email"]
    uid_account.set(uid)  # seed local uid so the app works immediately

    doc_ref = db.collection("users").document(uid)
    if doc_ref.get().exists:
        return

    db.collection("users").document(uid).set({"uid": uid})
    setup_user_details(uid)
    setup_pet(uid)

def setup_user_details(uid):
    user_data = create_account.get()

    if user_data is None:
        # logger.debug(f"No user details for UID: {uid}")
        pass
    else:
        username = user_data["username"]
        email = user_data["email"]
        gender = user_data["gender"]
        dob = user_data["dob"]

        data = {"username": username, "email": email, "gender": gender, "dob": dob}

        db.collection("users").document(str(uid)).collection("details").document("user details").set(data)
        # logger.debug(f"User details created for UID: {uid}")

def setup_pet(uid):
    db.collection("users").document(uid).collection("details").document("pets").set({"temp": "temp"})

def create_oauth_user_doc(uid: str):
    """Ensure a Firestore doc exists for an OAuth user (keyed by email)."""
    if not uid:
        return
    uid_account.set(uid)
    doc_ref = db.collection("users").document(uid)
    if doc_ref.get().exists:
        return
    doc_ref.set({"uid": uid})
    setup_pet(uid)

# to get uid in homepage
def get_uid():
    # set uid
    uid = uid_account.get()
    if not uid:
        logger.debug("get_uid: no uid set")
        return None

    # check doc
    doc_ref = db.collection("users").document(uid)
    doc = doc_ref.get()

    if doc.exists:
        logger.debug(f"User document exists for UID: {uid}")
        return uid
    else:
        logger.debug(f"User document does not exist for UID: {uid}")
        return None

class SignUpError(Exception):
    """Raised when Firebase sign-up fails, carrying Firebase's error code."""
    def __init__(self, code: str, message: str = ""):
        self.code = code
        self.message = message
        super().__init__(message or code)


def sign_up(email: str, password: str) -> str:
    resp = requests.post(
        f"{BASE_URL}:signUp?key={API_KEY}",
        json={"email": email, "password": password, "returnSecureToken": True},
    )
    if resp.status_code == 200:
        return resp.json()["localId"]

    error = resp.json().get("error", {})
    message = error.get("message", "")
    code = message.split(" : ")[0]  # e.g. "WEAK_PASSWORD" from "WEAK_PASSWORD : Password should be..."
    logger.debug(f"Sign up failed: {message}")
    raise SignUpError(code, message)


def log_in(email: str, password: str) -> str | None:
    resp = requests.post(
        f"{BASE_URL}:signInWithPassword?key={API_KEY}",
        json={"email": email, "password": password, "returnSecureToken": True},
    )
    if resp.status_code == 200:
        return resp.json()["localId"]
    logger.debug(f"Sign in failed: {resp.json().get('error', {}).get('message')}")
    return None