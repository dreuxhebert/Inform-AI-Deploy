# seed_bulk.py
import random
from datetime import timedelta, datetime
from db import db

dispatchers = db["dispatchers"]
calls = db["calls"]

# ----- helpers -----
def pick(xs): return random.choice(xs)
def dur(min_s=45, max_s=600): return random.randint(min_s, max_s)

def fake_transcript(dispatcher_name: str) -> str:
    return (
        "Dispatcher: 911, what's your emergency?\n"
        "Caller: There's been a car accident at 5th and Main.\n"
        f"Dispatcher: {dispatcher_name} speaking. Is anyone injured?\n"
        "Caller: Yes, one person looks hurt.\n"
        "Dispatcher: Stay on the line. I'm dispatching EMS now.\n"
    )

def fake_summary() -> str:
    return "Vehicle collision reported, location verified, EMS dispatched. Caller remained on scene."

LANGS = ["English", "Spanish", "English", "English", "English", "Spanish"]
MODELS = ["gpt-4o-mini", "gpt-4.1", "sonnet-3.5", "gpt-4o-mini"]
CALL_TYPES = ["Medical", "Fire", "Traffic", "Shooting", "Other", "Traffic"]
STATUSES = ["queued", "processing", "processed", "processed", "processed", "failed"]
SENTIMENTS = ["positive", "neutral", "negative", "neutral", "positive", "neutral"]

def ensure_dispatchers():
    names = [
        ("Jane Doe", "D123"),
        ("John Smith", "D456"),
        ("Alex Johnson", "D789"),
    ]
    ids = []
    for name, emp in names:
        existing = dispatchers.find_one({"employee_id": emp})
        if existing:
            ids.append(existing["_id"])
        else:
            ins = dispatchers.insert_one({"name": name, "employee_id": emp})
            ids.append(ins.inserted_id)
    return ids

def seed_calls(disp_ids):
    # clear old demo calls if you want a clean slate (optional)
    # calls.delete_many({})  # uncomment to wipe calls first

    rows = []
    now = datetime.utcnow()
    for i in range(12):
        d_id = pick(disp_ids)
        d_doc = dispatchers.find_one({"_id": d_id}, {"name": 1}) or {}
        d_name = d_doc.get("name", "Dispatcher")

        row = {
            "dispatcher_id": d_id,
            "call_id": f"CALL-{now.strftime('%Y%m%d')}-{i:03d}",
            "duration_seconds": dur(),
            "direction": pick(["Inbound", "Outbound"]),
            "language": pick(LANGS),
            "model": pick(MODELS),
            "callType": pick(CALL_TYPES),
            "status": pick(STATUSES),
            "sentiment": pick(SENTIMENTS),
            "transcript": fake_transcript(d_name),
            "summary": fake_summary(),
            "created_at": now - timedelta(minutes=i*3),
        }
        rows.append(row)

    if rows:
        calls.insert_many(rows)
        print(f"Inserted {len(rows)} calls.")

if __name__ == "__main__":
    ids = ensure_dispatchers()
    seed_calls(ids)
    print("Seed complete.")