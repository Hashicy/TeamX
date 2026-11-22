# Request-Flow & Protocol Layer Analysis (Phase 1)

## 1. Request Lifecycle Overview
This document traces the complete journey of a single client request to `https://app.teamX.test/api/status`, explicitly mapping each step to its corresponding protocol and OSI/TCP-IP layer to demonstrate a full-stack network interaction.

## 2. Step-by-Step Protocol Breakdown

### Step 1: DNS Resolution (Application & Transport Layers)
*   **Protocol:** DNS over UDP (Port 53)
*   **Action:** The client machine (browser or `curl`) does not know where `app.teamX.test` is. It sends a DNS query to the team's private DNS server on **Mac 1 (10.7.17.51)**.
*   **Result:** Mac 1 responds with the IP address of the Edge Proxy, **Mac 2 (10.7.8.105)**.

### Step 2: Connection Establishment (Transport Layer)
*   **Protocol:** TCP (Port 443)
*   **Action:** Before sending any application data, the client initiates a reliable connection with Mac 2. 
*   **Result:** The classic TCP three-way handshake occurs: `SYN` → `SYN-ACK` → `ACK`.

### Step 3: Secure Tunneling (Session / Presentation Layers)
*   **Protocol:** TLS v1.3 (HTTPS)
*   **Action:** The client and Mac 2 negotiate encryption to secure the payload.
*   **Result:** The TLS handshake executes: `ClientHello` → `ServerHello` → `Certificate` presentation (from `mkcert` CA) → `ChangeCipherSpec` / Key Exchange. Traffic is now encrypted.

### Step 4: The Application Request (Application Layer)
*   **Protocol:** HTTP/1.1 or HTTP/2 over TLS
*   **Action:** The client sends the actual `GET /api/status` request over the encrypted tunnel. 
*   **Result:** Mac 2 (Nginx) receives and decrypts the payload (TLS Termination).

### Step 5: Load Balancing & Proxy Forwarding (Network & Application)
*   **Protocol:** HTTP (Unencrypted, Internal LAN)
*   **Action:** Mac 2 applies a round-robin algorithm and selects the next available backend server.
*   **Result:** Mac 2 acts as a proxy, forwarding the unencrypted HTTP request to either **Mac 3 (10.7.7.136:3001)** or **Mac 4 (10.7.12.123:3002)**.

### Step 6: Response & Caching (Application Layer)
*   **Protocol:** HTTP
*   **Action:** The selected backend generates a JSON response. It appends specific headers for traceability and performance.
*   **Result:** The response includes `X-Backend: A` (or B) and `Cache-Control` (e.g., `max-age=60`). Mac 2 encrypts this HTTP response and delivers it securely back to the client.

---

## 3. Detailed Sequence Diagram

```text
 Client (Browser/curl)           Mac 1 (DNS: 53)           Mac 2 (Edge: 443)       Mac 3/4 (Backends: 3001/3002)
       |                                |                          |                             |
       |==== 1. Application: DNS =======|                          |                             |
       | Query: app.teamX.test          |                          |                             |
       |------------------------------->|                          |                             |
       |<-------------------------------|                          |                             |
       | Response: 10.7.8.105           |                          |                             |
       |                                |                          |                             |
       |==== 2. Transport: TCP ====================================|                             |
       | SYN                            |                          |                             |
       |---------------------------------------------------------->|                             |
       |<----------------------------------------------------------|                             |
       | SYN-ACK                        |                          |                             |
       |---------------------------------------------------------->|                             |
       | ACK                            |                          |                             |
       |                                |                          |                             |
       |==== 3. Session: TLS ======================================|                             |
       | ClientHello                    |                          |                             |
       |---------------------------------------------------------->|                             |
       |<----------------------------------------------------------|                             |
       | ServerHello, Certificate, KeyExchange                     |                             |
       |                                |                          |                             |
       |==== 4. Application: HTTP (Encrypted) =====================|                             |
       | GET /api/status                |                          |                             |
       |---------------------------------------------------------->|                             |
       |                                |                  (TLS Termination)                     |
       |                                |                          |                             |
       |==== 5. Internal LAN: HTTP (Unencrypted) ================================================|
       |                                |                          | Round-Robin Proxy Forward   |
       |                                |                          |---------------------------->|
       |                                |                          |                             |
       |==== 6. Response & Caching ==============================================================|
       |                                |                          | JSON Payload                |
       |                                |                          | X-Backend: A/B              |
       |                                |                          | Cache-Control: max-age=60   |
       |                                |                          |<----------------------------|
       |<----------------------------------------------------------|                             |
       | Encrypted HTTPS Response       |                          |                             |
