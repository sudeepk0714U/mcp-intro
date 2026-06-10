# scout/memory/episodic.py

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct
)

from .embeddings import create_embedding

import uuid
from datetime import datetime


class EpisodicMemory:

    def __init__(self):

        self.collection_name = "episodes"

        self.client = QdrantClient(
            host="localhost",
            port=6333
        )

        self._create_collection()

    def _create_collection(self):

        collections = self.client.get_collections().collections

        names = [c.name for c in collections]

        if self.collection_name not in names:

            self.client.create_collection(
                collection_name=self.collection_name,

                vectors_config=VectorParams(
                    size=1536,
                    distance=Distance.COSINE
                )
            )

    def store_episode(
        self,
        task,
        error,
        actions,
        outcome,
        success=True,
        metadata=None
    ):

        text = f"""
        Task: {task}

        Error: {error}

        Actions:
        {' '.join(actions)}

        Outcome:
        {outcome}
        """

        embedding = create_embedding(text)

        point = PointStruct(
            id=str(uuid.uuid4()),

            vector=embedding,

            payload={
                "task": task,
                "error": error,
                "actions": actions,
                "outcome": outcome,
                "success": success,
                "metadata": metadata or {},
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )

    def search_similar(
        self,
        query,
        limit=5
    ):

        embedding = create_embedding(query)

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=embedding,
            limit=limit
        ).points

        return [r.payload for r in results]