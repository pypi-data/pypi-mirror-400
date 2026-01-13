"""248 SDK - Shared models and utilities for 248 products.

Usage:
    from sdk_248 import mongodb, postgres
    from sdk_248.models import Campaign, CampaignStatus

    # Initialize MongoDB
    await mongodb.initialize(
        connection_string="mongodb://localhost:27017",
        database_name="mydb"
    )

    # Use models
    campaigns = await Campaign.find(
        Campaign.status == CampaignStatus.RUNNING
    ).to_list()
"""

__version__ = "0.1.0"

# Database managers
from sdk_248.db.mongo import MongoDBManager, mongodb
from sdk_248.db.postgres import Base, PostgresManager, postgres

__all__ = [
    # Version
    "__version__",
    # Database managers
    "MongoDBManager",
    "mongodb",
    "PostgresManager",
    "postgres",
    "Base",
]
