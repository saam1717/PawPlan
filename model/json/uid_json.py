import tempfile
import os


class UserIdStore:
    def __init__(self):
        self.filepath = os.path.join(tempfile.gettempdir(), "current_user_id.txt")
        self.tmp_path = self.filepath + ".tmp"

    def set(self, uid):
        if not uid:
            return
        with open(self.tmp_path, "w") as f:
            f.write(str(uid))
        os.replace(self.tmp_path, self.filepath)  # atomic on POSIX, no torn reads

    def get(self):
        if not os.path.exists(self.filepath):
            return None
        with open(self.filepath, "r") as f:
            content = f.read().strip()
        return content or None

    def clear(self):
        for path in (self.filepath, self.tmp_path):
            if os.path.exists(path):
                os.remove(path)
