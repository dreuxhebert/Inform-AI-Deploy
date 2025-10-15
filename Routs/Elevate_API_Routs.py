from pydantic import BaseModel
from fastapi import APIRouter, UploadFile, File, Form

from Controllers.ElevateController import (
    get_interaction_id_download_url,
    get_status,
    get_cx_summary,
    get_transcription_url,
    get_general_summary,
    upload_audio
)

class FileRequest(BaseModel):
    download_uri: str

router = APIRouter(prefix="/elevate.api", tags=["Elevate API Calls"])

@router.get("/getInteractionID")
def interaction_id(body: FileRequest):
    return get_interaction_id_download_url(body)

@router.post("/getTranscription")
def generate_transcription(body: FileRequest):
    return get_transcription_url(body)

@router.get("/general/Summary")
def generate_general_summary(interaction_id: str):
   return get_general_summary(interaction_id)

@router.get("/CX-AI/Summary")
def generate_cx_summary(interaction_id: str):
    return get_cx_summary(interaction_id)

@router.get("/checkStatus")
def generate_status(interaction_id: str):
    return get_status(interaction_id)

@router.post("/uploadAudio")
async def audio_upload(
    audio_file: UploadFile = File(...),
    dispatcher: str = Form(""),
    call_type: str = Form(""),
    language: str = Form(""),
    notes: str = Form("")
):
    result = await upload_audio(audio_file, dispatcher, call_type, language, notes)
    return result