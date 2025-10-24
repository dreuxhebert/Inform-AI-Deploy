import os
import requests
import json
import re

from fastapi import HTTPException

api_token = os.getenv("ELEVATEAI_API_TOKEN")
api_url = os.getenv("ELEVATEAI_BASE_URL")

class Analysis:
    def __init__(self, **kwargs):
        self.headers = {
            "X-API-Token": api_token,
            "Accept": "gzip, deflate",
            "Content-Type": "application/json"
        }

    def check_address(self, interaction_id):
        payload = json.dumps({
            "question": "Did the dispatcher ask for or confirm the location of the incident — such as the street name, street number, nearby location, or landmark — even if the caller provided it before being asked? The answer must start with Yes if the dispatcher asked or confirmed the location, Refused if the caller refused to answer, or No if the dispatcher did not ask. If the answer is Yes or Refused, include short proof lines from the conversation — nothing else."
        })
        try:
            response = requests.post(
                f"{api_url}/interactions/{interaction_id}/gen-ai/ask",
                headers=self.headers,
                data=payload,
                verify=False
            )
            response.raise_for_status()

            answer_text = response.json().get("answer", "")

            # Extract the main answer (Yes, No, Refused)
            ans_match = re.match(r'^(Yes|No|Refused)', answer_text, re.IGNORECASE)
            ans = ans_match.group(1) if ans_match else "Unknown"

            # Extract proof from quotes (single or double)
            proof_matches = re.findall(r'["\']([^"\']+)["\']', answer_text)
            proof = " ".join(proof_matches) if proof_matches else None

            return {
                "answer_type": ans,
                "proof": proof
            }
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Processing error: {e}")

    def check_callback(self, interaction_id):
        payload = json.dumps({
            "question": "Did the dispatcher ask for or confirm a way to contact the caller if their is a need to call back. The 'answer' must start with Yes if the dispatcher asked for the location,Refused if the other person refused to answer the question, No if the dispatcher did not ask the question. If the answer is Yes or Refused, include 2–3 short proof lines from the conversation nothing else."
        })
        try:
            response = requests.post(
                f"{api_url}/interactions/{interaction_id}/gen-ai/ask",
                headers=self.headers,
                data=payload,
                verify=False
            )
            response.raise_for_status()
            answer = response.json().get("answer", "")
            ans_match = re.match(r'^(Yes|No|Refused)', answer, re.IGNORECASE)
            ans = ans_match.group(1) if ans_match else "Unknown"

            # Extracts the proof from the transcriptions
            proof_matches = re.findall(r"'([^']+)'", answer)
            proof = " ".join(proof_matches) if proof_matches else None

            return {
                "answer_type": ans,
                "proof": proof
            }
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Processing error: {e}")

    def call_type(self, interaction_id):
        payload = json.dumps({
            "question": "Analyze the following 911 call transcript and determine the type or types of the call. Choose from Fire, Medical (EMD), Police, or Other. The answer must list all applicable types. Include short proof lines from the conversation that justify your classification — nothing else."
        })
        try:
            response = requests.post(
                f"{api_url}/interactions/{interaction_id}/gen-ai/ask",
                headers=self.headers,
                data=payload,
                verify=False
            )
            response.raise_for_status()

            answer_text = response.json().get("answer", "")

            # Extract the main call type (Police, Medical (EMD), Other)
            type_match = re.match(r'^(Police|Medical \(EMD\)|Other)', answer_text, re.IGNORECASE)
            call_type = type_match.group(1) if type_match else "Unknown"

            # Extract proof from quotes (single or double)
            proof_matches = re.findall(r'["\']([^"\']+)["\']', answer_text)
            proof = proof_matches if proof_matches else []

            return {
                "answer_type": call_type,
                "proof": proof
            }
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Processing error: {e}")