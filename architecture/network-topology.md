# Network Topology & Machine Roles (Phase 1)

## 1. System Overview
This diagram illustrates our local network topology, showing the four machine roles, their connections, and their cloud-equivalent components[cite: 4, 5, 6].

## 2. Machine Roles and IP/Service Table
| Machine | Primary Role | Services Running | Cloud Equivalent |
| :--- | :--- | :--- | :--- |
| **Mac 1** | Private DNS Server + Test Client | `dnsmasq`, `dig`/`nslookup`, `curl`/browser | Managed DNS service (e.g., Route 53) |
| **Mac 2** | Edge/Reverse Proxy + Load Balancer | `nginx`, TLS certificate, load balancer config | Cloud load balancer / CDN edge node |
| **Mac 3** | Backend Server A | Simple HTTP/REST application (port 3001) | Application server instance A |
| **Mac 4** | Backend Server B + Test Client | Simple HTTP/REST application (port 3002), `curl`/browser | Application server instance B |

*(Note: Data sourced from project guidelines[cite: 4])*

## 3. Network Topology Map
```text
[ Client Machine (Mac 1) ]
             |
             | (DNS Queries)
             v
    +-----------------------------------+
    |       Mac 1: DNS Server           |
    |       Service: dnsmasq            |
    |       Cloud Eq: Route 53          |
    +-----------------------------------+
             |
             | (HTTPS Traffic)
             v
    +-----------------------------------+
    |       Mac 2: Edge Proxy Node      |
    |       Service: nginx (TLS)        |
    |       Cloud Eq: Cloud Load Balancer|
    +-----------------------------------+
             |
             | (HTTP Proxy Traffic)
             |
    +--------+--------+
    |                 |
    v                 v
+-----------------+ +-----------------+
| Mac 3: Backend A| | Mac 4: Backend B|
| Port: 3001      | | Port: 3002      |
| Cloud Eq: App A | | Cloud Eq: App B |
+-----------------+ +-----------------+
