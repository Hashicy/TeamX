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

| Extension | What we added | Where |
| :--- | :--- | :--- |
| A: Backup DNS | Second dnsmasq on Mac 4 with the same records; clients list Mac 1 then Mac 4 | `configuration/phase2/dnsmasq-backup.conf` |
| B: DNS TTL | `local-ttl=30` on both DNS servers (Phase 1 was 0) | `dnsmasq-primary.conf`, `dnsmasq-backup.conf` |
| C: Service isolation | pf rules on Mac 3 / Mac 4: only the edge may reach ports 3001 / 3002 | `pf-isolation-mac3.conf`, `pf-isolation-mac4.conf` |
| D: HA failover | nginx passive health checks (`max_fails=1 fail_timeout=10s`) and retry on the other backend (`proxy_next_upstream`) | `nginx-phase2.conf` |
| E: Edge migration | Standby nginx on Mac 3 (`X-Edge: mac3`); DNS cutover to it and back | `nginx-phase2.conf` |
| F: Troubleshooting | Layer-by-layer diagnosis: DNS, IP, TCP, TLS, application | [Step 10](#step-10-fault-diagnosis-ext-f) |

* Full walkthrough with what we observed: [`configuration/phase2/README.md`](configuration/phase2/README.md)
* Evidence from the 23 Nov 2026 session: `Evidences/phase2/mac1` … `mac4`
* Final report and presentation: `docs/TeamX_Phase2_Final_Report.pdf`, `docs/index.html`
* Demonstration commands: [Demonstration Commands](#demonstration-commands)

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
│       ├── pf-isolation-mac4.conf
│       └── README.md              (Phase 2 setup and demo guide)
├── backends/
│   ├── backend-a/
│   │   └── server.py
│   └── backend-b/
│       └── server.py
├── docs/
│   ├── TeamX_Phase2_Final_Report.pdf
│   └── index.html                 (presentation)
└── Evidences/
    ├── phase2/
    │   ├── mac1/                  (client + primary DNS: p1-*, extA..extE, full-request.pcap)
    │   ├── mac2/                  (edge: nginx -t, cert, HTTP/2, failover logs)
    │   ├── mac3/                  (Backend A, pf isolation, standby edge)
    │   └── mac4/                  (Backend B, backup DNS, pf isolation, fresh client)
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

---

## Demonstration Commands

Commands for each step of the final demonstration sequence and each Phase 2 extension. All commands run from the repository root (`~/TeamX`). Results recorded in the 23 Nov 2026 session are in [`configuration/phase2/README.md`](configuration/phase2/README.md).

### Step 0: Setup

#### 0.1 Session variables and helper functions (every Mac)

IP addresses are assigned by DHCP and can change between sessions; each Mac's current address is shown by `ipconfig getifaddr en0`. The block below sets the addresses and defines the helper functions used in later steps:

| Function | Purpose |
| :--- | :--- |
| `fixips <file>` | Prints a `configuration/phase2/` file with the Phase 1 addresses replaced by the current ones |
| `setrecords <ip>` | Points both project DNS records at `<ip>` and restarts dnsmasq |
| `flushdns` | Clears the macOS DNS cache |
| `lb` | Sends six requests and prints the status and `x-backend` of each |
| `edge` | Prints the status and `x-edge` of one request |
| `cached` | Prints the address the client's resolver currently uses for `app.teamX.test` |

```bash
export M1=10.7.31.159 M2=10.7.4.179 M3=10.7.28.230 M4=10.7.15.199
export CA=~/cn-project/tls/rootCA.pem URL=https://app.teamX.test

fixips() { sed -e "s/10\.7\.17\.51/$M1/g" -e "s/10\.7\.8\.105/$M2/g" -e "s/10\.7\.7\.136/$M3/g" -e "s/10\.7\.12\.123/$M4/g" "$1"; }

setrecords() {
  sudo sed -i '' -E "s#^(address=/(app|api)\.teamX\.test/).*#\1$1#" /opt/homebrew/etc/dnsmasq.conf
  sudo pkill -x dnsmasq; sleep 1; sudo /opt/homebrew/sbin/dnsmasq -C /opt/homebrew/etc/dnsmasq.conf
  grep '^address=' /opt/homebrew/etc/dnsmasq.conf
}

flushdns() { sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder; }
lb()   { for i in 1 2 3 4 5 6; do curl --cacert "$CA" -s -o /dev/null -D - $URL/api/status | grep -iE '^(HTTP|x-backend)' | tr -d '\r' | paste -sd' ' -; done; }
edge() { curl --cacert "$CA" -sI $URL/api/status | grep -iE '^(HTTP|x-edge)' | tr -d '\r' | paste -sd' ' -; }
cached() { dscacheutil -q host -a name app.teamX.test | awk '/ip_address/{print $2}'; }

caffeinate -d &
```

#### 0.2 Backends (Mac 3 and Mac 4)

Each backend runs in its own Terminal window and listens on all interfaces. Mac 3 runs Backend A (port 3001), Mac 4 runs Backend B (port 3002):

```bash
python3 backends/backend-a/server.py
```

```bash
python3 backends/backend-b/server.py
```

#### 0.3 DNS servers (Mac 1 primary, Mac 4 backup)

Mac 1:

```bash
sudo cp /opt/homebrew/etc/dnsmasq.conf /opt/homebrew/etc/dnsmasq.conf.bak 2>/dev/null
fixips configuration/phase2/dnsmasq-primary.conf | sudo tee /opt/homebrew/etc/dnsmasq.conf >/dev/null
sudo pkill -x dnsmasq; sudo /opt/homebrew/sbin/dnsmasq -C /opt/homebrew/etc/dnsmasq.conf
```

Mac 4:

```bash
sudo cp /opt/homebrew/etc/dnsmasq.conf /opt/homebrew/etc/dnsmasq.conf.bak 2>/dev/null
fixips configuration/phase2/dnsmasq-backup.conf | sudo tee /opt/homebrew/etc/dnsmasq.conf >/dev/null
sudo pkill -x dnsmasq; sudo /opt/homebrew/sbin/dnsmasq -C /opt/homebrew/etc/dnsmasq.conf
```

Both servers return Mac 2's address:

```bash
dig @$M1 app.teamX.test +short
dig @$M4 app.teamX.test +short
```

#### 0.4 Edge (Mac 2)

```bash
sudo cp /opt/homebrew/etc/nginx/nginx.conf /opt/homebrew/etc/nginx/nginx.conf.bak
fixips configuration/phase2/nginx-phase2.conf | sudo tee /opt/homebrew/etc/nginx/nginx.conf >/dev/null
sudo nginx -t && (sudo nginx -s reload 2>/dev/null || sudo nginx)
curl -s -i http://$M3:3001/api/status | grep -i x-backend
curl -s -i http://$M4:3002/api/status | grep -i x-backend
```

#### 0.5 Clients (Mac 1 and Mac 4)

The team CA certificate `rootCA.pem` from Mac 2 (folder shown by `mkcert -CAROOT`) is placed at `~/cn-project/tls/rootCA.pem`. The CA private key `rootCA-key.pem` stays on Mac 2. The client DNS servers are set once both DNS servers answer:

```bash
sudo networksetup -setdnsservers Wi-Fi $M1 $M4 && flushdns
scutil --dns | grep nameserver | sort -u
```

For browser access without certificate warnings, the CA is added to the system keychain:

```bash
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain "$CA"
```

### Step 1: Topology and IP/service inventory

Topology, IP table and request flow: `architecture/network-topology.md`, `architecture/ip_table.md`, `architecture/request_flow.md`. Interface details on each Mac:

```bash
networksetup -getinfo Wi-Fi
ifconfig en0 | grep -E 'ether|inet '
```

### Step 2: LAN connectivity

```bash
for ip in $M1 $M2 $M3 $M4; do echo "== $ip"; ping -c 2 $ip | tail -2; done
```

### Step 3: Private domain resolution

Expected: `app.teamX.test. 30 IN A <Mac 2>`, answered by `SERVER: <Mac 1>#53`, with the `aa` flag.

```bash
dig app.teamX.test
nslookup app.teamX.test
```

### Step 4: HTTPS by domain name

Certificate verification uses the team CA (`--cacert`); verification is never skipped. Expected: `TLSv1.3`, `subjectAltName ... matched`, `issuer: mkcert development CA`, `SSL certificate verify ok`, `ALPN: server accepted h2`.

```bash
curl --cacert "$CA" -v -o /dev/null $URL/ 2>&1 | grep -E 'Connected to|SSL connection|ALPN|subjectAltName|issuer|verify ok|HTTP/'
open $URL
```

Certificate served by the edge (Mac 2):

```bash
openssl x509 -in /opt/homebrew/etc/nginx/certs/app.teamX.test.pem -noout -subject -issuer -dates -ext subjectAltName
```

### Step 5: Load balancing

Expected: `x-backend` alternates between A and B.

```bash
lb
```

### Step 6: Packet capture (DNS, TCP, TLS)

Saved capture of one complete request: `Evidences/phase2/mac1/p1-09-full-request.pcap`.

```bash
open Evidences/phase2/mac1/p1-09-full-request.pcap
```

| Wireshark filter | Shows |
| :--- | :--- |
| `dns` | Frames 1–2: query and answer for `app.teamX.test` (UDP 53) |
| `tcp.flags.syn == 1` | Frames 3–4: SYN and SYN-ACK (client port 58446 → 443); frame 5 is the ACK |
| `tls.handshake.type == 1 \|\| tls.handshake.type == 2` | Frame 6 ClientHello (with SNI), frame 9 ServerHello |
| `tls` | All records after the ServerHello are encrypted Application Data; TLS 1.3 also encrypts the certificate |

New capture on a client:

```bash
sudo -v
sudo tcpdump -i en0 -w /tmp/demo.pcap "port 53 or port 443" &
sleep 1; flushdns; curl --cacert "$CA" -s -o /dev/null $URL/api/status; sleep 1; sudo pkill -INT tcpdump
open /tmp/demo.pcap
```

### Step 7: HTTP headers and caching

Response headers include `cache-control: max-age=60`, `etag`, `x-backend` and `x-edge`:

```bash
curl --cacert "$CA" -I $URL/api/status
```

Conditional requests with the ETag from the first response. The backend that issued the ETag answers `304 Not Modified`; the other backend answers `200`, because its body, and therefore its ETag, differs:

```bash
ET=$(curl --cacert "$CA" -sI $URL/api/status | tr -d '\r' | awk 'tolower($1)=="etag:"{print $2}'); echo "ETag $ET"
for n in 1 2; do curl --cacert "$CA" -si -H "If-None-Match: $ET" $URL/api/status | grep -iE '^(HTTP|x-backend|etag)'; echo; done
```

### Step 8: Backend failure and failover (Ext D)

1. Client, both backends up (A and B alternate):

   ```bash
   lb
   ```

2. Mac 3: Backend A is stopped with Ctrl+C.
3. Client: every request returns `200` from Backend B:

   ```bash
   lb
   ```

4. Mac 2: nginx logs the refused connection to port 3001:

   ```bash
   tail -n 5 /opt/homebrew/var/log/nginx/error.log
   ```

5. Mac 3: Backend A is restarted. After the 10 s `fail_timeout`, A and B alternate again:

   ```bash
   python3 backends/backend-a/server.py
   ```

   ```bash
   lb
   ```

### Step 9: Phase 2 DNS and resilience

#### Ext A: Backup DNS

1. Client, backup server answers on its own:

   ```bash
   dig @$M4 app.teamX.test +short
   ```

2. Mac 1, primary stopped:

   ```bash
   sudo pkill -x dnsmasq
   ```

3. Client: the primary times out, the backup answers, and the application still returns `200`. A public resolver returns no answer for the private name while the edge stays reachable by IP:

   ```bash
   dig @$M1 app.teamX.test +time=2 +tries=1
   dig app.teamX.test | grep -E 'IN[[:space:]]+A|SERVER'
   curl --cacert "$CA" -sI $URL/ | head -1
   dig @8.8.8.8 app.teamX.test +short; ping -c 2 $M2 | tail -1
   ```

4. Mac 1, primary restarted:

   ```bash
   sudo /opt/homebrew/sbin/dnsmasq -C /opt/homebrew/etc/dnsmasq.conf
   ```

#### Ext B: TTL and controlled record change

`dig` queries the server directly and bypasses the client cache; `cached` shows the address the client resolver uses.

1. Client: TTL of 30 s, answer cached:

   ```bash
   dig app.teamX.test | grep -E 'IN[[:space:]]+A'
   flushdns; cached
   ```

2. Mac 1 and Mac 4: records changed to Mac 3:

   ```bash
   setrecords $M3
   ```

3. Client: the servers answer the new address, while the client keeps the old one until the cached entry expires (about 30–45 s), then switches (stop the loop with Ctrl+C):

   ```bash
   dig @$M1 app.teamX.test +short
   while true; do echo "$(date +%T) $(cached)"; sleep 5; done
   ```

4. Mac 1 and Mac 4: records restored:

   ```bash
   setrecords $M2
   ```

5. Client: the old answer stays until a manual flush, then the change is immediate:

   ```bash
   cached; flushdns; cached
   ```

#### Ext C: Service isolation with pf (Mac 3 and Mac 4)

1. Mac 1, direct access before the rules (`200`):

   ```bash
   curl -s -m 5 -o /dev/null -w '%{http_code}\n' http://$M3:3001/api/status
   curl -s -m 5 -o /dev/null -w '%{http_code}\n' http://$M4:3002/api/status
   ```

2. Mac 3 (Mac 4 uses `pf-isolation-mac4.conf`). `pfctl -E` prints a token that is used for the rollback:

   ```bash
   sudo pfctl -s info | head -1
   fixips configuration/phase2/pf-isolation-mac3.conf > /tmp/pf-iso.conf
   sudo pfctl -f /tmp/pf-iso.conf -E
   sudo pfctl -sr | grep -E 'port = 300[12]'
   ```

3. Mac 1: direct access is blocked, access through the edge still works:

   ```bash
   curl -s -m 5 http://$M3:3001/api/status || echo blocked
   curl -s -m 5 http://$M4:3002/api/status || echo blocked
   curl --cacert "$CA" -sI $URL/ | head -1
   ```

4. Mac 2: the edge still reaches both backends (`200`):

   ```bash
   curl -s -o /dev/null -w '%{http_code}\n' http://$M3:3001/api/status
   curl -s -o /dev/null -w '%{http_code}\n' http://$M4:3002/api/status
   ```

5. Mac 3 and Mac 4, rollback to the macOS default rules (completed before Ext E). `<token>` is the value printed in step 2; afterwards no Team X rules remain:

   ```bash
   sudo pfctl -f /etc/pf.conf && sudo pfctl -X <token>
   sudo pfctl -sr 2>/dev/null | grep -c 'port = 300[12]'
   ```

#### Ext E: Edge migration with DNS cutover

1. Mac 3, standby edge. The certificate and key from Mac 2 are copied into `/opt/homebrew/etc/nginx/certs/`; the configuration is identical except `X-Edge "mac3"`:

   ```bash
   sudo chmod 600 /opt/homebrew/etc/nginx/certs/app.teamX.test-key.pem
   fixips configuration/phase2/nginx-phase2.conf | sed 's/X-Edge "mac2"/X-Edge "mac3"/' | sudo tee /opt/homebrew/etc/nginx/nginx.conf >/dev/null
   sudo nginx -t && sudo nginx
   ```

2. Client: the standby is tested without changing DNS (`x-edge: mac3`), while normal requests still reach Mac 2 (`x-edge: mac2`):

   ```bash
   curl --cacert "$CA" -sI --resolve app.teamX.test:443:$M3 $URL/api/status | grep -i x-edge
   edge
   ```

3. Mac 1 and Mac 4, cutover:

   ```bash
   setrecords $M3
   ```

4. Client with a cached answer (Mac 1): still `mac2` immediately after the cutover, `mac3` once the cached entry expires:

   ```bash
   edge
   ```

5. Client without a cached answer (Mac 4): `mac3` immediately:

   ```bash
   flushdns; cached; edge
   ```

6. Cut back. Mac 1 and Mac 4:

   ```bash
   setrecords $M2
   ```

   Mac 3:

   ```bash
   sudo nginx -s stop
   ```

   Clients (`x-edge: mac2`):

   ```bash
   flushdns; edge
   ```

### Step 10: Fault diagnosis (Ext F)

Diagnosis follows the request path, stopping at the first layer that fails.

DNS (client, then Mac 1 / Mac 4):

```bash
scutil --dns | grep nameserver | sort -u
dig app.teamX.test
dig @$M1 app.teamX.test +short
dig @$M4 app.teamX.test +short
```

```bash
pgrep -fl dnsmasq
grep -E '^(listen-address|address|local-ttl)' /opt/homebrew/etc/dnsmasq.conf
```

IP and TCP (client, then Mac 2):

```bash
ping -c 2 $M2
nc -vz $M2 443
```

```bash
sudo lsof -nP -iTCP:443 -sTCP:LISTEN
```

TLS (client):

```bash
openssl s_client -connect $M2:443 -servername app.teamX.test -CAfile "$CA" </dev/null 2>/dev/null | grep -E 'subject=|issuer=|Verify return'
```

Application (client, then Mac 2, then Mac 3 / Mac 4):

```bash
curl --cacert "$CA" -i $URL/api/status
```

```bash
sudo nginx -t
tail -n 20 /opt/homebrew/var/log/nginx/error.log
curl -s -i http://$M3:3001/api/status
curl -s -i http://$M4:3002/api/status
```

```bash
sudo pfctl -sr 2>/dev/null | grep 300
```

| Symptom | Layer | Likely cause |
| :--- | :--- | :--- |
| `Could not resolve host` | DNS | Client DNS servers changed, dnsmasq stopped, record missing or misspelt |
| Name resolves, connection times out | IP / DNS data | Record points to the wrong IP, machine asleep or on another network |
| `Connection refused` on 443 | TCP | nginx stopped, wrong port, firewall rule |
| `SSL certificate problem` / name mismatch | TLS | Wrong certificate path, certificate without that name, client missing `rootCA.pem` |
| `502 Bad Gateway` | Application (upstream) | Backends down, wrong IP/port in `upstream`, pf blocking the edge |
| Only one `x-backend` value | Upstream | One backend down or removed from `upstream` |

### Phase 1 Failure Scenarios

**Wrong DNS server on a client.** The name no longer resolves, while the edge is still reachable by IP. Client:

```bash
sudo networksetup -setdnsservers Wi-Fi 8.8.8.8 && flushdns
curl --cacert "$CA" -sI $URL/
ping -c 2 $M2 | tail -1
sudo networksetup -setdnsservers Wi-Fi $M1 $M4 && flushdns
```

**DNS record points to a wrong IP.** Resolution succeeds, but the connection goes to a host with no service on 443. Mac 1 and Mac 4:

```bash
setrecords $M1
```

Client:

```bash
flushdns; dig app.teamX.test +short; curl --cacert "$CA" -sI $URL/
```

Mac 1 and Mac 4, restore:

```bash
setrecords $M2
```

**Both backends stopped** (Ctrl+C on Mac 3 and Mac 4). DNS and TLS still work at the edge; the application returns `502`. Client:

```bash
curl --cacert "$CA" -si $URL/api/status | head -1
```

**Wrong destination port.** The host is reachable, but nothing listens on the port. Client:

```bash
nc -vz $M2 443
nc -vz $M2 8443
curl --cacert "$CA" -sI https://app.teamX.test:8443/
```

### Teardown

Clients:

```bash
sudo networksetup -setdnsservers Wi-Fi Empty && flushdns
sudo security remove-trusted-cert -d "$CA"
```

Mac 1 and Mac 4:

```bash
sudo pkill -x dnsmasq
```

Mac 2 (and Mac 3 if the standby edge is running):

```bash
sudo nginx -s stop
```

Mac 3 and Mac 4, if the pf rules are still loaded:

```bash
sudo pfctl -f /etc/pf.conf && sudo pfctl -X <token>
```
