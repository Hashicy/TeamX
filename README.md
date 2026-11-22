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

## Phase 2

Phase 2 hardens the same network: backup DNS, DNS TTL, backend firewall isolation, HA failover, DNS-based edge migration, and a live troubleshooting challenge.

---

## Project Structure

```text
CN_Project/
├── README.md
├── architecture/
│   ├── ip_table.md
│   ├── network-topology.md
│   └── request_flow.md
├── configuration/
│   ├── dnsmasq.conf
│   ├── nginx_config.conf
│   ├── TLS-notes.md
│   ├── backend_launch_instruction.txt
│   └── phase2/
│       ├── dnsmasq-primary.conf
│       ├── dnsmasq-backup.conf
│       ├── nginx-phase2.conf
│       ├── pf-isolation-mac3.conf
│       └── pf-isolation-mac4.conf
├── backends/
│   ├── backend-a/
│   │   └── server.py
│   └── backend-b/
│       └── server.py
└── Evidences/
    ├── 01-ping.png
    ├── 02-dng.png
    ├── 03-backend-a-and-b.png
    ├── 04-https.png.jpeg
    ├── 05-load-balancing.png
    ├── 06-dns-wireshark-overview.png
    ├── 06-dns-wireshark-query.png
    ├── 06-dns-wireshark-response.png
    ├── 07-wireshark-tcp-tls.png
    ├── 08-http-wireshark.png
    ├── 08-http-cache.png
    └── 09-failure-tests/
        ├── 01-wrong-dns-server.png
        ├── 02-wrong-dns-record.png
        ├── 03-one-backend-down.png
        ├── 04-both-backends-down.png
        └── 05-wrong-destination-port.png
```

---

## Running the Backends

Phase 1 uses two backend servers running on separate machines: Backend A and Backend B, both written in Python.
The exact IP addresses and ports are documented in `architecture/ip_table.md`.

### Backend A

Navigate to the Backend A directory:

```bash
cd backends/backend-a
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
cd backends/backend-b
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

The exact machine assignments, IP addresses, and service ports are documented in `architecture/ip_table.md`.

---

## Evidence

The `Evidences/` directory contains demonstrations of the Phase 1 requirements:

- Ping/connectivity testing
- DNS resolution
- Backend A and Backend B availability
- HTTPS
- Load balancing
- DNS packet capture
- TCP/TLS packet capture
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

- [X] Backend A starts successfully
- [X] Backend B starts successfully
- [X] Backend A is reachable using its configured IP and port
- [X] Backend B is reachable using its configured IP and port
- [X] Backend A responds successfully
- [X] Backend B responds successfully
- [X] The Nginx/client machine can reach Backend A
- [X] The Nginx/client machine can reach Backend B
- [X] IP addresses and ports match `architecture/ip_table.md`
