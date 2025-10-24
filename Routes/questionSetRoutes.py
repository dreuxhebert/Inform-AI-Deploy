from typing import List

from pydantic import BaseModel
from fastapi import APIRouter

from Controllers.questionSetController import (
    add_question,
    get_question,
    edit_question
)

class QuestionSet(BaseModel):
    originalQuestion: str
    editedQuestion: str
    questionDescription: str
    type: List[str] = []

class EditQuestion(BaseModel):
    _id: str
    editedText: str
    editedState: str

router = APIRouter(prefix="/questionSet", tags=["Questions Set"])

@router.post("/")
def get_question_list(body: QuestionSet):
    return add_question(body)

@router.get("/")
def get_all_questions():
    return get_question()

@router.patch("/")
def edit_question(body: EditQuestion):
    return edit_question(body)