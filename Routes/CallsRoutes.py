from fastapi import APIRouter
from models import CallSummary
from Controllers.CallController import (
    get_all_calls,
    create_call,
    serialize_call,
    get_by_type,
    get_by_date
)

router = APIRouter(prefix="/calls", tags=["Cards"])


#Adds uploaded call to the database
@router.post("/createCall")
def create_call_router(call_data: CallSummary):
    return create_call(call_data)



# Fetches all the calls from the database
@router.get("/", response_model=list[CallSummary])
def get_calls():
    return [serialize_call(c) for c in get_all_calls()]



# Gives data by their type
# example:{
#     fire : 3
#     shooting : 6
# }
@router.get("/byType")
def get_calls_by_type():
    return get_by_type()


# Gives data by their type
# example:{
#     10/16/25 : 3
#     10/15/25 : 6
# }
@router.get("/byDate")
def get_calls_by_date():
    return get_by_date()