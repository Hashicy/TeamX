# TeamX: Computer Networks Project

## Team Members

- Harshita Joshi
- Manan Bansal
- Soumya Tiwari
- Niharika Choudhary

---

## Phase 1

Phase 1 implements the network architecture with:

- Two backend servers
- DNS configuration
- Nginx reverse proxy / load balancing
- HTTPS/TLS configuration
- Network connectivity and verification
- Evidence of successful requests and failure scenarios

---

## Project Structure

```text
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
```

---

## Running the Backends

Phase 1 uses two Python backend servers running on separate machines.
The exact IP addresses and ports are documented in `Architecture/ip-table.txt`.

### Backend A

Navigate to the Backend A directory:

```bash
cd Phase1/Backends/backend-a
```

Start the server:

```bash
python3 server.py
```

Verify Backend A:

```bash
curl -i http://<BACKEND-A-IP>:<BACKEND-A-PORT>/
```

### Backend B

Navigate to the Backend B directory:

```bash
cd Phase1/Backends/backend-b
```

Start the server:

```bash
python3 server.py
```

Verify Backend B:

```bash
curl -i http://<BACKEND-B-IP>:<BACKEND-B-PORT>/
```

---

## LAN Connectivity Verification

The backend servers must be reachable from the machine running the Nginx reverse proxy.

Find the IP address of a Mac:

```bash
ipconfig getifaddr en0
```

If `en0` is not the active network interface:

```bash
networksetup -listallhardwareports
```

Test Backend A:

```bash
curl -i http://<BACKEND-A-IP>:<BACKEND-A-PORT>/
```

Test Backend B:

```bash
curl -i http://<BACKEND-B-IP>:<BACKEND-B-PORT>/
```

Successful responses confirm that both backend servers are reachable over the LAN.

---

## Network Architecture

```text
Client
  |
  v
Nginx Reverse Proxy
  |
  +----------------+
  |                |
  v                v
Backend A       Backend B
```

The exact machine assignments, IP addresses, and service ports are documented in `Architecture/ip-table.txt`.

---

## Evidence

The `Evidence/` directory contains demonstrations of the Phase 1 requirements:

- Ping/connectivity testing
- DNS resolution
- Backend A and Backend B availability
- HTTPS
- Load balancing
- DNS packet capture
- HTTP caching
- Failure scenarios

---

## Failure Scenarios

The following failure scenarios are documented:

- Wrong DNS server
- Wrong DNS record
- One backend unavailable
- Both backends unavailable
- Wrong destination port

---

## Stopping the Backends

To stop a running backend server, press:

```text
Ctrl + C
```

---

## Phase 1 Backend Checklist

- [ ] Backend A starts successfully
- [ ] Backend B starts successfully
- [ ] Backend A is reachable using its configured IP and port
- [ ] Backend B is reachable using its configured IP and port
- [ ] Backend A responds successfully
- [ ] Backend B responds successfully
- [ ] The Nginx/client machine can reach Backend A
- [ ] The Nginx/client machine can reach Backend B
- [ ] IP addresses and ports match `Architecture/ip-table.txt`

---

## Submission

The `_submission_` directory contains:

- `Backend-Source-Code.zip`
