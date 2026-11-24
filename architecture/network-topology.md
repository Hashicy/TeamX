# Network Topology & Machine Roles

Section 4 shows the current Phase 2 design. Sections 1–3 are the Phase 1 design it extends. Addresses for both phases are in [`ip_table.md`](ip_table.md).

## 1. System Overview (Phase 1)
This diagram illustrates our local network topology, showing the four machine roles, their connections, and their cloud-equivalent components.

## 2. Machine Roles and IP/Service Table (Phase 1)
| Machine | Primary Role | Services Running | Cloud Equivalent |
| :--- | :--- | :--- | :--- |
| **Mac 1** | Private DNS Server + Test Client | `dnsmasq`, `dig`/`nslookup`, `curl`/browser | Managed DNS service (e.g., Route 53) |
| **Mac 2** | Edge/Reverse Proxy + Load Balancer | `nginx`, TLS certificate, load balancer config | Cloud load balancer / CDN edge node |
| **Mac 3** | Backend Server A | Simple HTTP/REST application (port 3001) | Application server instance A |
| **Mac 4** | Backend Server B + Test Client | Simple HTTP/REST application (port 3002), `curl`/browser | Application server instance B |

*(Note: Data sourced from project guidelines)*

## 3. Network Topology Map (Phase 1)
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
```

## 4. Phase 2 Topology (23 Nov 2026)

Phase 2 keeps the same four Macs and adds a backup DNS server, backend firewall rules, backend failover and a standby edge.

### 4.1 Machine roles

| Machine | Phase 2 IP | Role | Services and ports | Cloud Equivalent |
| :--- | :--- | :--- | :--- | :--- |
| **Mac 1** | `10.7.31.159` | Primary DNS + Test Client | `dnsmasq` 53/udp | Managed DNS service (e.g., Route 53) |
| **Mac 2** | `10.7.4.179` | Edge / Load Balancer | `nginx` 443/tcp (TLS, HTTP/2, failover) | Cloud load balancer |
| **Mac 3** | `10.7.28.230` | Backend A + Standby Edge | Python 3001/tcp; `nginx` 443/tcp during Ext E only | Application instance A + standby load balancer |
| **Mac 4** | `10.7.15.199` | Backend B + Backup DNS + Test Client | Python 3002/tcp; `dnsmasq` 53/udp | Application instance B + secondary DNS |

### 4.2 Topology map

```text
                  Clients (Mac 1, Mac 4)
                   |                  |
     1. DNS (UDP 53)                  2. HTTPS (TCP 443)
      primary, then backup            |
         |            |               |
         v            v               v
  +------------+ +------------+  +--------------------+     +--------------------+
  | Mac 1      | | Mac 4      |  | Mac 2              |     | Mac 3 (Ext E only) |
  | Primary DNS| | Backup DNS |  | Edge nginx         |     | Standby edge nginx |
  | TTL 30 s   | | TTL 30 s   |  | X-Edge: mac2       |     | X-Edge: mac3       |
  +------------+ +------------+  +--------------------+     +--------------------+
                                     |            |           (same config and certs;
                          3. HTTP    |            |            used after DNS cutover)
                                     v            v
                           [pf, Ext C: edge only on each port]
                          +----------------+ +----------------+
                          | Mac 3          | | Mac 4          |
                          | Backend A      | | Backend B      |
                          | 3001/tcp       | | 3002/tcp       |
                          +----------------+ +----------------+
```

Macs 3 and 4 appear more than once because each runs more than one service. The pf rules admit only Mac 2, so Extension C is rolled back before the standby edge is used in Extension E.

### 4.3 What Phase 2 adds

| Ext | Addition | Effect |
| :--- | :--- | :--- |
| A | Backup `dnsmasq` on Mac 4 with the same records | Names still resolve when Mac 1's DNS stops |
| B | `local-ttl=30` on both DNS servers | Clients may cache an answer, so a record change reaches them gradually |
| C | pf rules on Mac 3 and Mac 4 | Only the edge can open connections to ports 3001 / 3002 |
| D | `max_fails=1 fail_timeout=10s` and `proxy_next_upstream` | One stopped backend is not visible to clients |
| E | Standby nginx on Mac 3 | Traffic can be moved by changing the DNS records |

**Remaining single point of failure:** the edge nginx on Mac 2. The standby is started and switched to by hand, so removing it would need automatic failover (for example a floating virtual IP or health-checked DNS).
