# Master Project Plan
# CGP SDK + Steward Agent Backend

## Project Overview

Build a lightweight SDK (CGP - Cognitive Governance Protocol) and hosted backend infrastructure to allow clients to integrate Steward Agent oversight into their AI agent pipelines with minimal friction.

**Architecture Flow:**
```
Client Code -> CGP SDK (lightweight wrapper) -> Steward API -> GCP Infrastructure
```

**Decisions Made:**
- SDK: Framework-agnostic (works with any Python agent)
- Infrastructure: Google Cloud Platform
- Scope: Production-ready from start (multi-tenancy, rate limiting, proper ingestion)
- Repos: Separate from day one

**Repositories:**
- `cgp-sdk` - Python SDK for PyPI distribution
- `steward-agent-backend` - GCP-hosted backend service

---

## Timeline Overview

| Phase | Duration | Focus |
|-------|----------|-------|
| Phase 1 | 3-4 days | SDK Extraction |
| Phase 2 | 2-3 days | Async Transport |
| Phase 3 | 3-4 days | Multi-Tenancy Backend |
| Phase 4 | 3-4 days | Ingestion Pipeline |
| Phase 5 | 2-3 days | GCP Deployment |
| Phase 6 | 2-3 days | Polish & Publish |
| **Total** | **15-21 days** | |

---

## Phase Details

### Phase 1: SDK Extraction (3-4 days)
**Repo: cgp-sdk**

- [ ] Create repo structure
- [ ] Copy wrapper/, adapters/, utils/ modules from steward-agent-gov-backend
- [ ] Create pyproject.toml with minimal deps
- [ ] Write CGPClient with sync API calls (no batching yet)
- [ ] Write basic quickstart example
- [ ] Test: SDK can send traces to existing backend

### Phase 2: Async Transport (2-3 days)
**Repo: cgp-sdk**

- [ ] Implement AsyncEventQueue (background thread)
- [ ] Implement BatchSender (accumulate, flush)
- [ ] Add retry logic with exponential backoff
- [ ] Add graceful degradation (offline queuing)
- [ ] Test: SDK batches events, handles failures

### Phase 3: Multi-Tenancy Backend (3-4 days)
**Repo: steward-agent-backend**

- [ ] Add Tenant and APIKey SQLAlchemy models
- [ ] Add tenant context middleware
- [ ] Add API key validation middleware
- [ ] Add tenant_id column to existing tables
- [ ] Update all queries with tenant filtering
- [ ] Test: Tenant isolation works

### Phase 4: Ingestion Pipeline (3-4 days)
**Repo: steward-agent-backend**

- [ ] Add batch ingestion endpoint (/v1/ingest/traces)
- [ ] Set up GCP Pub/Sub topic/subscription
- [ ] Implement Pub/Sub consumer worker
- [ ] Add Redis deduplication cache
- [ ] Test: High-volume ingestion works

### Phase 5: GCP Deployment (2-3 days)
**Repo: steward-agent-backend**

- [ ] Write Terraform for Cloud Run
- [ ] Write Terraform for Pub/Sub
- [ ] Write Terraform for Cloud SQL
- [ ] Write Terraform for Redis
- [ ] Set up GitHub Actions CI/CD
- [ ] Deploy and test end-to-end

### Phase 6: Polish & Publish (2-3 days)
**Both repos**

- [ ] SDK documentation
- [ ] Backend API documentation
- [ ] PyPI package publishing
- [ ] Integration tests
- [ ] Example applications

---

## Effort Breakdown

### CGP SDK
| Category | Lines | Status |
|----------|-------|--------|
| Copy existing code | 2,850 | Already written |
| New transport layer | 450 | To write |
| New client + packaging | 500 | To write |
| **Total** | **~3,800** | **75% done** |

### Steward Agent Backend
| Category | Lines | Status |
|----------|-------|--------|
| Existing code | 500KB+ | Working |
| New tenancy module | 500 | To write |
| New ingestion pipeline | 400 | To write |
| New API/middleware | 350 | To write |
| New Terraform | 400 | To write |
| **Total new** | **~1,700** | **10% of total** |

---

## Success Criteria

### SDK
1. Install with `pip install cgp-sdk`
2. Integration requires <20 lines of code
3. Adds <5ms latency to agent execution
4. Works offline - queues events locally

### Backend
1. Handles 1000 traces/sec sustained
2. 99.9% uptime achievable
3. Tenant data isolation verified
4. API response <100ms p95

---

## Security Checklist

- [ ] API keys hashed with SHA-256 + salt
- [ ] TLS enforced for all endpoints
- [ ] Tenant data isolation verified
- [ ] Rate limiting prevents abuse
- [ ] No tenant data in error messages/logs
- [ ] Key rotation mechanism
- [ ] Audit logging for admin actions
- [ ] CORS configuration locked down
