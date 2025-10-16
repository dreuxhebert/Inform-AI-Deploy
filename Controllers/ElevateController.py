import asyncio

from pydantic import BaseModel
import os
import time
import requests
from fastapi import HTTPException, UploadFile, File, Form
import aiofiles

api_token = os.getenv("ELEVATEAI_API_TOKEN")
api_url = os.getenv("ELEVATEAI_BASE_URL")


# Request body model
class FileRequest(BaseModel):
    download_uri: str


# This generates transcriptions with the download url given in the body
def get_interaction_id_download_url(body: FileRequest):
    declare_url = f"{api_url}/interactions"
    payload = {
        "type": "audio",
        "model": "echo",
        "languageTag": "en-us",
        "downloadUri": body.download_uri
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


# Fetches interaction id using elevate api.
def get_interaction_id():
    declare_url = f"{api_url}/interactions"
    payload = {
        "type": "audio",
        "model": "echo",
        "languageTag": "en-us",
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


# Generates transcriptions using the download url
def get_transcription_url(body: FileRequest):
    transaction_id = get_interaction_id_download_url(body)["interaction_id"]
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


# Generates transcriptions
def get_transcription(transaction_id: str):
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


# Generates general summary for the transcriptions
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


# Generates CS summary for the transcriptions
def get_cx_summary(interaction_id: str):
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


# Fetches the status of the uploaded call
def get_status(interaction_id: str):
    try:
        headers = {
            'X-API-Token': api_token,
            'Accept': 'gzip, deflate',
        }
        status_resp = requests.get(
            f"{api_url}/interactions/{interaction_id}/status",
            headers=headers,
        )
        if status_resp.status_code != 200:
            raise HTTPException(status_code=404, detail=f"Status request error: {status_resp.text}")
        return status_resp
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Status request error: {e}")


# Upload calls from the front end
async def upload_audio(
    audio_file: UploadFile = File(...),
    dispatcher: str = Form(""),
    call_type: str = Form(""),
    language: str = Form(""),
    notes: str = Form("")
):
    UPLOAD_DIR = "uploads"
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(UPLOAD_DIR, audio_file.filename)

    try:
        interaction_id = get_interaction_id()["interaction_id"]
        headers = {
            "X-API-Token": api_token,
            "Accept": "gzip, deflate",
        }

        # Save uploaded file to disk
        async with aiofiles.open(file_path, "wb") as out_file:
            while chunk := await audio_file.read(1024 * 1024):  # 1MB chunks
                await out_file.write(chunk)

        # Forward to external API (blocking call — acceptable if traffic is low)
        with open(file_path, "rb") as f:
            files = {"audio_file": (audio_file.filename, f, audio_file.content_type or "audio/wav")}
            response = requests.post(
                f"{api_url}/interactions/{interaction_id}/upload",
                headers=headers,
                files=files,
                timeout=60,
            )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        # If you want a pause, make it non-blocking
        await asyncio.sleep(2)
        print("Starting to generate transcription")
        # Fetch results
        transcript = get_transcription(interaction_id)
        print("Finished generating transcription starting summary")
        summary = get_general_summary(interaction_id)["summary"]
        print("Finished generating general summary")
        try:
            transcription = "Dispatcher: "
            t = transcript["transcript"]
            sentence = t["sentenceSegments"]
            for s in sentence:
                transcription += s["phrase"] + " "
        except KeyError as e:
            raise print(e.args[0])
        print(transcription)
        print(summary)
        return {
            "message": f"Processed {audio_file.filename} successfully",
            "interaction_id": interaction_id,
            "transcription": transcription,
            "summary": summary,
            "dispatcher": dispatcher,
            "callType": call_type,
            "language": language,
            "notes": notes,
        }

    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Processing error: {e}")
    finally:
        # Optional cleanup even on error
        try:
            os.remove(file_path)
        except Exception:
            pass