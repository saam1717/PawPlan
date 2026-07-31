import tempfile
import os
import json


class NewAccountStore:
    def __init__(self):
        self.filepath = os.path.join(tempfile.gettempdir(), "current_user_session.json")

    def set(self, username, email, gender, date_of_birth):
        data = {
            "username": username,  # doc id / uid
            "email": email,
            "gender": gender,
            "dob": date_of_birth,
        }
        with open(self.filepath, "w") as f:
            json.dump(data, f)

    def get(self):
        if not os.path.exists(self.filepath):
            return None
        with open(self.filepath, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return None

    def get_username(self):
        """Convenience accessor since username acts as the uid/doc key."""
        data = self.get()
        return data["username"] if data else None

    def clear(self):
        if os.path.exists(self.filepath):
            os.remove(self.filepath)


if __name__ == "__main__":
    store = NewAccountStore()
    store.set(
        username="cereal",
        email="cereal@example.com",
        gender="male",
        date_of_birth="2003-01-01",
    )
    print(store.get())
    print(store.get_username())
    store.clear()
    print(store.get())