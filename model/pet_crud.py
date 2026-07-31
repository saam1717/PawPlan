from firebase_admin import firestore

from model.json.uid_json import UserIdStore
from model.task_crud import remove_tasks_by_pet
from setup.firebase_setup import db
import logging
logger = logging.getLogger(f"pawplan.{__name__}")
uid_account = UserIdStore()

# The 5 pastel colors a pet can be assigned (name -> hex), shared by the
# add-pet form and every view that reflects a pet's color on its tasks.
PASTEL_PET_COLORS = {
    "Yellow": "#FFF59D",
    "Red": "#FF8A80",
    "Orange": "#FFCC80",
    "Blue": "#81D4FA",
    "Green": "#A5D6A7",
}
DEFAULT_PET_COLOR = PASTEL_PET_COLORS["Yellow"]

# Maximum number of pets a single account can have.
MAX_PETS = 5

def get_specific_pet(uid, index):
    pet_list = get_pet_list(uid)

    if not pet_list:
        logger.warning("get_specific_pet: no pets for uid=%s", uid)
        return {}
    return pet_list[index]

def get_pet_list(uid=None):
    pet_list = []
    uid = uid or uid_account.get()
    if not uid:
        logger.debug("get_pet_list: no uid set, returning empty list")
        return pet_list

    pets_ref = db.collection("users").document(uid).collection("details").document("pets")
    doc = pets_ref.get()
    if doc.exists:
        data = doc.to_dict()
        if not data.get("pets", []):
            logger.debug("pet list empty")
        pet_list = data.get("pets", [])
        logger.debug("Pet list: %s", pet_list)
    else:
        logger.debug("No such document!")

    return pet_list

def add_pet(name, pet_type, age, breed, allergies, color=DEFAULT_PET_COLOR):
    """Add a pet, enforcing a maximum of MAX_PETS pets per account.

    Returns a ``(success, message)`` tuple. On failure ``message`` explains
    why (e.g. limit reached), on success it's just confirmation.
    """
    uid = uid_account.get()
    if not uid:
        logger.error("add_pet: no uid set, aborting")
        return False, "User not signed in."

    if len(get_pet_list(uid)) >= MAX_PETS:
        logger.warning(
            "add_pet: pet limit of %d reached for uid=%s, refusing '%s'",
            MAX_PETS, uid, name,
        )
        return False, f"You can only have up to {MAX_PETS} pets. Delete one before adding another."

    pets_ref = db.collection("users").document(uid).collection("details").document("pets")
    pets_ref.set({
        "pets": firestore.ArrayUnion([{
            "name": name,
            "type": pet_type,
            "age": age,
            "breed": breed,
            "allergies": allergies,
            "color": color or DEFAULT_PET_COLOR,
        }])
    }, merge=True)
    logger.info(f"Added pet '{name}' for uid={uid}")
    return True, "Pet added."

def get_pet_color_map(uid=None):
    """Map each pet's name to its stored pastel color, defaulting for old pets."""
    return {
        pet.get("name"): pet.get("color") or DEFAULT_PET_COLOR
        for pet in get_pet_list(uid)
        if pet.get("name")
    }

def remove_pet(uid, name):
    if not uid:
        logger.error("remove_pet: no uid set, aborting")
        return

    doc_ref = db.collection("users").document(uid).collection("details").document("pets")
    doc = doc_ref.get()
    data = doc.to_dict()

    pets = data.get("pets", [])
    target = next((pet for pet in pets if pet.get("name") == name), None)

    if target:
        doc_ref.update({
            "pets": firestore.ArrayRemove([target])
        })
        # Tasks live in a separate document, so cascade-delete any that
        # reference this pet by name to avoid orphaned reminders.
        remove_tasks_by_pet(name, uid)
    else:
        logger.warning(f"No pet named '{name}' found for uid={uid}")


