import os
from flask_cors import CORS
from flask import Flask, Response, request, jsonify
from dotenv import load_dotenv
import requests

MODEL_PROVIDER_OPENAI = "openai"
MODEL_PROVIDER_BRAINTRUST_PROXY = "braintrust"

app = Flask(__name__)
with app.app_context():
    print("Initializing ai-proxy...")
    global LLM_API_KEY
    load_dotenv(".env")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    BRAINTRUST_PROXY_API_KEY = os.getenv("BRAINTRUST_PROXY_API_KEY")
    CORS(
        app,
        resources={
            r"/proxy/*": {"origins": "*"},
            r"/": {"origins": "*"},
            r"/chv-proxy/*": {"origins": "*"},
        },
    )


# Simple route to check server status
@app.route("/", methods=["GET"])
def index():
    return "Hello, the ai-proxy is running"


# Proxy route to handle all subpaths under /proxy/api/
@app.route(
    "/proxy/<string:provider>/<path:subpath>",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
)
def proxy(provider, subpath):
    if provider not in [MODEL_PROVIDER_OPENAI, MODEL_PROVIDER_BRAINTRUST_PROXY]:
        return jsonify({"error": f"Invalid API provider: {provider}"}), 400
    method = request.method
    data = request.get_data()

    # Filter headers to be forwarded, included one used by BT proxy for caching.
    allowed_headers = {"Content-Type", "X-Bt-Use-Cache"}
    headers = {k: v for k, v in request.headers if k in allowed_headers}

    if provider == MODEL_PROVIDER_OPENAI:
        headers["Authorization"] = f"Bearer {OPENAI_API_KEY}"
        target_url = f"https://api.openai.com/v1/{subpath}"
    else:
        headers["Authorization"] = f"Bearer {BRAINTRUST_PROXY_API_KEY}"
        target_url = f"https://api.braintrust.dev/v1/proxy/{subpath}"

    # Forward the request to the target URL.
    try:
        print(f"Forwarding request to: {target_url} with data: {data}")
        response = requests.request(
            method=method,
            url=target_url,
            headers=headers,
            data=data,
            params=request.args,
            timeout=30,
        )
        response.raise_for_status()

        # Print headers used by BT proxy to indicate a cache hit. Won't be useful for other providers.
        print(
            f'X-Bt-Cached: {response.headers.get("X-Bt-Cached", "not set")} X-Cached: {response.headers.get("X-Cached", "not set")}'
        )
        content_type = response.headers.get("Content-Type", "application/octet-stream")
        return response.content, response.status_code, [("Content-Type", content_type)]
    except requests.exceptions.HTTPError as e:
        print(f"HttpError: {e}")
        return jsonify({"error": str(e)}), e.response.status_code
    except Exception as e:
        print(f"General exception: {e}")
        return jsonify({"error": str(e)}), 500


# Proxy route to handle all subpaths under /proxy/api/
@app.route(
    "/chv-proxy/<path:subpath>",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
)
def chv_proxy(subpath):
    method = request.method
    data = request.get_data()

    # Filter headers to be forwarded
    allowed_headers = {"Content-Type"}
    headers = {k: v for k, v in request.headers if k in allowed_headers}

    # Forward the request to the target URL.
    target_url = f"http://127.0.0.1:7000/{subpath}"
    try:
        print(f"Forwarding request to: {target_url} with data: {data}")
        response = requests.request(
            method=method,
            url=target_url,
            headers=headers,
            data=data,
            params=request.args,
            timeout=30,
        )
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "application/octet-stream")
        return response.content, response.status_code, [("Content-Type", content_type)]
    except requests.exceptions.HTTPError as e:
        print(f"HttpError: {e}")
        return jsonify({"error": str(e)}), e.response.status_code
    except Exception as e:
        print(f"General exception: {e}")
        return jsonify({"error": str(e)}), 500
