from db_connect import calls
from db_connect import db

def serialize_call(call):
    call["_id"] = str(call["_id"])  # Convert ObjectId to string
    return call


async def create_call(call_data: calls):
    call = call_data.dict(by_alias=True)
    call["created_at"] = str(call["created_at"])
    result = await db["calls"].insert_one(call)
    call["_id"] = str(result.inserted_id)
    return {"message": "Call added successfully", "id": call["_id"]}

def get_all_calls():
    all_calls = list(calls.find())
    return [serialize_call(c) for c in all_calls]

def get_by_type():
    pipeline = [
        {"$group": {"_id": "$callType", "count": {"$sum": 1}}}
    ]
    result = list(calls.aggregate(pipeline))

    # Rename _id -> type for frontend clarity
    formatted_result = [{"type": r["_id"], "count": r["count"]} for r in result if r["_id"] is not None]
    return formatted_result

def get_by_date():
    pipeline = [
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$created_at"
                    }
                },
                "count": {"$sum": 1}
            }
        },
        {
            "$project": {
                "type": "$_id",
                "count": 1,
                "_id": 0
            }
        },
        {"$sort": {"type": 1}}
    ]
    result = list(calls.aggregate(pipeline))
    formatted_result = [{"type": r["type"], "count": r["count"]} for r in result if r.get("type") is not None]
    return formatted_result


# def update_card(card_id: str, card_data):
#     result = card_collection.update_one({"_id": ObjectId(card_id)}, {"$set": card_data})
#     if result.matched_count == 0:
#         raise HTTPException(status_code=404, detail="Card not found")
#     return {"message": "Card updated successfully"}

# def delete_card(card_id: str):
#     result = card_collection.delete_one({"_id": ObjectId(card_id)})
#     if result.deleted_count == 0:
#         raise HTTPException(status_code=404, detail="Card not found")
#     return {"message": "Card deleted successfully"}


# --- Test section ---
if __name__ == "__main__":

    # 2️⃣ Fetch all documents
    all_data = get_all_calls()
    print("\nAll documents in 'calls' collection:")
    for doc in all_data:
        print(doc)


