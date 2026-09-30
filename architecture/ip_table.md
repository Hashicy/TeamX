# Machine Roles and IP/Service Table (Team X)

## Architecture Overview
This table maps the physical machines to their respective roles, IP addresses, and active services for the Phase 1 private network setup.

| Machine Role | Device | IP Address | Port | Active Service / Software |
| :--- | :--- | :--- | :--- | :--- |
| **DNS Server** | Mac 1 (Manan Bansal) | `10.7.17.51` | `53` | `dnsmasq` (Local DNS Resolution) |
| **Edge / Reverse Proxy** | Mac 2 (Harshita Joshi)| `10.7.8.105` | `443` | Nginx (Load Balancer & TLS Termination) |
| **Backend A** | Mac 3 (Soumya Tiwari)  | `10.7.7.136` | `3001` | Backend Application Server |
| **Backend B** | Mac 4 (Niharika Choudhary)| `10.7.12.123`  | `3002` | Backend Application Server |

## Domain Mapping
* **Primary Domain:** `app.teamX.test` -> Resolves to `10.7.8.105` (Mac 2)
* **API Domain:** `api.teamX.test` -> Resolves to `10.7.8.105` (Mac 2)
