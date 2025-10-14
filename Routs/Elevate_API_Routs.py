from pydantic import BaseModel
import os
import time
import requests
from fastapi import HTTPException, APIRouter

router = APIRouter(prefix="/elevate.api", tags=["Elevate API Calls"])

api_token = os.getenv("ELEVATEAI_API_TOKEN")
api_url = os.getenv("ELEVATEAI_BASE_URL")


# Request body model
class FileRequest(BaseModel):
    downloadUri: str


@router.post("/getInteractionID")
def get_interaction_id(body: FileRequest):
    declare_url = f"{api_url}/interactions"
    payload = {
        "type": "audio",
        "model": "echo",
        "languageTag": "en-us",
        "downloadUri": body.downloadUri,
    }

    headers = {
        'X-API-Token': api_token,
        'Content-Type': 'application/json'
    }

    try:
        resp = requests.post(declare_url, json=payload, headers=headers, verify=False, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Declare request error: {e}")

    decl = resp.json()
    interaction_id = decl.get("interactionIdentifier") or decl.get("id")
    if not interaction_id:
        raise HTTPException(status_code=500, detail="No interaction ID returned")
    return {"interaction_id": interaction_id}


@router.post("/getTranscription")
def get_transcription(body: FileRequest):
    # Step 1: Get interaction ID
    transaction_id = get_interaction_id(body)["interaction_id"]
    if not transaction_id:
        raise HTTPException(status_code=400, detail="Interaction ID not set")

    # Step 2: Poll for processing status
    max_tries = 80
    wait_seconds = 5
    for attempt in range(max_tries):
        status_url = f"{api_url}/interactions/{transaction_id}/status"
        headers = {'X-API-Token': api_token, 'Accept': 'gzip, deflate'}
        status_resp = requests.get(status_url, headers=headers, verify=False, timeout=30)
        status_resp.raise_for_status()
        status = status_resp.json().get("status", "").lower()
        if status == "processed":
            break
        time.sleep(wait_seconds)
    else:
        raise HTTPException(status_code=504, detail="Processing timed out")

    # Step 3: Fetch transcript
    headers = {'X-API-Token': api_token, 'Content-Type': 'application/json'}
    transcription_resp = requests.get(
        f"{api_url}/interactions/{transaction_id}/transcripts/punctuated",
        headers=headers,
        verify=False,
        timeout=30,
    )
    transcription_resp.raise_for_status()
    transcript = transcription_resp.json()

    return {"transaction_id": transaction_id, "transcript": transcript}


@router.get("/{interaction_id}/general/Summary")
def get_general_summary(interaction_id: str):
    headers = {'X-API-Token': api_token, 'Accept': 'gzip, deflate'}
    summary_resp = requests.get(
        f"{api_url}/interactions/{interaction_id}/gen-ai/summary",
        headers=headers,
        verify=False,
        timeout=30,
    )
    summary_resp.raise_for_status()
    return summary_resp.json()

@router.get("/{interaction_id}/CX-AI/Summary")
def get_summary(interaction_id: str):
    payload = ''
    headers = {
        'X-API-Token': api_token,
        'Accept': 'gzip, deflate',
    }
    try:
        summary = requests.get(f'{api_url}/interactions/{interaction_id}/gen-ai/cx/summary', headers=headers,
                               data=payload, verify=False)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Summary request error: {e}")

    if not summary.ok:
        raise HTTPException(status_code=summary.status_code, detail=f"Summary fetching failed:  {summary.text}")

    output = summary.json()
    return output
