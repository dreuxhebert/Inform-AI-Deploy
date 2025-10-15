from datetime import datetime

from fastapi import APIRouter
from models import CallSummary
from db_connect import db
from Controllers.CallController import (
    get_all_calls,
    create_call,
    serialize_call,
    get_by_type,
    get_by_date
)

router = APIRouter(prefix="/calls", tags=["Cards"])

@router.post("/createCall")
def create_call(call_data: CallSummary):
    call = call_data.model_dump()
    result = db["calls"].insert_one(call)
    call["id"] = result.inserted_id
    return {"Successfully added call"}

@router.get("/", response_model=list[CallSummary])
def get_calls():
    return [serialize_call(c) for c in get_all_calls()]

@router.get("/byType")
def get_calls_by_type():
    return get_by_type()

@router.get("/byDate")
def get_calls_by_date():
    return get_by_date()


# @router.get("/{card_id}")
# def get_card(card_id: str):
#     return get_card_by_id(card_id)
#
# @router.put("/{card_id}")
# def modify_card(card_id: str, card: Card):
#     return update_card(card_id, card.dict())
#
# @router.delete("/{card_id}")
# def remove_card(card_id: str):
#     return delete_card(card_id)
