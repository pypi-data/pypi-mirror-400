# Empirica CRM

Client Relationship Management module for Empirica.

Enables **relational epistemics** - tracking what AI knows about entities (clients) separate from tasks (goals).

## Prerequisites

- Python 3.9+
- Empirica framework (`pip install empirica` or from source)

## Installation

```bash
# Install from source (development)
pip install -e .

# Or install directly
pip install empirica-crm
```

**Note:** Empirica CRM extends the Empirica framework. Ensure you have Empirica installed first:

```bash
pip install empirica>=1.0.0
```

## Quick Start

### 1. Create a Client

```bash
empirica crm client-create \
  --name "Acme Corp" \
  --type prospect \
  --industry "Enterprise Software" \
  --description "Potential partner for API integration"
```

### 2. Add an Engagement

```bash
empirica crm engagement-create \
  --client-id <client-id> \
  --title "Partnership Discussion" \
  --type outreach
```

### 3. Log Interactions

```bash
empirica crm interaction-log \
  --client-id <client-id> \
  --type email \
  --summary "Initial outreach email sent"
```

### 4. Capture Knowledge

```bash
# Log what you learned
empirica crm memory-log-finding \
  --client-id <client-id> \
  --finding "They use Kubernetes for all deployments"

# Log what you need to learn
empirica crm memory-log-unknown \
  --client-id <client-id> \
  --unknown "What's their Q2 budget?"
```

### 5. Get Full Context

```bash
empirica crm client-bootstrap --client-id <client-id>
```

Returns everything an AI needs: client details, active engagements, memory (findings/unknowns), recent interactions, and suggested next actions.

## CLI Commands

| Command | Description |
|---------|-------------|
| `client-create` | Create a new client |
| `client-list` | List all clients |
| `client-show` | Show client details |
| `client-update` | Update client fields |
| `client-bootstrap` | Get full AI context |
| `engagement-create` | Start a new engagement |
| `engagement-list` | List engagements |
| `engagement-update` | Update engagement status |
| `interaction-log` | Log an interaction |
| `memory-log-finding` | Log a finding |
| `memory-log-unknown` | Log an unknown |
| `memory-search` | Search client memory |
| `metrics-show` | Show client metrics |

## Python API

```python
from empirica_crm import (
    create_client,
    get_client,
    list_clients,
    create_engagement,
    log_interaction,
)

# Create client
client = create_client(
    name="42.works",
    description="AI advertising platform",
    client_type="prospect",
    industry="AdTech",
    tags=["ai", "advertising"],
)

# Create engagement
engagement = create_engagement(
    client_id=client.client_id,
    title="Technical Partnership",
    engagement_type="outreach",
)

# Log interaction
log_interaction(
    client_id=client.client_id,
    interaction_type="email",
    summary="Sent partnership proposal",
)
```

## Documentation

- [User Guide](docs/guides/USER_GUIDE.md) - Comprehensive guide for humans and AIs
- [API Reference](docs/reference/API_REFERENCE.md) - Full CLI and Python API documentation
- [Module Design](docs/design/CRM_MODULE_DESIGN.md) - Architecture and design decisions

## Architecture

```
empirica_crm/
├── __init__.py           # Package exports + plugin registration
├── schema.py             # CRM database tables
├── client_store.py       # Client CRUD operations
├── engagement_store.py   # Engagement management
├── interaction_store.py  # Interaction logging
├── client_memory.py      # Semantic memory (Qdrant-backed)
├── memory_backend.py     # Memory storage abstraction
├── epistemic_metrics.py  # Relationship health scoring
└── cli/
    ├── commands.py       # Command facade (re-exports handlers)
    └── handlers/         # Domain-specific command handlers
```

## Database

CRM extends Empirica's `sessions.db` with these tables:

| Table | Purpose |
|-------|---------|
| `clients` | Persistent client relationships |
| `engagements` | Time-bounded client interactions |
| `interactions` | Activity log (emails, calls, meetings) |
| `client_memory` | SQLite fallback for memory items |

Memory is also stored in Qdrant for semantic search when available.

## Dependencies

- `empirica>=1.0.0` - Core Empirica framework (required)
- `qdrant-client` - For semantic memory search (optional)

## License

[Business Source License 1.1](LICENSE)

- **Free for:** Internal use, non-production use, self-hosted deployments
- **Restricted:** Offering as a competing managed/cloud service
- **Converts to:** Apache 2.0 on January 1, 2029
