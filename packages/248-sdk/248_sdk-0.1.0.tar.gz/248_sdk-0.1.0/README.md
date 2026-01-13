# 248 SDK

Shared SDK for 248 products - MongoDB models, PostgreSQL models, and SmartLead schemas.

## Installation

```bash
# From Git
pip install git+https://github.com/248ai/248-sdk.git

# With PostgreSQL support
pip install "248-sdk[postgres] @ git+https://github.com/248ai/248-sdk.git"

# Local development (editable)
pip install -e .
```

## Quick Start

### MongoDB Models

```python
import asyncio
from sdk_248 import mongodb
from sdk_248.models import Campaign, CampaignStatus

async def main():
    # Initialize MongoDB connection
    await mongodb.initialize(
        connection_string="mongodb://localhost:27017",
        database_name="mydb"
    )

    # Query campaigns
    campaigns = await Campaign.find(
        Campaign.status == CampaignStatus.RUNNING
    ).to_list()

    for campaign in campaigns:
        print(f"Campaign: {campaign.name}")

    # Close connection
    await mongodb.close()

asyncio.run(main())
```

### PostgreSQL Models

```python
from sdk_248 import postgres
from sdk_248.models import Organization

# Initialize PostgreSQL
postgres.initialize(
    connection_string="postgresql://user:pass@localhost:5432/db"
)

# Use sessions
with postgres.session() as session:
    orgs = session.query(Organization).all()
    for org in orgs:
        print(f"Organization: {org.name}")
```

### Using Models Without Database

```python
from sdk_248.models import Lead, CampaignStatus

# Create models for validation/serialization
lead = Lead(
    email="test@example.com",
    first_name="John",
    last_name="Doe"
)

# Serialize to dict
lead_dict = lead.model_dump()

# Use enums
status = CampaignStatus.RUNNING
```

## Available Exports

### From `sdk_248`
- `MongoDBManager`, `mongodb` - MongoDB connection management
- `PostgresManager`, `postgres`, `Base` - PostgreSQL connection management

### From `sdk_248.models`

#### Enums
- `CampaignStatus` - Campaign status values
- `EmailOrchestrator` - Email orchestrator options
- `AppType` - Application types
- `NodeType` - Node types for responder actions
- `ActionRunStatus` - Action run status values
- `CategoriserStatus` - Categoriser status values

#### MongoDB Models
- `Campaign` - Main campaign document (Beanie)
- `Lead` - Lead embedded model
- `ActionRun` - Action run embedded model
- `Node` - Responder node model

#### PostgreSQL Models
- `Organization` - Organization entity
- `OrganizationStatus` - Organization status enum

### From `sdk_248.schemas`
- `CampaignSequenceInput` - Campaign sequence configuration
- `CampaignReplyWebhookSchema` - Reply webhook payload
- `EmailSentWebhookSchema` - Email sent webhook payload
- `Organization` - Organization response schema (Pydantic)
- `OrganizationCreate` - Organization create schema
- `OrganizationUpdate` - Organization update schema
