from firebase_admin import firestore

from model.json.uid_json import UserIdStore
from setup.firebase_setup import db
from datetime import datetime, timezone, date, timedelta
import logging
import re
logger = logging.getLogger(f"pawplan.{__name__}")


uid_account = UserIdStore()

# Matches the day_names saved by taskboard_input.py's AlarmClockSelector
WEEKDAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _alarm_of(task):
    return task.get("alarm") or {}


def _split_day_names(day_names):
    """Normalize day_names, which may be stored as a list or a joined string."""
    if not day_names:
        return []
    if isinstance(day_names, str):
        return [name.strip() for name in re.split(r"[,\s]+", day_names) if name.strip()]
    return list(day_names)


def task_occurs_on(task, target_date):
    """True if the task's schedule (repeating days or specific date) falls on target_date."""
    day_names = _split_day_names(_alarm_of(task).get("day_names"))
    if day_names:
        return WEEKDAY_NAMES[target_date.weekday()] in day_names
    date_str = _alarm_of(task).get("date")
    if date_str:
        try:
            return date.fromisoformat(date_str) == target_date
        except ValueError:
            return False
    return False


def task_occurrences(tasks, start_date, days_ahead=7):
    """Expand tasks into (occurrence_date, task) pairs, one per scheduled day.

    Repeating tasks are expanded to each selected weekday inside the window;
    single-date tasks yield their date if it falls in the window.
    """
    end_date = start_date + timedelta(days=days_ahead)
    occurrences = []
    for task in tasks:
        day_names = _split_day_names(_alarm_of(task).get("day_names"))
        if day_names:
            for offset in range(days_ahead):
                candidate = start_date + timedelta(days=offset)
                if WEEKDAY_NAMES[candidate.weekday()] in day_names:
                    occurrences.append((candidate, task))
        else:
            date_str = _alarm_of(task).get("date")
            if date_str:
                try:
                    task_date = date.fromisoformat(date_str)
                except ValueError:
                    continue
                if start_date <= task_date < end_date:
                    occurrences.append((task_date, task))
    return occurrences


def split_tasks_by_occurrence(tasks, target_date, days_ahead=7):
    """Split tasks into per-day (date, task) pairs for today and the upcoming week.

    A task scheduled on multiple days (e.g. Fri + Sun) yields one entry per day.
    """
    occurrences = task_occurrences(tasks, target_date, days_ahead)
    todays = [(d, t) for d, t in occurrences if d == target_date]
    upcoming = [(d, t) for d, t in occurrences if d > target_date]
    upcoming.sort(key=lambda pair: pair[0])
    return todays, upcoming


def format_occurrence_date(occ_date, today=None):
    """Short label for a task occurrence, e.g. "Today (Fri)" or "Sun, Aug 02"."""
    today = today or date.today()
    if occ_date == today:
        return f"Today ({occ_date.strftime('%a')})"
    return occ_date.strftime("%a, %b %d")

# read task
def get_task_list(uid=None):
    task_list = []
    uid = uid or uid_account.get()
    if not uid:
        logger.debug("get_task_list: no uid set, returning empty list")
        return task_list

    tasks_ref = db.collection("users").document(uid).collection("details").document("tasks")

    doc = tasks_ref.get()
    if doc.exists:
        data = doc.to_dict()
        if not data.get("tasks", []):
            logger.debug("task list empty")
        task_list = data.get("tasks", [])
        logger.debug("Task list: %s", task_list)
    else:
        logger.debug("No such document!")

    return task_list

# add task
def add_task(task_name, pet_name, description, alarm, uid=None):
    """Persist a new task to Firestore.

    Returns True on success, False if no uid was available (so callers can
    surface a real error instead of silently "succeeding").
    """
    uid = uid or uid_account.get()
    if not uid:
        logger.error("add_task: no uid set, aborting")
        return False

    tasks_ref = db.collection("users").document(uid).collection("details").document("tasks")

    # append to existing

    # new task based on pet
    tasks_ref.set({
        "tasks": firestore.ArrayUnion([{
            "task_name": task_name,
            "pet_name": pet_name,
            "description": description,
            "created_at": datetime.now(timezone.utc),
            "alarm": alarm,
        }])
    }, merge=True)
    logger.info("Added task '%s' for uid=%s", task_name, uid)
    return True


def _normalize_task_value(value):
    """Recursively normalize a value so task dicts read from Firestore compare
    equal across separate reads (datetimes are the common gotcha)."""
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _normalize_task_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize_task_value(v) for v in value]
    return value


def _find_task_index(tasks, target_task):
    target = _normalize_task_value(target_task)
    for i, task in enumerate(tasks):
        if _normalize_task_value(task) == target:
            return i
    return None


# complete (check off) a single task occurrence
def complete_task_occurrence(task, occurrence_date, uid=None):
    """Check off one occurrence of a task and persist it to Firestore.

    - Repeating task with multiple scheduled days: remove the completed
      weekday from ``day_names`` and its matching number from ``days``.
    - Repeating task with a single day, or a one-off date task: delete the
      task from the tasks array entirely.

    Returns True if the occurrence was completed/removed, False if the task
    wasn't found or wasn't scheduled on ``occurrence_date``.
    """
    uid = uid or uid_account.get()
    if not uid:
        logger.error("complete_task_occurrence: no uid set, aborting")
        return False

    tasks = get_task_list(uid)
    if not tasks:
        return False

    idx = _find_task_index(tasks, task)
    if idx is None:
        logger.warning("complete_task_occurrence: task not found, skipping")
        return False

    scheduled_task = tasks[idx]
    alarm = dict(scheduled_task.get("alarm") or {})
    day_names = _split_day_names(alarm.get("day_names"))

    if day_names:
        day_name = WEEKDAY_NAMES[occurrence_date.weekday()]
        if day_name not in day_names:
            logger.warning(
                "complete_task_occurrence: %r not scheduled on %s",
                scheduled_task.get("task_name"), day_name,
            )
            return False

        if len(day_names) > 1:
            # multiple days -> drop only the completed day from the schedule
            alarm["day_names"] = [d for d in day_names if d != day_name]
            days = alarm.get("days")
            if isinstance(days, list):
                day_index = WEEKDAY_NAMES.index(day_name)
                alarm["days"] = [d for d in days if d != day_index]
            else:
                alarm["days"] = []
            tasks[idx] = {**scheduled_task, "alarm": alarm}
            logger.debug(
                "Removed %s from %r, days left: %s",
                day_name, scheduled_task.get("task_name"), alarm["day_names"],
            )
        else:
            # only one day left -> remove the whole task
            tasks.pop(idx)
            logger.debug("Removed single-day task %r", scheduled_task.get("task_name"))
    else:
        # one-off date task -> checking it off deletes it
        tasks.pop(idx)
        logger.debug("Removed one-off task %r", scheduled_task.get("task_name"))

    tasks_ref = db.collection("users").document(uid).collection("details").document("tasks")
    tasks_ref.set({"tasks": tasks}, merge=True)
    return True


def remove_tasks_by_pet(pet_name, uid=None):
    """Delete every task assigned to a pet (matched via the task's ``pet_name``).

    Called when a pet is deleted so orphaned tasks don't linger in the
    separate tasks document. No-op if the tasks document is missing or no
    task references the pet.
    """
    uid = uid or uid_account.get()
    if not uid:
        logger.error("remove_tasks_by_pet: no uid set, aborting")
        return

    tasks = get_task_list(uid)
    remaining = [t for t in tasks if t.get("pet_name") != pet_name]
    removed = len(tasks) - len(remaining)

    if removed == 0:
        logger.debug("remove_tasks_by_pet: no tasks found for pet '%s'", pet_name)
        return

    tasks_ref = db.collection("users").document(uid).collection("details").document("tasks")
    tasks_ref.set({"tasks": remaining}, merge=True)
    logger.info("Removed %d task(s) for pet '%s' (uid=%s)", removed, pet_name, uid)