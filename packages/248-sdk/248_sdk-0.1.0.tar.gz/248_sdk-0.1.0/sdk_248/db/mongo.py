"""MongoDB connection and Beanie initialization for the SDK."""

from typing import List, Optional, Type

from beanie import Document, init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


class MongoDBManager:
    """Manages MongoDB connections and Beanie initialization.

    Usage:
        # Option 1: Let the SDK create the client
        from sdk_248 import mongodb, Campaign

        await mongodb.initialize(
            connection_string="mongodb://user:pass@host:27017",
            database_name="mydb"
        )

        # Now use models
        campaigns = await Campaign.find_all().to_list()

        # Option 2: Use your own client
        from motor.motor_asyncio import AsyncIOMotorClient
        from sdk_248 import MongoDBManager, Campaign

        client = AsyncIOMotorClient("mongodb://...")
        manager = MongoDBManager()
        await manager.initialize_with_client(
            client=client,
            database_name="mydb"
        )
    """

    _client: Optional[AsyncIOMotorClient] = None
    _database: Optional[AsyncIOMotorDatabase] = None
    _initialized: bool = False

    def _get_document_models(self) -> List[Type[Document]]:
        """Get all Beanie document models to register.

        Import here to avoid circular imports.
        """
        from sdk_248.models.mongo.campaign import Campaign

        return [Campaign]

    async def initialize(
        self,
        connection_string: str,
        database_name: str,
        document_models: Optional[List[Type[Document]]] = None,
    ) -> None:
        """Initialize MongoDB connection and Beanie ODM.

        Args:
            connection_string: MongoDB connection URI
            database_name: Name of the database to use
            document_models: Optional custom list of document models.
                           If None, uses default SDK models.
        """
        self._client = AsyncIOMotorClient(connection_string)
        self._database = self._client[database_name]

        models = document_models or self._get_document_models()
        await init_beanie(database=self._database, document_models=models)
        self._initialized = True

    async def initialize_with_client(
        self,
        client: AsyncIOMotorClient,
        database_name: str,
        document_models: Optional[List[Type[Document]]] = None,
    ) -> None:
        """Initialize Beanie with an existing MongoDB client.

        Args:
            client: Existing AsyncIOMotorClient instance
            database_name: Name of the database to use
            document_models: Optional custom list of document models
        """
        self._client = client
        self._database = client[database_name]

        models = document_models or self._get_document_models()
        await init_beanie(database=self._database, document_models=models)
        self._initialized = True

    async def close(self) -> None:
        """Close the MongoDB connection."""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None
            self._initialized = False

    @property
    def database(self) -> AsyncIOMotorDatabase:
        """Get the database instance."""
        if not self._initialized:
            raise RuntimeError("MongoDB not initialized. Call initialize() first.")
        return self._database

    @property
    def client(self) -> AsyncIOMotorClient:
        """Get the MongoDB client instance."""
        if not self._initialized:
            raise RuntimeError("MongoDB not initialized. Call initialize() first.")
        return self._client

    @property
    def is_initialized(self) -> bool:
        """Check if the database is initialized."""
        return self._initialized


# Global instance for convenience
mongodb = MongoDBManager()
