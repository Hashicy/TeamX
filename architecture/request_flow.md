# Request-Flow & Protocol Layer Analysis

Sections 1–3 describe the Phase 1 flow with Phase 1 addresses. Section 4 describes the current Phase 2 flow.

## 1. Request Lifecycle Overview (Phase 1)
This document traces the complete journey of a single client request to `https://app.teamX.test/api/status`, explicitly mapping each step to its corresponding protocol and OSI/TCP-IP layer to demonstrate a full-stack network interaction.

## 2. Step-by-Step Protocol Breakdown (Phase 1)

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

## 3. Detailed Sequence Diagram (Phase 1)

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
```

---

## 4. Phase 2 Request Flow (23 Nov 2026)

The steps are the same as in Phase 1. The table lists what each one does in Phase 2.

| # | Layer (OSI) | Protocol / port | Phase 2 behaviour |
| :--- | :--- | :--- | :--- |
| 1 | Application (7), over UDP (4) | DNS, 53/udp | The client asks Mac 1 (`10.7.31.159`), or Mac 4 (`10.7.15.199`) if Mac 1 does not answer. Answer: `10.7.4.179`, TTL 30 s. A cached answer skips this step |
| 2 | Transport (4) | TCP, 443 | `SYN` → `SYN-ACK` → `ACK` with Mac 2 |
| 3 | Session / Presentation (5/6) | TLS 1.3 | `ClientHello` (SNI, ALPN) → `ServerHello`. The certificate that follows is encrypted. The client verifies it with the team's mkcert root CA |
| 4 | Application (7) | HTTP/2 over TLS | `GET /api/status`, optionally with `If-None-Match`. HTTP/2 is chosen through ALPN |
| 5 | Application (7) | nginx on Mac 2 | TLS ends here. nginx picks a backend round-robin and skips one marked down |
| 6 | Application (7), over TCP (4) | HTTP, 3001 / 3002 | Plain HTTP to Mac 3 (`10.7.28.230:3001`) or Mac 4 (`10.7.15.199:3002`). With Ext C on, pf accepts only Mac 2. If the attempt fails, nginx retries on the other backend |
| 7 | Application (7) | HTTP, then HTTP/2 over TLS | `200` with JSON, or `304` with no body if the ETag matches. Headers: `X-Backend`, `ETag`, `Cache-Control: max-age=60`; nginx adds `X-Edge` |
| – | Network (3) / Link (2) | IPv4 / Wi-Fi | Every step above is carried in IP packets within `10.7.0.0/19`, inside Wi-Fi frames |

### 4.1 Sequence diagram

```text
 Client            DNS (Mac 1, else Mac 4)      Mac 2 (Edge :443)         Mac 3 / Mac 4 (:3001 / :3002)
   |                          |                         |                              |
   | A app.teamX.test ? (UDP) |                         |                              |
   |------------------------->|                         |                              |
   |   10.7.4.179, TTL 30 s   |                         |                              |
   |<-------------------------|                         |                              |
   | SYN / SYN-ACK / ACK                                |                              |
   |<-------------------------------------------------->|                              |
   | ClientHello (SNI, ALPN)                            |                              |
   |--------------------------------------------------->|                              |
   | ServerHello, then {Certificate, Finished}          |                              |
   |<---------------------------------------------------|                              |
   | {Finished}                                         |                              |
   |--------------------------------------------------->|                              |
   | {GET /api/status} HTTP/2                           |                              |
   |--------------------------------------------------->|                              |
   |                                  (TLS termination) | GET /api/status (plain HTTP) |
   |                                                    |----------------------------->|
   |                                                    | 200 or 304, X-Backend, ETag  |
   |                                                    |<-----------------------------|
   | {200 or 304 + X-Edge: mac2}                        |                              |
   |<---------------------------------------------------|                              |

   { } = encrypted by TLS
```

### 4.2 When something fails or moves

| Situation | What changes in the flow |
| :--- | :--- |
| Primary DNS stopped (Ext A) | Step 1 is answered by Mac 4; the rest is unchanged |
| DNS record changed (Ext B) | A client with a cached answer keeps using the old address until it expires or is flushed |
| Direct client request to 3001 / 3002 (Ext C) | pf refuses it; the path through the edge still works |
| One backend stopped (Ext D) | Step 6 is retried on the other backend; the client still gets `200` |
| Both backends stopped | Steps 1–5 work; nginx returns `502 Bad Gateway` |
| DNS cutover to the standby edge (Ext E) | Step 1 returns `10.7.28.230`; Mac 3 performs steps 2–7 with `X-Edge: mac3` |
