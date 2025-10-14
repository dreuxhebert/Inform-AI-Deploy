# db_connection_test.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Any
from bson import ObjectId, errors as bson_errors

from db import db  # uses your existing db.py (client + db)

app = FastAPI(title="Inform QA - Dev API")

# ---- CORS for local frontend ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- helpers ----
def oid(s: str) -> ObjectId:
    try:
        return ObjectId(s)
    except bson_errors.InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")

def serialize(doc: dict[str, Any]) -> dict[str, Any]:
    if not doc:
        return doc
    doc["id"] = str(doc.pop("_id"))
    return doc

def fmt_duration(seconds: Optional[int]) -> str:
    if not seconds or seconds < 0:
        return "00:00"
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"

# ---- Schemas ----
class DispatcherIn(BaseModel):
    name: str
    employee_id: Optional[str] = None

class DispatcherOut(DispatcherIn):
    id: str

# -----------------------------
# Routes
# -----------------------------
@app.get("/")
def root():
    return {"ok": True, "service": "mongo dev api"}

# ---- dispatchers ----
@app.post("/dispatchers/", response_model=DispatcherOut)
def create_dispatcher(dispatcher: DispatcherIn):
    doc = dispatcher.model_dump()
    result = db["dispatchers"].insert_one(doc)
    return {"id": str(result.inserted_id), **doc}

@app.get("/dispatchers/", response_model=List[DispatcherOut])
def list_dispatchers():
    docs = db["dispatchers"].find({}, {"name": 1, "employee_id": 1})
    return [{"id": str(d["_id"]), "name": d["name"], "employee_id": d.get("employee_id")} for d in docs]

@app.get("/dispatchers/{dispatcher_id}", response_model=DispatcherOut)
def get_dispatcher(dispatcher_id: str):
    doc = db["dispatchers"].find_one({"_id": oid(dispatcher_id)}, {"name": 1, "employee_id": 1})
    if not doc:
        raise HTTPException(status_code=404, detail="Dispatcher not found")
    return {"id": str(doc["_id"]), "name": doc["name"], "employee_id": doc.get("employee_id")}

# ---- interactions (table feed) ----
@app.get("/interactions")
def list_interactions():
    """
    Returns rows shaped for your frontend table.
    Reads optional fields from calls if present; falls back when missing.
    """
    cursor = db["calls"].find({}, {
        "call_id": 1,
        "dispatcher_id": 1,
        "duration_seconds": 1,
        "language": 1,
        "model": 1,
        "callType": 1,
        "status": 1,
        "sentiment": 1,
    })

    rows = []
    for c in cursor:
        disp_name = "Unknown"
        if c.get("dispatcher_id"):
            disp = db["dispatchers"].find_one({"_id": c["dispatcher_id"]}, {"name": 1})
            if disp:
                disp_name = disp.get("name", disp_name)

        rows.append({
            "id": str(c["_id"]),
            "fileName": c.get("call_id") or "(no id)",
            "dispatcher": disp_name,
            "language": c.get("language") or "N/A",
            "model": c.get("model") or "N/A",
            "callType": c.get("callType") or "Other",
            "duration": fmt_duration(c.get("duration_seconds")),
            "status": (c.get("status") or "processed"),
            "sentiment": (c.get("sentiment") or "neutral"),
        })
    return rows

# ---- simple seed endpoints (optional, helpful in dev) ----
class CallIn(BaseModel):
    dispatcher_id: str
    call_id: Optional[str] = None
    duration_seconds: Optional[int] = None
    direction: Optional[str] = None

@app.post("/calls/seed")
def seed_call(body: CallIn):
    d_id = oid(body.dispatcher_id)
    # ensure dispatcher exists
    if not db["dispatchers"].find_one({"_id": d_id}):
        raise HTTPException(status_code=404, detail="Dispatcher not found")
    doc = {
        "dispatcher_id": d_id,
        "call_id": body.call_id,
        "duration_seconds": body.duration_seconds,
        "direction": body.direction,
    }
    ins = db["calls"].insert_one(doc)
    return {"inserted_id": str(ins.inserted_id)}