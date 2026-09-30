TeamX — Computer Networks Project
Team Members
- Harshita Joshi
- Manan Bansal
- Soumya Tiwari
- Niharika Choudhary
Phase 1
Phase 1 implements the network architecture with:
- Two backend servers
- DNS configuration
- Nginx reverse proxy/load balancing
- HTTPS/TLS configuration
- Network connectivity and verification
- Evidence of successful requests and failure scenarios
Project Structure
Phase1/
├── README.md
├── Architecture/
│   ├── ip-table.txt
│   ├── topology.md
│   ├── topology.mmd
│   ├── topology-diagram.png
│   ├── request-flow.md
│   └── request-flow-diagram.png
├── Configuration/
│   ├── dnsmasq.conf
│   ├── nginx.conf
│   ├── TLS-notes.txt
│   └── backend-launch-instructions.md
├── Backends/
│   ├── backend-a/
│   │   └── server.py
│   └── backend-b/
│       └── server.py
├── Evidence/
│   ├── README.md
│   ├── 01-ping.png
│   ├── 02-dns.png
│   ├── 03-backend-a-and-b.png
│   ├── 04-https.png
│   ├── 05-load-balancing.png
│   ├── 06-dns-wireshark.png
│   ├── 07-wireshark-tcp-tls-NOT-CAPTURED.png
│   ├── 08-http-cache.png
│   └── 09-failure-tests/
│       ├── 01-wrong-dns-server.png
│       ├── 02-wrong-dns-record.png
│       ├── 03-one-backend-down.png
│       ├── 04-both-backends-down.png
│       └── 05-wrong-destination-port.png
└── _submission_/
    └── Backend-Source-Code.zip
Architecture/
Contains the network topology, IP/service table, request-flow documentation, and diagrams.
Configuration/
Contains:
- dnsmasq.conf — DNS configuration
- nginx.conf — Nginx configuration
- TLS-notes.txt — TLS setup notes
- backend-launch-instructions.md — Instructions for starting the backend servers
Backends/
Contains the source code for both backend servers:
Backends/
├── backend-a/
│   └── server.py
└── backend-b/
    └── server.py
Evidence/
Contains screenshots and demonstrations of:
- Network connectivity
- DNS resolution
- Backend availability
- HTTPS
- Load balancing
- DNS packet capture
- HTTP caching
- Failure scenarios
Running the Backends
The project uses two Python backend servers.
Backend A
Navigate to the Backend A directory:
cd Phase1/Backends/backend-a
Start the server:
python3 server.py
Backend A should run on its assigned IP address and port as specified in:
Phase1/Architecture/ip-table.txt
Backend B
Navigate to the Backend B directory:
cd Phase1/Backends/backend-b
Start the server:
python3 server.py
Backend B should run on its assigned IP address and port as specified in:
Phase1/Architecture/ip-table.txt
Backend Verification
After starting both servers, verify that they are reachable using curl.
For Backend A:
curl -i http://<BACKEND-A-IP>:<BACKEND-A-PORT>/
For Backend B:
curl -i http://<BACKEND-B-IP>:<BACKEND-B-PORT>/
The exact IP addresses and ports are documented in:
Architecture/ip-table.txt
Network Architecture
The general Phase 1 architecture is:
                     Client
                       |
                       v
                Nginx Reverse Proxy
                       |
                +------+------+
                |             |
                v             v
          Backend A      Backend B
The exact machine assignments, IP addresses, and service ports are documented in:
Architecture/ip-table.txt
Evidence
The Evidence/ directory contains demonstrations of the Phase 1 requirements, including:
- Ping/connectivity testing
- DNS resolution
- Backend A and Backend B availability
- HTTPS
- Load balancing
- DNS packet capture
- HTTP caching
- Failure scenarios
Failure scenarios include:
- Wrong DNS server
- Wrong DNS record
- One backend unavailable
- Both backends unavailable
- Wrong destination port
Submission
The _submission_/ directory contains:
Backend-Source-Code.zip
which contains the backend source code submitted for the project.
