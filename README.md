## What is this?

React SPA apps can't directly call LLM APIs with API Keys due to CORS and the risk of exposing keys.

Instead your SPA app can call this proxy and the proxy in turn can add your key etc. and make the call
to the LLM provider.

Currently, it supports calling OpenAI and [Braintrust Proxy](https://github.com/braintrustdata/braintrust-proxy) which in turn can call multiple models and has caching support.

## How to setup and run this proxy?

1. Set BRAINTRUST_PROXY_API_KEY and/or OPENAI_API_KEY in a .env file
2. `python3 -m venv venv`
3. `source venv/bin/activate`
4. `pip install -r requirements.txt`
5. `flask --app src/main.py run --host 127.0.0.1 --port 4000`

## How to setup with a React SPA?

1. If you have a dev VM with public IP: `devvm-ip`
2. Run this proxy: `flask --app src/main.py run --host 127.0.0.1 --port 4000`
3. Run your SPA (pnpm, npm) at: `127.0.0.1:5173`
4. Forward ports to your client machine: `ssh -L 5173:127.0.0.1:5173 -L 4000:127.0.0.1:4000 user@devvm-ip`
5. This ensures that port 5173 and 4000 on your client redirect to the SPA and this proxy. The SPA rendered on your client can call the proxy successfully.
6. For OpenAI, from your SPA call: `http://127.0.0.1:4000/proxy/openai/<api-paths>`
7. For Braintrust Proxy, from your SPA call: `http://127.0.0.1:4000/proxy/braintrust/<api-paths>`