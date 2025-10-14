# models.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId

# ---- Helper to allow Pydantic to work with Mongo ObjectId ----
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


# ---------------------------
# Dispatcher
# ---------------------------
class Dispatcher(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    employee_id: Optional[str] = None  # optional internal HR ID

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}


# ---------------------------
# Call
# ---------------------------
class Call(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")

    dispatcher_id: Optional[PyObjectId] = None

    # --- Core timing / identifiers ---
    start_time: datetime = Field(default_factory=datetime.utcnow)
    stop_time: Optional[datetime] = None
    rec_start_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    call_id: Optional[str] = None
    cls_call_id: Optional[str] = None
    call_class: Optional[str] = None
    parent_cls_call_id: Optional[str] = None
    interaction_type: Optional[str] = None

    # --- Station / Trunk / Channel / Logger ---
    station: Optional[str] = None
    trunk: Optional[str] = None
    trunk_label: Optional[str] = None
    logger: Optional[str] = None
    channel: Optional[str] = None
    recorded: bool = True
    screen_logger: Optional[str] = None
    screen_token: Optional[str] = None
    screen_recorded: bool = False

    # --- Direction / Caller / Dial info ---
    direction: Optional[str] = None
    phone_number: Optional[str] = None
    dialed_in: Optional[str] = None
    dtmf: Optional[str] = None

    # --- Agent/User fields (keeping redundant text copies) ---
    agent_name: Optional[str] = None
    agent_id_text: Optional[str] = None
    user_id: Optional[str] = None

    # --- Status / Flags / Comments ---
    comment: Optional[str] = None
    flags: Optional[str] = None
    status: Optional[str] = None
    unit: Optional[str] = None
    locked: bool = False
    wrap_up_time: Optional[int] = None
    to_delete: bool = False

    # --- QA / Programs / Tags ---
    qa: bool = False
    qa_program: Optional[str] = None
    rec_program: Optional[str] = None
    rec_initiator: Optional[str] = None
    call_tags: Optional[str] = None
    evaluated: bool = False

    # --- Email metadata ---
    email_ref_id: Optional[str] = None
    reply_email_ref_id: Optional[str] = None
    email_subject: Optional[str] = None
    email_from_address: Optional[str] = None
    email_to_address: Optional[str] = None
    email_sender: Optional[str] = None

    # --- Archive metadata ---
    vc_archive_path: Optional[str] = None
    i_archive_id_high: Optional[int] = None
    i_archive_id_low: Optional[int] = None
    i_archive_class: Optional[int] = None
    vc_sc_server_id: Optional[str] = None
    vc_archive_unique_id: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}


# ---------------------------
# Transcript
# ---------------------------
class Transcript(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    call_id: PyObjectId

    text: str
    word_count: Optional[int] = None
    ai_summary: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}


# ---------------------------
# Evaluation
# ---------------------------
class Evaluation(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    call_id: PyObjectId

    ai_score: Optional[float] = None
    strengths: Optional[str] = None
    improvements: Optional[str] = None
    reviewed_by_supervisor: bool = False

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
