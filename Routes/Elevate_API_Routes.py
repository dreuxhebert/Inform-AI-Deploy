from pydantic import BaseModel
from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks

from Controllers.ElevateController import (
    get_interaction_id_download_url,
    get_status,
    get_cx_summary,
    get_transcription_url,
    get_general_summary,
    upload_audio,
    QA_Analysis
)

class FileRequest(BaseModel):
    download_uri: str

router = APIRouter(prefix="/elevate.api", tags=["Elevate API Calls"])

# Generates interaction id from elevate. Required for generating summary and transcription
@router.get("/getInteractionID")
def interaction_id(body: FileRequest):
    return get_interaction_id_download_url(body)

# Generates transcriptions using the download url. No need to upload file
@router.post("/getTranscription")
def generate_transcription(body: FileRequest):
    return get_transcription_url(body)

# Generates general summary. General is a model in elevate api.
@router.get("/general/Summary")
def generate_general_summary(interaction_id: str):
   return get_general_summary(interaction_id)

# Generates CX summary. CX is a model in elevate api.
@router.get("/CX-AI/Summary")
def generate_cx_summary(interaction_id: str):
    return get_cx_summary(interaction_id)

# Status is used to check if the uploaded call is "queued" | "processing" | "processed" | "failed"
@router.get("/checkStatus")
def generate_status(interaction_id: str):
    return get_status(interaction_id)

# Generates Interaction id -> Generated transcripts & summary -> returns the data to the frontend
@router.post("/uploadAudio")
async def audio_upload(
    audio_file: UploadFile = File(...),
    dispatcher: str = Form(""),
    call_type: str = Form(""),
    language: str = Form(""),
    notes: str = Form(""),
):
    result =  await upload_audio(audio_file, dispatcher, call_type, language, notes)
    return result

@router.get("/QA")
def qa_analysis():
    return QA_Analysis("8648dcae-3010-4c7b-aba9-f4b283043535")