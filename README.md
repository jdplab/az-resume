# az-resume

Personal resume website hosted on Azure with serverless backend, CosmosDB storage, and integrated blog platform.

**Live Site**: [https://jon-polansky.com](https://jon-polansky.com)

---

## Architecture

### Tech Stack
- **Frontend**: Static HTML/CSS/JavaScript hosted on Azure Storage + CDN
- **Backend**: Azure Functions (Python 3.11) - serverless API
- **Database**: Azure CosmosDB (SQL API)
- **Storage**: Azure Blob Storage (images, static content)
- **Authentication**: Azure AD B2C
- **CDN**: Azure CDN + Cloudflare
- **Infrastructure**: Terraform (IaC)
- **CI/CD**: GitHub Actions

### High-Level Flow
```
User → Cloudflare → Azure CDN → Static Site (Storage) → Azure Functions → CosmosDB
                                                       ↓
                                                 Blob Cache (15min TTL)
```

---

## Features

- Personal resume and portfolio
- Blog platform with admin panel
- Comment system (authenticated users)
- Visitor counter
- Image storage and management
- Automatic HTTPS with Let's Encrypt
- Global CDN distribution

---

## Caching Implementation

### Overview

The application implements a **blob storage caching layer** to significantly reduce CosmosDB queries and improve response times.

### Cache Architecture

**Storage Location**: `blogposts/cache/` (blob container)  
**TTL**: 15 minutes (900 seconds)  
**Format**: JSON with metadata envelope

#### Cache Keys
```
cache/posts.json              - All blog posts list
cache/comments-{post_id}.json - Comments for specific post
```

#### Cache Invalidation Matrix

| Action | Function | Invalidates |
|--------|----------|-------------|
| Create new post | `saveblog` | `posts` |
| Edit existing post | `editpostsave` | `posts` |
| Delete post | `deletepost` | `posts` + `comments-{id}` |
| Submit comment | `submitcomment` | `comments-{id}` |

### Performance Improvements

| Metric | Before Caching | After Caching | Improvement |
|--------|---------------|---------------|-------------|
| Response Time | 100-200ms | 10-20ms | **80-90% faster** |
| CosmosDB Queries | ~100/day | ~10/day | **90% reduction** |
| RU Consumption | ~1,000 RUs/day | ~100 RUs/day | **90% savings** |
| Additional Cost | N/A | ~$0.01/month | Minimal |

### Key Features
- **Graceful degradation**: Cache failures fall back to CosmosDB
- **Comprehensive logging**: Cache HIT/MISS/INVALIDATE events tracked
- **Automatic expiration**: 15-minute TTL prevents stale data
- **Event-driven invalidation**: Content updates immediately clear cache

---

## Deployment

### Prerequisites
- Azure subscription
- Terraform Cloud account
- GitHub account
- Azure CLI installed
- Python 3.11+

### Deployment Steps

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd az-resume
   ```

2. **Deploy Infrastructure**
   ```bash
   terraform init
   terraform apply
   ```

3. **Deploy Functions** (via GitHub Actions)
   ```bash
   git push origin main
   ```

---

## API Endpoints

### Public Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/getrecentposts` | GET | Fetch all blog posts (cached) |
| `/api/getcomments?id={post_id}` | GET | Fetch comments for post (cached) |
| `/api/visitorcount?repeatVisit={bool}` | GET | Track/get visitor count |

### Authenticated Endpoints (Require JWT Token)

| Endpoint | Method | Auth Level | Description |
|----------|--------|------------|-------------|
| `/api/submitcomment?id={post_id}` | POST | User | Submit comment |
| `/api/saveblog` | POST | Admin | Create new post |
| `/api/editpostsave?id={post_id}` | POST | Admin | Edit existing post |
| `/api/deletepost?id={post_id}` | DELETE | Admin | Delete post |

---

## Development

### Local Development Setup

1. **Install Azure Functions Core Tools**
   ```bash
   npm install -g azure-functions-core-tools@4 --unsafe-perm true
   ```

2. **Install Python Dependencies**
   ```bash
   cd function
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run Functions Locally**
   ```bash
   func start
   ```

---

## Backup & Rollback

Backups are created before major changes in `backups/` directory (gitignored).

### Rollback Procedure

1. Stop Function App
2. Restore backup files from `backups/<timestamp>/`
3. Redeploy via Git
4. Restart Function App

See backup documentation in `backups/` for detailed instructions.

---

## Monitoring

### Key Metrics
- **Application Insights**: Function execution times, errors
- **CosmosDB Metrics**: RU consumption, query performance
- **CDN Metrics**: Cache hit ratio, bandwidth

### Cache Performance Query

```kusto
traces
| where message contains "Cache"
| summarize
    Hits = countif(message contains "HIT"),
    Misses = countif(message contains "MISS"),
    HitRate = 100.0 * countif(message contains "HIT") / count()
```

---

## Infrastructure

### Azure Resources
- **Resource Group**: `azresume`
- **Function App**: Python 3.11 on Consumption plan
- **CosmosDB**: SQL API, 400 RU/s per container
- **Storage Account**: Static website + blob storage
- **CDN Profile**: Standard Microsoft tier
- **Azure AD B2C**: User authentication

### Terraform State
- **Organization**: JP-Lab
- **Workspace**: azure-resume

---

## Cost Optimization

- Consumption plan for Functions (pay-per-execution)
- Blob caching reduces CosmosDB costs by 90%
- LRS storage replication
- CDN reduces origin requests

**Estimated Monthly Cost**: ~$10-20

---

## License

Private project - All rights reserved

---

**Last Updated**: 2025-11-30  
**Major Changes**: Added blob storage caching layer
