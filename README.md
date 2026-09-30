# TeamX — Computer Networks Project

## Team Members

- Harshita Joshi
- Manan Bansal
- Soumya Tiwari
- Niharika Choudhary

---

# Phase 1 — Backend Setup

Phase 1 uses two backend servers running on separate machines.

| Backend | Machine | Port |
|---|---|---:|
| Backend A | Mac 3 | 3001 |
| Backend B | Mac 4 | 3002 |

Both backends must listen on `0.0.0.0` so that they can be accessed by other machines on the LAN.

---

# Repository Structure

```text
TeamX/
└── backends/
    ├── backend-a/
    │   ├── package.json
    │   ├── package-lock.json
    │   └── server.js
    │
    └── backend-b/
        ├── .gitignore
        ├── package.json
        ├── package-lock.json
        └── server.js

Running Backend A — Mac 3
Navigate to the Backend A directory:
cd ~/TeamX/backends/backend-a

Install dependencies:
npm install

Start the server:
node server.js

Backend A runs on:
0.0.0.0:3001

Test Backend A
Test the root endpoint:
curl -i http://localhost:3001/

Test the status endpoint:
curl -i http://localhost:3001/api/status

The response should contain:
X-Backend: A

Running Backend B — Mac 4
Navigate to the Backend B directory:
cd ~/TeamX/backends/backend-b

Install dependencies:
npm install

Start the server:
node server.js

Backend B runs on:
0.0.0.0:3002

Test Backend B
Test the root endpoint:
curl -i http://localhost:3002/

Test the status endpoint:
curl -i http://localhost:3002/api/status

The response should contain:
X-Backend: B

LAN Connectivity
The backends must be accessible from Mac 2.
Find Backend A IP
On Mac 3:
ipconfig getifaddr en0

Find Backend B IP
On Mac 4:
ipconfig getifaddr en0

If en0 is not the active Wi-Fi interface, use:
networksetup -listallhardwareports

Test Backend A from Mac 2
Replace <MAC3-IP> with the IP address of Mac 3:
curl -i http://<MAC3-IP>:3001/api/status

Expected header:
X-Backend: A

Test Backend B from Mac 2
Replace <MAC4-IP> with the IP address of Mac 4:
curl -i http://<MAC4-IP>:3002/api/status

Expected header:
X-Backend: B

Successful responses confirm that Mac 2 can reach both backends over the LAN.
Backend Requirements
Backend A
- Machine: Mac 3
- Port: 3001
- Listen address: 0.0.0.0
- Endpoint: GET /
- Endpoint: GET /api/status
- Response header: X-Backend: A
Backend B
- Machine: Mac 4
- Port: 3002
- Listen address: 0.0.0.0
- Endpoint: GET /
- Endpoint: GET /api/status
- Response header: X-Backend: B
Phase 1 Architecture
                       Mac 2
                  Reverse Proxy
                    /       \
                   /         \
                  v           v
           Mac 3 :3001   Mac 4 :3002
           Backend A     Backend B
           X-Backend:A   X-Backend:B

Stopping the Backends
To stop a running backend:
Ctrl + C
