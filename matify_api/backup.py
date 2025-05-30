from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os
from dotenv import load_dotenv
import requests

load_dotenv()
token = os.getenv("REPLICATE_TOKEN")

class ReplicateTrainingView(APIView):
    def get(self, request):
        headers = {
            "Authorization": f"Token {token}"
        }
        try:
            r = requests.get("https://api.replicate.com/v1/trainings", headers=headers)
            return Response(r.json(), status=r.status_code)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
        
class ReplicatePredictionView(APIView):
    def post(self, request):
        replicate_token = os.getenv("REPLICATE_TOKEN")
        if not replicate_token:
            return Response({"error": "Replicate token not set"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Extract data
        version = request.data.get("version")
        input_data = request.data.get("input")
        print(version,input_data)
        if not version or not input_data:
            return Response(
                {"error": "Both 'version' and 'input' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        headers = {
            "Authorization": f"Token {replicate_token}",
            "Content-Type": "application/json",
            "Prefer": "wait"
        }

        payload = {
            "version": version,
            "input":input_data
        }

        # try:
        r = requests.post("https://api.replicate.com/v1/predictions", json=payload, headers=headers)
        r.raise_for_status()
        print(r.json())
        headers1 = {
        "Authorization": f"Token {token}"
    }
        get_the_deliviry_url = requests.get(r.json('get'), headers=headers1)
    
        return Response(get_the_deliviry_url, status=r.status_code)
        # except requests.exceptions.RequestException as e:
        #     return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        
class ReplicateModelTrainingView(APIView):
    def post(self, request):
        try:
            replicate_token = os.getenv("REPLICATE_API_TOKEN")
            model_owner = request.data.get("model_owner")     # e.g. 'ostris'
            model_name = request.data.get("model_name")       # e.g. 'flux-dev-lora-trainer'
            version_id = request.data.get("version")          # full version hash
            input_images_url = request.data.get("input_images")  # Must be an external .zip URL
            hf_token = request.data.get("hf_token", None)
            hf_repo_id = request.data.get("hf_repo_id", None)

            if not (model_owner and model_name and version_id and input_images_url):
                return Response({"error": "Missing required fields"}, status=400)

            headers = {
                "Authorization": f"Token {replicate_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "destination": f"{model_owner}/{model_name}",
                "input": {
                    "input_images": input_images_url,
                    "steps": 1000,
                }
            }

            # Optional fields
            if hf_token:
                payload["input"]["hf_token"] = hf_token
            if hf_repo_id:
                payload["input"]["hf_repo_id"] = hf_repo_id

            # Send POST request to Replicate training endpoint
            url = f"https://api.replicate.com/v1/models/{model_owner}/{model_name}/versions/{version_id}/trainings"
            res = requests.post(url, headers=headers, json=payload)

            return Response(res.json(), status=res.status_code)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
