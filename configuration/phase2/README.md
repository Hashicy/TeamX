# Phase 2 Setup and Demo Guide (Team X)

Phase 2 extends the Phase 1 network: backup DNS, DNS TTL, backend firewall isolation, HA failover and DNS-based edge migration. This guide lists what each Mac ran and what we observed in the Phase 2 session on **23 Nov 2026**. Evidence for every step is in `Evidences/phase2/mac1` … `mac4`.

| Mac | IP (Phase 2 session) | Phase 1 role | Added in Phase 2 |
|---|---|---|---|
| Mac 1 (Manan) | 10.7.31.159 | Primary DNS + client | 30 s TTL on records |
| Mac 2 (Harshita) | 10.7.4.179 | Edge nginx (TLS, load balancer) | Failover config, HTTP/2, `X-Edge` header |
| Mac 3 (Soumya) | 10.7.28.230 | Backend A :3001 | pf isolation, **standby edge nginx** (Ext E) |
| Mac 4 (Niharika) | 10.7.15.199 | Backend B :3002 + client | pf isolation, **backup DNS** (Ext A) |

Full interface details (mask, gateway, MAC addresses) are in `architecture/ip_table.md`.

Files in this folder:

| File | Installed on | Used for |
|---|---|---|
| `dnsmasq-primary.conf` | Mac 1 → `/opt/homebrew/etc/dnsmasq.conf` | Ext A, B, E |
| `dnsmasq-backup.conf` | Mac 4 → `/opt/homebrew/etc/dnsmasq.conf` | Ext A, B, E |
| `nginx-phase2.conf` | Mac 2 (and Mac 3 for Ext E) → `/opt/homebrew/etc/nginx/nginx.conf` | Ext D, E |
| `pf-isolation-mac3.conf` / `-mac4.conf` | Mac 3 / Mac 4 (loaded directly, not copied) | Ext C |

> The files keep the Phase 1 addresses (`10.7.17.51`, `10.7.8.105`, `10.7.7.136`, `10.7.12.123`). Addresses change on our Wi-Fi between sessions, so before installing a file, replace each Phase 1 address with that Mac's current one (table above). Keep a copy of every file you overwrite: `cp <file> <file>.phase1.bak`.

---

## What we fixed from Phase 1

| Item | Phase 1 | Phase 2 |
|---|---|---|
| Backend identification | Only Backend B sent `X-Backend` | Both backends send `X-Backend: A` / `B` |
| HTTP caching (Task F) | Only `Cache-Control` shown | Backends send an `ETag` and answer `If-None-Match` with **304 Not Modified**; `curl -I` (HEAD) works |
| Duplicate headers | nginx and the backend both added `Cache-Control` | nginx hides the backend copy, so clients get one header |
| DNS TTL | `0` (never cached) | `30` s on both DNS servers |
| Client DNS settings (Task B) | Only shown on Mac 1 | Client Macs use the team DNS servers (primary + backup), shown on each client |
| Network inventory (Task A) | IPs only | IP, mask, gateway, interface and MAC address per Mac; ping between every pair |
| Packet capture (Task G) | Separate DNS / TCP / TLS captures | One capture of a complete request: DNS query/answer, TCP handshake, TLS, encrypted data |
| Certificate | mkcert local CA | mkcert approved by the faculty; clients verify the edge with the team root CA (`curl --cacert`), never `-k` |
| HTTP version | HTTP/1.1 | HTTP/2 negotiated through ALPN |

---

## 0. Before starting

* **Mac 3, Mac 4:** `git pull`, then start the backend in its own Terminal and keep it open:
  `python3 backends/backend-a/server.py` (Mac 3) · `python3 backends/backend-b/server.py` (Mac 4).
  If macOS asks *"Allow python3 to accept incoming network connections?"*, click **Allow**.
* **Mac 2:** install `nginx-phase2.conf`, then `sudo nginx -t` (must say *syntax is ok*), then start or reload nginx.
* **Clients:** copy `rootCA.pem` from Mac 2 (the folder shown by `mkcert -CAROOT`; **never** `rootCA-key.pem`) to `~/cn-project/tls/rootCA.pem`. Every HTTPS request below uses `curl --cacert ~/cn-project/tls/rootCA.pem …`.
* **DNS servers on each client** (primary first, then backup):
  `sudo networksetup -setdnsservers Wi-Fi 10.7.31.159 10.7.15.199`
  Do this only once both team DNS servers are running, otherwise the Mac loses all name lookups.
* dnsmasq is started and stopped directly, as in Phase 1:
  start `sudo /opt/homebrew/sbin/dnsmasq -C /opt/homebrew/etc/dnsmasq.conf` · stop `sudo pkill -x dnsmasq`.
* Keep every Mac awake and on the same Wi-Fi for the whole session (`caffeinate -d` in a spare Terminal tab).
  If a Mac is slow to reach another one at first, `ping <ip>` until replies arrive, then continue.

---

## Task F: caching demo

```bash
# Headers only: Cache-Control and ETag
curl --cacert ~/cn-project/tls/rootCA.pem -I https://app.teamX.test/api/status

# Send the ETag back twice ("has it changed?")
curl --cacert ~/cn-project/tls/rootCA.pem -si -H 'If-None-Match: "<etag from above>"' https://app.teamX.test/api/status
```

Round-robin alternates the backends, and each backend has its own ETag (their bodies differ). So the conditional request gets **304 Not Modified** from the backend that issued the ETag and **200** (with its own ETag) from the other one. We sent it twice per run and got exactly that in both runs.

Three cases to explain: **fresh hit** (within `max-age=60`, the client sends nothing), **conditional request** (`If-None-Match` → `304`, no body), **full request** (`200` with body).

---

## Extension A: Backup DNS resolver (Mac 4)

1. **Mac 4:** install `dnsmasq-backup.conf` (same records and TTL as the primary, listening on Mac 4's IP) and start dnsmasq.
2. **Mac 1:** install `dnsmasq-primary.conf` and restart dnsmasq.
3. **Every client:** list both servers, primary first (see section 0). Check: `scutil --dns | grep nameserver`.
4. From a client: `dig @10.7.15.199 app.teamX.test` returns `10.7.4.179`, so the backup works on its own.
5. **Mac 1:** stop the primary (`sudo pkill -x dnsmasq`).
6. From a client: `dig app.teamX.test` still resolves, answered by `SERVER: 10.7.15.199`, and `curl https://app.teamX.test/` still returns `200`.
7. **Mac 1:** start the primary again.

**Observed:** with the primary stopped, `dig @10.7.31.159` timed out, `dig app.teamX.test` was answered by the backup, and the app kept returning `HTTP/2 200`.

**Explain:** a DNS failure means the *name* can't be turned into an IP (`Could not resolve host`), although the machines are still reachable by IP. Asking the wrong server (8.8.8.8) gives `NXDOMAIN` while `ping 10.7.4.179` still works. An application failure means the name resolves fine but the service answers with an error or refuses (502, connection refused).

---

## Extension B: TTL and a controlled record change

Records now carry `local-ttl=30` (Phase 1 was **0**). `dig` asks a DNS server directly and skips the Mac's cache, so the client's view is checked with `dscacheutil -q host -a name app.teamX.test` (or `ping app.teamX.test`, which shows the resolved IP).

1. `dig app.teamX.test`: the TTL column shows **30**.
2. **Client:** flush the cache, then `dscacheutil -q host -a name app.teamX.test` → `10.7.4.179` (now cached).
3. **Mac 1 and Mac 4:** change both `address=` lines to another IP (we used Mac 3, `10.7.28.230`) and restart dnsmasq.
4. Both servers now answer `10.7.28.230` (`dig @10.7.31.159 …`, `dig @10.7.15.199 …`), but the client still uses the cached `10.7.4.179`.
5. Wait, checking the client every few seconds, until it switches to `10.7.28.230`.
6. Put the records back to `10.7.4.179` on both servers. The client still holds `10.7.28.230`. Flush manually:
   `sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder`, and the client shows `10.7.4.179` immediately.

**Observed:** the client switched about **43 s** after caching the answer, although the record's TTL was 30 s. The macOS resolver cache kept the entry a little longer than the TTL, so in practice the TTL is the *minimum* time clients keep using an old answer, not an exact deadline. The manual flush made the change visible at once.

**Explain:** in production, teams lower the TTL *before* a migration so clients pick up the new IP quickly, then raise it again. A long TTL means some users keep reaching the old server until their cached answer expires.

---

## Extension C: Service isolation with pf (Mac 3 and Mac 4)

The rules allow only the edge (`10.7.4.179`) to reach the backend port; everyone else gets a TCP reset.

1. **Before:** from Mac 1, `curl -i http://10.7.28.230:3001/api/status` works (direct access, which we want to stop).
2. **Mac 3:** note whether pf was enabled (`sudo pfctl -s info | head -1`), then
   `sudo pfctl -f configuration/phase2/pf-isolation-mac3.conf -E` and **note the `Token :` it prints**.
   **Mac 4:** the same with `pf-isolation-mac4.conf`.
3. `sudo pfctl -sr` on each shows the two Team X rules (`pass … from 10.7.4.179 … port = 3001`, `block return … port = 3001`).
4. From Mac 1: direct `curl` to either backend is **blocked**. From Mac 2: the same requests return `200 OK`. From Mac 1, `https://app.teamX.test/` still works (the edge path is untouched).
5. **Rollback (mandatory), Mac 3 and Mac 4:** `sudo pfctl -f /etc/pf.conf` (macOS defaults, never edited), then `sudo pfctl -X <token>` to disable pf again if it was off before. Direct access from Mac 1 works again.

**Observed:** Mac 1 was blocked from both backends while still getting `HTTP/2 200` through the edge; Mac 2 reached both backends; after rollback, Mac 3 showed pf disabled with 0 Team X rules left, and direct access from Mac 1 returned `200` for both backends.

> Roll back C **before** doing E: the standby edge on Mac 3 must be able to reach both backends.

---

## Extension D: HA failover (Mac 2 config, Mac 3 stops/starts)

`nginx-phase2.conf` marks a backend down after 1 failure for 10 s (`max_fails=1 fail_timeout=10s`) and retries the request on the other backend (`proxy_next_upstream`, `proxy_connect_timeout 2s`), so clients still get a 200.

1. **Client:** repeated requests show A and B alternating:
   `for i in 1 2 3 4 5 6; do curl --cacert ~/cn-project/tls/rootCA.pem -s -o /dev/null -D - https://app.teamX.test/api/status | grep -i x-backend; done`
2. **Mac 3:** stop Backend A (Ctrl+C).
3. Same loop: every request is `200` with `X-Backend: B`, and none fail.
4. **Mac 3:** start Backend A again and wait ~10 s.
5. Same loop: A and B alternate again.

**Observed:** with A stopped, 6 of 6 requests returned `200` from B. nginx's error log recorded `connect() failed (61: Connection refused) … upstream: "http://10.7.28.230:3001/api/status"`, and its access log shows the same requests answered with `200`. After the restart, the first two requests still went to B (A was still inside its 10 s `fail_timeout`), then balancing resumed.

**Single point of failure:** nginx on Mac 2. If it (or Mac 2) stops, nothing works even though both backends are fine. Removing it needs a second edge plus a way to move traffic: DNS with two A records or DNS failover (what Ext E shows), a floating/virtual IP (VRRP/keepalived), or a managed cloud load balancer that is itself redundant across zones.

---

## Extension E: Edge migration with DNS cutover (standby edge on Mac 3)

1. **Mac 3:** `brew install nginx`. Copy `app.teamX.test.pem` and `app.teamX.test-key.pem` from Mac 2 into `/opt/homebrew/etc/nginx/certs/` (`chmod 600` the key) and install `nginx-phase2.conf` with one change: `add_header X-Edge "mac2"` → `"mac3"`. Then `sudo nginx -t && sudo nginx`.
2. Test the standby without touching DNS:
   `curl --cacert ~/cn-project/tls/rootCA.pem -sI --resolve app.teamX.test:443:10.7.28.230 https://app.teamX.test/api/status` gives `X-Edge: mac3`.
3. **Client A** (keeps its cache): `curl … https://app.teamX.test/api/status` gives `X-Edge: mac2`.
4. **Mac 1 and Mac 4:** change both `address=` lines to `10.7.28.230`, restart dnsmasq.
5. **Client A, straight away:** still `X-Edge: mac2` (cached answer).
   **Client B** (Mac 4, cache flushed first): `X-Edge: mac3`.
6. After the cached answer expires, Client A also shows `mac3`.
7. **Cut back:** records to `10.7.4.179` on both DNS servers and restart; `sudo nginx -s stop` on Mac 3.

**Observed:** Mac 3's standby passed `nginx -t` and served `HTTP/2 200` with `X-Edge: mac3`. Right after the cutover Mac 1 (cached) was still served by `mac2`, then moved to `mac3` once its cached answer expired; after cutting back, `mac2` served again.

---

## Extension F: Faculty-injected fault

Diagnose layer by layer and say each step out loud: **DNS** (`scutil --dns`, `dig`, `dig @<each team DNS>`), then **IP/TCP** (`ping`, `nc -vz <edge> 443`), then **TLS** (`openssl s_client -connect <edge>:443 -servername app.teamX.test`), then the **application** (`curl -i`, nginx `error.log`). Stop at the first layer that fails; that is where the fault is.
