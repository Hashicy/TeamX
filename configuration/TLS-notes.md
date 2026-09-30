

# TLS Certificate Setup and Configuration Notes for Mac 2 Edge Node

## Objective
The primary goal for Mac 2 in Phase 1 is to establish a secure HTTPS connection and handle TLS termination[cite: 1]. This ensures that when a client requests the private domain, the connection is encrypted using a locally trusted Certificate Authority, fulfilling Task E without relying on insecure bypass flags[cite: 1].

## Tools Utilized
* *mkcert*: Used to act as our local Certificate Authority to generate certificates that are automatically trusted by the local system.
* *OpenSSL*: Installed to support the underlying cryptographic functions.
* *Nginx*: Configured as the edge reverse proxy to listen on port 443 and serve these certificates to the client[cite: 1].

## Step-by-Step Implementation

### Step 1: Installing Required Packages
We installed the necessary tools on Mac 2 using Homebrew by running the following command in the terminal:
brew install nginx mkcert openssl


### Step 2: Initializing the Local Certificate Authority

We set up the local CA and added it to the macOS system trust store so that browsers natively trust the connection. We used the command:

```bash
mkcert -install

```

### Step 3: Generating the Domain Certificates

We created a dedicated directory for the certificates and generated them for our private namespaces, `app.team1.test` and `api.team1.test`, using the following commands:

```bash
sudo mkdir -p /opt/homebrew/etc/nginx/certs
sudo mkcert -cert-file /opt/homebrew/etc/nginx/certs/app.team1.test.pem -key-file /opt/homebrew/etc/nginx/certs/app.team1.test-key.pem app.team1.test api.team1.test

```

### Step 4: Securing File Permissions

To ensure the Nginx service could read the files securely without exposing the private key, we updated the file permissions with these commands:

```bash
sudo chmod 644 /opt/homebrew/etc/nginx/certs/app.team1.test.pem
sudo chmod 600 /opt/homebrew/etc/nginx/certs/app.team1.test-key.pem

```

## File Paths and Nginx Configuration Mapping

The generated TLS files are safely stored in the following exact locations on Mac 2:

* **Certificate File Path:** `/opt/homebrew/etc/nginx/certs/app.team1.test.pem`
* **Private Key File Path:** `/opt/homebrew/etc/nginx/certs/app.team1.test-key.pem`

In the Nginx configuration file located at `/opt/homebrew/etc/nginx/nginx.conf`, the server block was updated to include these paths under the `listen 443 ssl` directive. The `ssl_certificate` and `ssl_certificate_key` parameters were explicitly pointed to the exact paths listed above to ensure successful TLS termination at the edge before traffic is routed to the backend servers.

