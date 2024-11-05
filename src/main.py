import os
from flask_cors import CORS
from flask import Flask, Response, request, jsonify
from dotenv import load_dotenv
import requests


app = Flask(__name__)
with app.app_context():
    print("Initializing ai-proxy...")
    global LLM_API_KEY
    load_dotenv(".env")
    LLM_API_KEY = os.getenv("OPENAI_API_KEY")
    CORS(app, resources={r"/proxy/openai/*": {"origins": "*"}, r"/": {"origins": "*"}})


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
    headers = {
        k: v
        for k, v in request.headers
        if k
        not in [
            "Host",
            "Authorization",
            "Connection",
            "Content-Length",
            "X-Stainless-Os",
            "X-Stainless-Runtime-Version",
            "X-Stainless-Package-Version",
            "X-Stainless-Runtime",
            "X-Stainless-Arch",
            "X-Stainless-Retry-Count",
            "X-Stainless-Lang",
            "Origin",
            "Referer",
            "Accept-Encoding",
        ]
    }
    # Add the Authorization header for OpenAI API
    headers["Authorization"] = f"Bearer {LLM_API_KEY}"

    # Construct the target URL
    target_url = f"https://api.openai.com/v1/{subpath}"

    # Forward the request to the target URL
    try:
        print(f"Forwarding request to: {target_url}")
        response = requests.request(
            method=method,
            url=target_url,
            headers=headers,
            data=data,
            params=request.args,
            timeout=30,  # Set a timeout for the request
        )
        print(f"Response: {response}")

        # Return the response from the OpenAI API
        return Response(response.content, response.status_code, response.raw.headers)

    except Exception as e:
        print(f"Error: {e}")
        return Response(str(e), status=500)
