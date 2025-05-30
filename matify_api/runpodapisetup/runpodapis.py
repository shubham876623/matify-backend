from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser
from dotenv import load_dotenv
import requests
from django.core.files.storage import default_storage
import replicate
import boto3
import uuid
import base64
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
load_dotenv()

# --- Runpod API Integration ---
BASE_RUNPOD_URL = "https://api.runpod.ai/v2"



def call_runpod_sync(endpoint_id, payload):
    url = f"{BASE_RUNPOD_URL}/{endpoint_id}/runsync"
    try:
        runpod_api_key = os.getenv("RUN_POD_API_KEY")
       
        headers = {"Authorization": f"{runpod_api_key}"}
        response = requests.post(url, json=payload,headers= headers)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "COMPLETED" and "output" in data:
            return {"status": "COMPLETED", "output": data["output"]}
        else:
            return poll_runpod_status(endpoint_id, data.get("id"))
    except Exception as e:
        return {"status": "FAILED", "error": str(e)}
    

def poll_runpod_status(endpoint_id, job_id, max_wait=180):
    url = f"{BASE_RUNPOD_URL}/{endpoint_id}/status/{job_id}"
    import time
    start_time = time.time()

    while time.time() - start_time < max_wait:
        resp = requests.get(url)
        data = resp.json()
        status = data.get("status")

        if status == "COMPLETED" and "output" in data:
            return {"status": "COMPLETED", "output": data["output"]}
        elif status == "FAILED":
            return {"status": "FAILED", "error": data}
        time.sleep(3)

    return {"status": "TIMEOUT", "message": "Job did not complete in time."}
