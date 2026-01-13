# Profile Management Guide

This guide covers how to create and manage Dremio CLI profiles using both YAML configuration files and environment variables.

## Overview

Profiles store connection information for Dremio instances. The CLI supports two methods:

1. **YAML Configuration** - Stored in `~/.dremio/profiles.yaml` (RECOMMENDED for local use)
2. **Environment Variables** - Loaded from `.env` file or shell environment (RECOMMENDED for CI/CD)

Environment variables take precedence over YAML profiles.

---

## 🚀 Profile Values Guide

### 1. Base URL
The URL to your Dremio instance's API.

| Platform | Format | Example | Note |
|----------|--------|---------|------|
| **Dremio Cloud** | `https://api.dremio.cloud/v0` | `https://api.dremio.cloud/v0` | Used for US control plane |
| **Dremio Cloud (EU)** | `https://api.dremio.eu/v0` | `https://api.dremio.eu/v0` | Used for EU control plane |
| **Dremio Software** | `http(s)://<host>:<port>` | `https://dremio.company.com` | **Smart URL**: The CLI automatically appends `/api/v3` if you omit it. |
| **Local Software** | `http://localhost:9047` | `http://localhost:9047` | Defaults for local Docker/install |

> **Note:** For Dremio Software, you can provide `https://dremio.company.com` OR `https://dremio.company.com/api/v3`. The CLI handles both correctly.

### 2. Authentication
How you log in to Dremio.

| Type | Platform | Description |
|------|----------|-------------|
| **PAT** (Token) | Cloud & Software | **Recommended**. Personal Access Token generated in User Settings. |
| **Services Account** | Cloud Only | Treats Client/Secret as a PAT for automation. |
| **Username/Password** | Software Only | Traditional login. **Less secure** than PAT. |

### 3. Project ID (Cloud Only)
Can be found in the URL of your Dremio Cloud project.
- URL: `https://app.dremio.cloud/projectId/12345-abcde.../home`
- Project ID: `12345-abcde...`

---

## YAML Configuration

**Location**: `~/.dremio/profiles.yaml`

### Examples

**Dremio Cloud (US)**
```yaml
profiles:
  cloud-prod:
    type: cloud
    base_url: https://api.dremio.cloud/v0
    project_id: 788baab4-3c3b-42da-9f1d-5cc6dc03147d
    auth:
      type: pat
      token: your-personal-access-token
```

**Dremio Software (Corporate)**
```yaml
profiles:
  corp-dremio:
    type: software
    base_url: https://dremio.corp.com  # CLI will add /api/v3 automatically
    auth:
      type: pat
      token: your-personal-access-token
```

**Dremio Software (Local/Docker)**
```yaml
profiles:
  local:
    type: software
    base_url: http://localhost:9047  # Default port
    auth:
      type: username_password
      username: admin
      password: password123
```

### CLI Commands

```bash
# Interactve Wizard (Best for beginners)
dremio init

# Create manually
dremio profile create --name prod --type cloud ...
```

---

## Environment Variable Configuration

Ideal for CI/CD pipelines or Docker containers.

### Pattern
`DREMIO_{PROFILE_NAME}_KEY=VALUE`

### Example `.env` File
```bash
# Cloud Profile (Name: 'CLOUD')
DREMIO_CLOUD_TYPE=cloud
DREMIO_CLOUD_BASE_URL=https://api.dremio.cloud/v0
DREMIO_CLOUD_PROJECTID=788baab4-3c3b-42da-9f1d-5cc6dc03147d
DREMIO_CLOUD_TOKEN=s3JcLOqFTR...

# Software Profile (Name: 'PROD')
DREMIO_PROD_TYPE=software
DREMIO_PROD_BASE_URL=https://dremio.corp.com
DREMIO_PROD_TOKEN=Q/ToosxORA...
```

### Usage
```bash
# Authenticates using DREMIO_PROD_* variables
dremio --profile prod catalog list
```

---

## Profile Management

```bash
# List all profiles
dremio profile list

# Show active profile details
dremio profile current

# Set default profile (so you don't need --profile flag)
dremio profile set-default cloud-prod
```
