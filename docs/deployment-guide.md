# Deployment Guide

**Version:** 0.7.1 | **Supported Platforms:** macOS, Windows, Linux

## Local Development Setup

### Prerequisites
- **Bun** 1.0+ ([install](https://bun.sh/))
- **Node.js** 18+ (or use Bun's Node compat)
- **Git** 2.0+
- **macOS:** Xcode Command Line Tools
- **Linux:** build-essential, python3
- **Windows:** Visual Studio Build Tools (for native modules)

### Installation

```bash
git clone https://github.com/lukilabs/craft-agents-oss.git
cd craft-agents-oss

# Install all workspace dependencies
bun install

# Set up environment variables (optional, for OAuth)
cp .env.example .env
# Edit .env with your OAuth credentials (optional)
```

### Running in Development

**Desktop App (hot reload):**
```bash
bun run electron:dev
```

Opens Electron with hot-reload for UI changes. Logs: `~/Library/Logs/@craft-agent/electron/`

**Headless Server:**
```bash
bun run server:dev
```

Starts server at `ws://127.0.0.1:9100` with debug logging enabled.

**CLI Testing:**
```bash
bun run apps/cli/src/index.ts ping
bun run apps/cli/src/index.ts run "Hello, world!"
```

### Type Checking & Tests

```bash
# Type check all packages
bun run typecheck:all

# Run tests
bun run test:shared:all

# Lint code
bun run lint
```

## Building for Production

### Desktop App (Packaged)

**macOS:**
```bash
bun run electron:dist:mac
# Output: apps/electron/dist/Craft\ Agents*.dmg
```

**Windows:**
```bash
bun run electron:dist:win
# Output: apps/electron/dist/Craft\ Agents*.exe
```

**Linux:**
```bash
bun run electron:dist:linux
# Output: apps/electron/dist/Craft\ Agents*.AppImage
```

**All Platforms:**
```bash
bun run electron:dist
# Packages for your current platform
```

**Output Location:** `apps/electron/dist/`

### Headless Server Binary

```bash
# Build for current platform
bun run server:build
# Output: server-standalone (executable)

# Build for specific platform
bun run server:build:linux-x64
bun run server:build:linux-arm64
bun run server:build:darwin-arm64
bun run server:build:darwin-x64
# Outputs: ./<platform>-<arch>/craft-agent-server
```

**Binary Usage:**
```bash
./craft-agent-server
# Listens on ws://127.0.0.1:9100
```

## Headless Server Deployment

### Local / Development

```bash
# Generate a token
CRAFT_SERVER_TOKEN=$(openssl rand -hex 32) bun run packages/server/src/index.ts

# Or with Bun built server
export CRAFT_SERVER_TOKEN=$(openssl rand -hex 32)
./craft-agent-server
```

**Output:**
```
✓ Server listening at ws://127.0.0.1:9100
✓ Token: abc123...
```

**Connect Desktop App:**
```bash
CRAFT_SERVER_URL=ws://127.0.0.1:9100 \
CRAFT_SERVER_TOKEN=abc123... \
bun run electron:start
```

### Remote Server (Linux VPS)

**Prerequisites:**
- Ubuntu/Debian Linux with 2GB+ RAM
- Public IP or domain
- Port 9100 open (or behind reverse proxy)

**Installation:**

```bash
# SSH into server
ssh user@your-server.com

# Download binary (or build)
wget https://releases.craft.do/craft-agent-server-linux-x64
chmod +x craft-agent-server-linux-x64

# Create systemd service
sudo tee /etc/systemd/system/craft-agent.service > /dev/null << EOF
[Unit]
Description=Craft Agent Server
After=network.target

[Service]
Type=simple
User=craft
WorkingDirectory=/opt/craft-agent
ExecStart=/opt/craft-agent/craft-agent-server-linux-x64
Environment="CRAFT_SERVER_TOKEN=$(openssl rand -hex 32)"
Environment="CRAFT_RPC_HOST=0.0.0.0"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable & start service
sudo systemctl daemon-reload
sudo systemctl enable craft-agent
sudo systemctl start craft-agent

# Check status
sudo systemctl status craft-agent
journalctl -u craft-agent -f
```

**Data Directory:**
```bash
# Create and set permissions
sudo mkdir -p /opt/craft-agent/data
sudo chown craft:craft /opt/craft-agent/data
```

Environment variables:
```bash
# Add to /etc/systemd/system/craft-agent.service [Service] section
Environment="CRAFT_RPC_HOST=0.0.0.0"
Environment="CRAFT_RPC_PORT=9100"
Environment="CRAFT_SERVER_TOKEN=your-secure-token-here"
Environment="CRAFT_DEBUG=false"
```

### TLS Configuration

**Generate Self-Signed Certificate (development):**
```bash
./scripts/generate-dev-cert.sh
# Creates: certs/cert.pem, certs/key.pem (valid 365 days)
```

**Start Server with TLS:**
```bash
CRAFT_SERVER_TOKEN=<token> \
CRAFT_RPC_HOST=0.0.0.0 \
CRAFT_RPC_TLS_CERT=certs/cert.pem \
CRAFT_RPC_TLS_KEY=certs/key.pem \
./craft-agent-server
```

**Connect Client (with self-signed cert):**
```bash
CRAFT_SERVER_URL=wss://your-server.com:9100 \
CRAFT_SERVER_TOKEN=<token> \
CRAFT_TLS_CA=certs/cert.pem \
bun run electron:start
```

**Production TLS (Let's Encrypt):**

```bash
# Use Certbot on server
sudo apt-get install certbot
sudo certbot certonly --standalone -d your-server.com

# Update service environment
Environment="CRAFT_RPC_TLS_CERT=/etc/letsencrypt/live/your-server.com/fullchain.pem"
Environment="CRAFT_RPC_TLS_KEY=/etc/letsencrypt/live/your-server.com/privkey.pem"

sudo systemctl restart craft-agent
```

**Behind Reverse Proxy (Recommended):**

Use nginx or Caddy to handle TLS, then proxy to local server:

```nginx
server {
    listen 443 ssl http2;
    server_name your-server.com;

    ssl_certificate /etc/letsencrypt/live/your-server.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-server.com/privkey.pem;

    location / {
        proxy_pass ws://127.0.0.1:9100;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## Docker Deployment

### Build Image

```bash
# Use existing Dockerfile (if available)
docker build -t craft-agent-server:latest .

# Or use pre-built image
docker pull craft.do/craft-agent-server:latest
```

### Run Container

**Basic:**
```bash
docker run -d \
  -p 9100:9100 \
  -e CRAFT_SERVER_TOKEN=$(openssl rand -hex 32) \
  -e CRAFT_RPC_HOST=0.0.0.0 \
  -v craft-data:/root/.craft-agent \
  --name craft-agent \
  craft-agent-server:latest
```

**With TLS:**
```bash
docker run -d \
  -p 9100:9100 \
  -e CRAFT_SERVER_TOKEN=<token> \
  -e CRAFT_RPC_HOST=0.0.0.0 \
  -e CRAFT_RPC_TLS_CERT=/certs/cert.pem \
  -e CRAFT_RPC_TLS_KEY=/certs/key.pem \
  -v craft-data:/root/.craft-agent \
  -v ./certs:/certs:ro \
  --name craft-agent \
  craft-agent-server:latest
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  craft-agent:
    image: craft-agent-server:latest
    ports:
      - "9100:9100"
    environment:
      CRAFT_SERVER_TOKEN: ${CRAFT_SERVER_TOKEN}
      CRAFT_RPC_HOST: 0.0.0.0
      CRAFT_RPC_TLS_CERT: /certs/cert.pem
      CRAFT_RPC_TLS_KEY: /certs/key.pem
    volumes:
      - craft-data:/root/.craft-agent
      - ./certs:/certs:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "craft-cli", "ping"]
      interval: 30s
      timeout: 5s
      retries: 3

volumes:
  craft-data:
    driver: local
```

**Run:**
```bash
CRAFT_SERVER_TOKEN=$(openssl rand -hex 32) docker-compose up -d
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: craft-agent
spec:
  replicas: 1
  selector:
    matchLabels:
      app: craft-agent
  template:
    metadata:
      labels:
        app: craft-agent
    spec:
      containers:
      - name: craft-agent
        image: craft-agent-server:latest
        ports:
        - containerPort: 9100
        env:
        - name: CRAFT_SERVER_TOKEN
          valueFrom:
            secretKeyRef:
              name: craft-agent-secrets
              key: token
        - name: CRAFT_RPC_HOST
          value: "0.0.0.0"
        - name: CRAFT_RPC_TLS_CERT
          value: /certs/cert.pem
        - name: CRAFT_RPC_TLS_KEY
          value: /certs/key.pem
        volumeMounts:
        - name: data
          mountPath: /root/.craft-agent
        - name: certs
          mountPath: /certs
          readOnly: true
        livenessProbe:
          exec:
            command:
            - craft-cli
            - ping
          initialDelaySeconds: 10
          periodSeconds: 30
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: craft-agent-data
      - name: certs
        secret:
          secretName: craft-agent-certs
---
apiVersion: v1
kind: Service
metadata:
  name: craft-agent
spec:
  type: LoadBalancer
  ports:
  - port: 9100
    targetPort: 9100
  selector:
    app: craft-agent
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: craft-agent-data
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

**Deploy:**
```bash
kubectl create secret generic craft-agent-secrets \
  --from-literal=token=$(openssl rand -hex 32)

kubectl create secret tls craft-agent-certs \
  --cert=certs/cert.pem \
  --key=certs/key.pem

kubectl apply -f k8s-deployment.yaml

# Check status
kubectl get pods -l app=craft-agent
kubectl logs -f deployment/craft-agent
```

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CRAFT_SERVER_TOKEN` | Yes | — | Bearer token for client auth |
| `CRAFT_RPC_HOST` | No | `127.0.0.1` | Bind address (use `0.0.0.0` for remote) |
| `CRAFT_RPC_PORT` | No | `9100` | Bind port |
| `CRAFT_RPC_TLS_CERT` | No | — | Path to PEM cert (enables wss://) |
| `CRAFT_RPC_TLS_KEY` | No | — | Path to PEM key (required with cert) |
| `CRAFT_RPC_TLS_CA` | No | — | Path to CA chain (for client cert verification) |
| `CRAFT_DEBUG` | No | `false` | Enable debug logging |
| `ANTHROPIC_API_KEY` | No | — | Default Claude API key |
| `OPENAI_API_KEY` | No | — | Default OpenAI API key |
| `GOOGLE_API_KEY` | No | — | Default Google API key |
| `NODE_ENV` | No | `production` | Environment (production/development) |

## Monitoring & Maintenance

### Health Checks

```bash
# CLI health check
craft-cli --url ws://localhost:9100 --token <token> ping

# Server health endpoint (if enabled)
curl http://localhost:9100/health
```

### Logs

**Desktop App:**
- macOS: `~/Library/Logs/@craft-agent/electron/main.log`
- Windows: `%APPDATA%\@craft-agent\electron\logs\main.log`
- Linux: `~/.config/@craft-agent/electron/logs/main.log`

**Server (systemd):**
```bash
journalctl -u craft-agent -f
```

**Server (Docker):**
```bash
docker logs -f craft-agent
```

### Backups

**Backup user data:**
```bash
# Desktop app
tar -czf craft-agent-backup.tar.gz ~/.craft-agent/

# Server container
docker exec craft-agent tar -czf /root/.craft-agent/backup.tar.gz /root/.craft-agent/
docker cp craft-agent:/root/.craft-agent/backup.tar.gz ./
```

### Upgrades

**Desktop App:**
- Auto-updates via electron-updater (check for updates on launch)
- Manual: Download latest DMG/NSIS/AppImage

**Server Binary:**
```bash
# Stop existing
sudo systemctl stop craft-agent

# Replace binary
sudo cp craft-agent-server-linux-x64 /opt/craft-agent/

# Restart
sudo systemctl start craft-agent
```

**Docker:**
```bash
docker pull craft.do/craft-agent-server:latest
docker-compose up -d  # Recreates container with new image
```

## Troubleshooting

### Connection Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Connection timeout` | Server not running | Check `systemctl status craft-agent` |
| `AUTH_FAILED` | Wrong token | Verify `CRAFT_SERVER_TOKEN` matches |
| `WebSocket error` | Firewall blocking | Open port 9100 (or reverse proxy) |
| `SSL: certificate_verify_failed` | Self-signed cert | Use `--tls-ca` with cert path |

### Performance Issues

| Issue | Solution |
|-------|----------|
| High CPU usage | Reduce concurrent sessions, check tool pool |
| High memory usage | Monitor session count, clear old sessions |
| Slow tool responses | Check MCP server health, latency to server |
| Session lag | Use faster network, reduce message frequency |

### Data Loss Prevention

```bash
# Regular backups (cron job)
0 2 * * * tar -czf /backups/craft-agent-$(date +\%Y\%m\%d).tar.gz ~/.craft-agent/

# Keep last 30 days
find /backups -name "craft-agent-*.tar.gz" -mtime +30 -delete
```

## Security Checklist

- [ ] Use TLS for remote servers (wss:// not ws://)
- [ ] Set strong CRAFT_SERVER_TOKEN (32+ hex chars)
- [ ] Restrict firewall (only allow trusted clients)
- [ ] Enable debug logging only in development
- [ ] Rotate tokens periodically
- [ ] Restrict file permissions on certs (`chmod 600`)
- [ ] Use reverse proxy for production (nginx/Caddy)
- [ ] Enable audit logging (if using enterprise)
- [ ] Monitor credential store health regularly
- [ ] Keep dependencies up-to-date

## Performance Tuning

**For Large Deployments:**

```bash
# Increase max open files
ulimit -n 65536

# Tune kernel (Linux)
sysctl -w net.core.somaxconn=4096
sysctl -w net.ipv4.tcp_max_syn_backlog=4096

# Node.js memory
export NODE_OPTIONS="--max-old-space-size=4096"
```

**MCP Connection Pool:**
- Default pool size: 10 connections
- Adjust if many concurrent tools: `CRAFT_MCP_POOL_SIZE=50`

## Support & Resources

- **Docs:** [agents.craft.do/docs](https://agents.craft.do/docs)
- **Issues:** [GitHub Issues](https://github.com/lukilabs/craft-agents-oss/issues)
- **Discussions:** [GitHub Discussions](https://github.com/lukilabs/craft-agents-oss/discussions)
- **Security:** [SECURITY.md](../SECURITY.md)
