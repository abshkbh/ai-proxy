import os

from flask import Flask, Response, request, jsonify
from dotenv import load_dotenv
import requests


app = Flask(__name__)
with app.app_context():
    print("Initializing ai-proxy...")
    global LLM_API_KEY
    load_dotenv(".env")
    LLM_API_KEY = os.getenv("OPENAI_API_KEY")


# Simple route to check server status
@app.route("/", methods=["GET"])
def index():
    return "Hello, the ai-proxy is running"


# Proxy route to handle all subpaths under /proxy/api/
@app.route(
    "/proxy/openai/<path:subpath>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
def proxy(subpath):
    print(f"/proxy/openai/{subpath} request: {request}")
    method = request.method
    data = request.get_data()
    headers = dict(request.headers)

    # Remove headers that should not be forwarded
    headers.pop("Host", None)
    headers.pop("Authorization", None)  # Remove client's Authorization header

    # Add the OpenAI API key to the headers
    headers["Authorization"] = f"Bearer {API_KEY}"

    # Construct the target URL
    target_url = f"https://api.openai.com/{subpath}"

    # Forward the request to the target URL
    try:
        response = requests.request(
            method=method,
            url=target_url,
            headers=headers,
            data=data,
            params=request.args,
            timeout=30,  # Set a timeout for the request
        )

        # Return the response from the OpenAI API
        return Response(response.content, response.status_code, response.raw.headers)

    except requests.exceptions.RequestException as e:
        return Response(str(e), status=500)
