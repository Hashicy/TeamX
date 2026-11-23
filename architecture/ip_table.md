# Machine Roles and IP/Service Table (Team X)

All four Macs are on the same private Wi-Fi network, `10.7.0.0/19`. Addresses changed between the Phase 1 build (30 Sep 2026) and the Phase 2 session (23 Nov 2026). Both are recorded below.

## Phase 2 (23 Nov 2026)

| Machine Role | Device | IP Address | Port | Active Service / Software |
| :--- | :--- | :--- | :--- | :--- |
| **Primary DNS** + test client | Mac 1 (Manan Bansal) | `10.7.31.159` | `53/udp` | `dnsmasq` (records with 30 s TTL) |
| **Edge / Reverse Proxy** | Mac 2 (Harshita Joshi) | `10.7.4.179` | `443/tcp` | nginx (TLS termination, load balancer, failover, HTTP/2) |
| **Backend A** + standby edge | Mac 3 (Soumya Tiwari) | `10.7.28.230` | `3001/tcp` (+ `443/tcp` during Ext E) | Python backend; standby nginx for the DNS cutover |
| **Backend B** + backup DNS + test client | Mac 4 (Niharika Choudhary) | `10.7.15.199` | `3002/tcp`, `53/udp` | Python backend; backup `dnsmasq` |

### Network Interface Details (Task A)

| Machine | IPv4 | Subnet mask (prefix) | Default gateway | Interface | MAC address (on the wire) | Hardware Wi-Fi ID |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Mac 1 | `10.7.31.159` | `255.255.224.0` (/19) | `10.7.0.1` | `en0` (Wi-Fi) | `36:5b:29:6a:40:c4` | `10:9f:41:c6:2a:22` |
| Mac 2 | `10.7.4.179` | `255.255.224.0` (/19) | `10.7.0.1` | `en0` (Wi-Fi) | `f6:fa:d2:fe:bc:09` | `10:9f:41:c4:60:18` |
| Mac 3 | `10.7.28.230` | `255.255.224.0` (/19) | `10.7.0.1` | `en0` (Wi-Fi) | `6e:f4:d9:b5:98:e0` | `10:9f:41:a7:ea:fb` |
| Mac 4 | `10.7.15.199` | TODO | TODO | TODO | `10:9f:41:c1:78:91` ¹ | TODO |

* Sources: each Mac's `Evidences/phase2/macN/p1-01-network-info.txt` (`networksetup -getinfo Wi-Fi` and `ifconfig en0`).
* ¹ Mac 4's MAC address was observed in Mac 1's ARP table during the session; the TODOs are filled from `Evidences/phase2/mac4/p1-01-network-info.txt` once it is committed.
* **MAC address (on the wire)** is what appears in Ethernet frames and Wireshark. On Macs 1–3 it is a macOS *private Wi-Fi address* (randomised per network), so it differs from the hardware **Wi-Fi ID**.

### Domain Mapping (Phase 2)
* **Primary Domain:** `app.teamX.test` -> `10.7.4.179` (Mac 2), TTL 30 s, served by both DNS servers
* **API Domain:** `api.teamX.test` -> `10.7.4.179` (Mac 2)
* During Extension E only, both records pointed to `10.7.28.230` (standby edge on Mac 3), then back.

## Phase 1 (30 Sep 2026)

| Machine Role | Device | IP Address | Port | Active Service / Software |
| :--- | :--- | :--- | :--- | :--- |
| **DNS Server** | Mac 1 (Manan Bansal) | `10.7.17.51` | `53` | `dnsmasq` (Local DNS Resolution) |
| **Edge / Reverse Proxy** | Mac 2 (Harshita Joshi)| `10.7.8.105` | `443` | Nginx (Load Balancer & TLS Termination) |
| **Backend A** | Mac 3 (Soumya Tiwari)  | `10.7.7.136` | `3001` | Backend Application Server |
| **Backend B** | Mac 4 (Niharika Choudhary)| `10.7.12.123`  | `3002` | Backend Application Server |

| Machine | IPv4 | Subnet mask (prefix) | Default gateway | Interface | MAC address (on the wire) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Mac 1 | `10.7.17.51` | `255.255.224.0` (/19) | `10.7.0.1` | `en0` (Wi-Fi) | `36:5b:29:6a:40:c4` |
| Mac 2 | `10.7.8.105` | | | | `82:45:df:b2:07:fb` |
| Mac 3 | `10.7.7.136` | | | | `6e:f4:d9:b5:98:e0` |
| Mac 4 | `10.7.12.123` | | | | |

* Mac 1 values are from `Evidences/01-ping.png`; the other MAC addresses are from the Ethernet headers in the Phase 1 Wireshark captures (`06-dns-wireshark-query.png`, `07-wireshark-tcp-tls.png`, `08-http-cache.png`). The rest was not recorded in Phase 1.

### Domain Mapping (Phase 1)
* **Primary Domain:** `app.teamX.test` -> `10.7.8.105` (Mac 2)
* **API Domain:** `api.teamX.test` -> `10.7.8.105` (Mac 2)
