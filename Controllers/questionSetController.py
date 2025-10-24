from typing import List
from pydantic import BaseModel
from db_connect import questions as qa_collection
from fastapi import HTTPException
from bson import ObjectId

class QuestionSet(BaseModel):
    originalQuestion: str
    editedQuestion: str
    questionDescription: str
    type: List[str] = []

class EditQuestion(BaseModel):
    _id: str
    editedText: str
    editedState: str


def add_question(question: QuestionSet):
    try:
        result = qa_collection.insert_one(question.model_dump(by_alias=True))
        return {"message": "Question added successfully", "id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_question():
    try:
        result = list(qa_collection.find({}))

        # Convert ObjectId to string for JSON serialization
        for doc in result:
            doc["_id"] = str(doc["_id"])

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def edit_question(changes: EditQuestion):
    # 1) Validate ObjectId
    try:
        oid = ObjectId(changes._id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid _id")

    # 2) Perform the update
    result = qa_collection.update_one(
        {"_id": oid},
        {"$set": {"editedQuestion": changes.editedText}},
        {"$set": {"state": changes.editedState}},
    )

    # 3) Handle not found
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Question not found")

    # 4) Fetch the updated document (optional)
    updated = qa_collection.find_one({"_id": oid})
    updated["_id"] = str(updated["_id"])

    return {
        "message": "Question updated successfully",
        "modified_count": result.modified_count,  # can be 0 if same value
        "data": updated
    }
