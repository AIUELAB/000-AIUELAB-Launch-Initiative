# 🌐 Remote MCP Servers Guide (2025 Feature)

## Overview

Remote MCP servers allow Claude Code to connect to cloud-hosted services without managing local server infrastructure. This feature, introduced in August 2025, revolutionizes how AI tools integrate with external services.

## Key Benefits

- ✅ **No Local Setup**: Connect directly to cloud services
- ✅ **Automatic Updates**: Vendors manage server updates
- ✅ **Better Security**: OAuth 2.0 authentication
- ✅ **Scalability**: Cloud infrastructure handles load
- ✅ **Cross-Platform**: Works on any system with internet

## Transport Protocols

### 1. SSE (Server-Sent Events)
Real-time streaming connections for live updates.

```json
{
  "transport": "sse",
  "url": "https://service.com/mcp/sse",
  "headers": {
    "Authorization": "Bearer ${API_KEY}"
  }
}
```

**Best for:**
- Real-time notifications
- Live data streams
- Event-driven updates

### 2. HTTP (Streamable HTTP)
Standard request/response pattern with optional streaming.

```json
{
  "transport": "http",
  "url": "https://api.service.com/mcp",
  "oauth": {
    "clientId": "${CLIENT_ID}",
    "scope": "read write"
  }
}
```

**Best for:**
- RESTful APIs
- Request/response patterns
- Batch operations

## Quick Start

### Step 1: Setup Remote Servers

```bash
# Run the setup script
./scripts/setup-remote-mcp.sh

# Or manually add servers
claude mcp add --transport sse linear https://mcp.linear.app/sse
claude mcp add --transport http notion https://api.notion.com/v1/mcp
```

### Step 2: Configure Authentication

Edit `.env.mcp`:
```bash
# Linear
LINEAR_API_KEY=lin_api_xxxxxxxxxxxxx

# Notion OAuth
NOTION_CLIENT_ID=xxxxx-xxxx-xxxx-xxxx
NOTION_CLIENT_SECRET=secret_xxxxxxxxxxxx

# Sentry
SENTRY_AUTH_TOKEN=sntryu_xxxxxxxxxxxx
```

### Step 3: Test Connection

```bash
# List all servers
claude mcp list

# Test specific server
claude mcp test linear

# Check server status
claude mcp status
```

## Available Remote Servers

### 📋 Linear
**Issue tracking and project management**

- Transport: SSE
- Auth: Bearer token
- Capabilities:
  - Create/update issues
  - Manage projects
  - Track roadmaps
  - Search workspace

```bash
claude mcp add --transport sse linear https://mcp.linear.app/sse
```

### 📝 Notion
**Knowledge base and workspace**

- Transport: HTTP
- Auth: OAuth 2.0
- Capabilities:
  - Create/edit pages
  - Query databases
  - Search content
  - Manage workspaces

```bash
claude mcp add --transport http notion https://api.notion.com/v1/mcp
```

### 🚨 Sentry
**Error tracking and monitoring**

- Transport: SSE
- Auth: Bearer token
- Capabilities:
  - Track errors
  - Monitor performance
  - Manage releases
  - Alert configuration

```bash
claude mcp add --transport sse sentry https://sentry.io/api/mcp/sse
```

### 🔧 Apidog
**API documentation and testing**

- Transport: HTTP
- Auth: API key
- Capabilities:
  - Generate API docs
  - Test endpoints
  - Mock servers
  - Schema validation

```bash
claude mcp add --transport http apidog https://api.apidog.com/mcp
```

### 🕷️ SimpleScraper
**Web scraping service**

- Transport: SSE
- Auth: API key
- Capabilities:
  - Extract web data
  - Schedule scraping
  - Handle JavaScript
  - Export formats

```bash
claude mcp add --transport sse simplescraper https://api.simplescraper.io/mcp/sse
```

## Authentication Methods

### 1. API Key
Simple key-based authentication:

```bash
claude mcp add --transport http service https://api.service.com/mcp \
  --header "X-API-Key: your-api-key"
```

### 2. Bearer Token
OAuth or JWT tokens:

```bash
claude mcp add --transport sse service https://service.com/mcp/sse \
  --header "Authorization: Bearer your-token"
```

### 3. OAuth 2.0
Full OAuth flow with refresh tokens:

```bash
claude mcp add --transport http service https://api.service.com/mcp \
  --oauth-client-id "your-client-id" \
  --oauth-client-secret "your-client-secret" \
  --oauth-scope "read write"
```

## Configuration Examples

### Basic Remote Server
```json
{
  "service-name": {
    "transport": "sse",
    "url": "https://api.service.com/mcp/sse",
    "headers": {
      "Authorization": "Bearer ${SERVICE_API_KEY}"
    }
  }
}
```

### OAuth-Enabled Server
```json
{
  "oauth-service": {
    "transport": "http",
    "url": "https://api.service.com/mcp",
    "oauth": {
      "clientId": "${CLIENT_ID}",
      "clientSecret": "${CLIENT_SECRET}",
      "authorizationUrl": "https://service.com/oauth/authorize",
      "tokenEndpoint": "https://service.com/oauth/token",
      "scope": "read write admin"
    }
  }
}
```

### Custom Headers & Settings
```json
{
  "custom-service": {
    "transport": "http",
    "url": "${CUSTOM_MCP_URL}",
    "headers": {
      "X-API-Key": "${API_KEY}",
      "X-Client-ID": "${CLIENT_ID}",
      "X-Request-ID": "{{uuid}}"
    },
    "tlsVerify": true,
    "timeout": 30000,
    "retryPolicy": {
      "maxRetries": 3,
      "backoffMs": 1000
    }
  }
}
```

## Security Best Practices

### 1. Environment Variables
Never hardcode credentials:
```bash
# Good ✅
"Authorization": "Bearer ${LINEAR_API_KEY}"

# Bad ❌
"Authorization": "Bearer lin_api_actual_key_here"
```

### 2. TLS Verification
Always verify SSL certificates:
```json
{
  "tlsVerify": true,
  "tlsMinVersion": "1.2"
}
```

### 3. Token Rotation
Implement automatic token refresh:
```json
{
  "oauth": {
    "tokenRefreshBuffer": 300,
    "autoRefresh": true
  }
}
```

### 4. Scope Limitation
Request minimal permissions:
```json
{
  "oauth": {
    "scope": "read:issues write:comments"  // Specific scopes
  }
}
```

## Troubleshooting

### Connection Issues

**Problem**: Server unreachable
```bash
# Test connectivity
curl -I https://service.com/mcp/sse

# Check DNS
nslookup service.com

# Verify certificates
openssl s_client -connect service.com:443
```

**Solution**: Check firewall, proxy settings, or VPN

### Authentication Failures

**Problem**: 401 Unauthorized
```bash
# Verify token
claude mcp test service --debug

# Check environment variables
echo $SERVICE_API_KEY

# Refresh OAuth token
claude mcp auth refresh service
```

**Solution**: Regenerate API keys or re-authenticate

### Timeout Errors

**Problem**: Request timeout
```json
{
  "timeout": 60000,  // Increase to 60 seconds
  "keepAlive": true
}
```

### Rate Limiting

**Problem**: 429 Too Many Requests
```json
{
  "rateLimiting": {
    "maxRequestsPerSecond": 10,
    "backoffStrategy": "exponential"
  }
}
```

## Performance Optimization

### 1. Connection Pooling
```json
{
  "connectionPool": {
    "maxConnections": 10,
    "keepAliveTimeout": 60000
  }
}
```

### 2. Response Caching
```json
{
  "cache": {
    "enabled": true,
    "ttlSeconds": 300,
    "maxSize": "100MB"
  }
}
```

### 3. Compression
```json
{
  "headers": {
    "Accept-Encoding": "gzip, deflate, br"
  }
}
```

## Advanced Features

### Hybrid Configuration
Use local server with remote fallback:

```json
{
  "github-hybrid": {
    "primary": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-github"]
    },
    "fallback": {
      "transport": "sse",
      "url": "https://api.github.com/mcp/sse"
    }
  }
}
```

### Load Balancing
Distribute requests across multiple endpoints:

```json
{
  "service-lb": {
    "transport": "http",
    "urls": [
      "https://api1.service.com/mcp",
      "https://api2.service.com/mcp",
      "https://api3.service.com/mcp"
    ],
    "loadBalancer": "round-robin"
  }
}
```

### Circuit Breaker
Prevent cascading failures:

```json
{
  "circuitBreaker": {
    "enabled": true,
    "failureThreshold": 5,
    "resetTimeout": 60000
  }
}
```

## Platform Support

| Platform | SSE Support | HTTP Support | OAuth 2.0 |
|----------|------------|--------------|-----------|
| Claude Web | ✅ | ✅ | ✅ |
| Claude Desktop | ✅ | ✅ | ✅ |
| Claude Code | ✅ | ✅ | ✅ |
| Claude Mobile | ✅* | ✅* | ✅* |
| VS Code | ⚠️ Legacy | ✅ | ✅ |

*Mobile: Can use servers added via web, cannot add new ones

## Migration Guide

### From Local to Remote

1. **Identify local servers to migrate**
```bash
claude mcp list --local
```

2. **Find remote equivalents**
```bash
claude mcp search github
claude mcp search notion
```

3. **Add remote servers**
```bash
claude mcp add --transport sse service https://service.com/mcp/sse
```

4. **Test functionality**
```bash
claude mcp test service
```

5. **Remove local servers**
```bash
claude mcp remove local-service
```

## CLI Commands

```bash
# Add remote server
claude mcp add --transport [sse|http] <name> <url>

# Add with authentication
claude mcp add --transport sse <name> <url> --header "Authorization: Bearer token"

# Add with OAuth
claude mcp add --transport http <name> <url> --oauth

# List all servers
claude mcp list

# Test server connection
claude mcp test <name>

# Remove server
claude mcp remove <name>

# Update server configuration
claude mcp update <name> --url <new-url>

# Check server status
claude mcp status <name>

# View server logs
claude mcp logs <name>

# Refresh OAuth token
claude mcp auth refresh <name>
```

## Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [Transport Protocols](https://modelcontextprotocol.io/docs/transports)
- [OAuth 2.0 Guide](https://modelcontextprotocol.io/docs/auth)
- [Claude Code Docs](https://docs.anthropic.com/claude-code/mcp)
- [Community Servers](https://github.com/modelcontextprotocol/servers)

## FAQ

**Q: Are remote servers faster than local?**
A: It depends. Local servers have lower latency but remote servers offer better scalability and no maintenance overhead.

**Q: Can I use both local and remote servers?**
A: Yes! The hybrid configuration allows using both simultaneously.

**Q: Is SSE being deprecated?**
A: SSE is marked as "legacy" in VS Code but still fully supported in Claude products. Streamable HTTP is the recommended protocol going forward.

**Q: How secure are remote servers?**
A: Very secure when properly configured. Use OAuth 2.0, TLS 1.2+, and follow security best practices.

**Q: What about rate limits?**
A: Each service has its own rate limits. Configure retry policies and backoff strategies accordingly.

---

*Last updated: 2025-08-17 | Remote MCP Servers v1.0*