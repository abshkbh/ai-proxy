from flask import Flask, Response, request, jsonify
import requests

app = Flask(__name__)


# Simple route to check server status
@app.route("/", methods=["GET"])
def index():
    return "Hello, the server is running"


# Simple route to check server status
@app.route("/", methods=["GET"])
def index():
    return "Hello, the server is running"


# Proxy route to handle all subpaths under /proxy/api/
@app.route(
    "/proxy/api/<path:subpath>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
def proxy(subpath):
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


if __name__ == "__main__":
    app.run(debug=True)
