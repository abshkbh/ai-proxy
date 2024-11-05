How to setup with a React SPA?
- Forward ports to your client machine "ssh -L 5173:127.0.0.1:5173 -L 4000:127.0.0.1:4000 <vm-ip>"
- Run this proxy with flask --app src/main.py run --host 127.0.0.1 --port 4000
- Run SPA at 127.0.0.1:5173

