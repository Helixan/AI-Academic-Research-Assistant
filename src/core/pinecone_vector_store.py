from typing import List, Dict, Any
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec

class PineconeVectorStore:
    def __init__(
        self,
        api_key: str,
        index_name: str,
        dimension: int = 1536,
        metric: str = "cosine",
        cloud: str = "aws",
        region: str = "us-east-1"
    ):

        self.pc = Pinecone(api_key=api_key)

        existing_indexes = self.pc.list_indexes().names()
        if index_name not in existing_indexes:
            self.pc.create_index(
                name=index_name,
                dimension=dimension,
                metric=metric,
                spec=ServerlessSpec(
                    cloud=cloud,
                    region=region
                )
            )

        self.index = self.pc.Index(index_name)

    def add_document(self, paper_id: int, embedding: List[float], metadata: dict):
        self.index.upsert(vectors=[(str(paper_id), embedding, metadata)])

    def similarity_search(self, query_embedding: List[float], top_k: int = 3) -> List[dict]:
        response = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        if not response.matches:
            return []

        results = []
        for match in response.matches:
            results.append({
                "paper_id": match.id,
                "score": match.score,
                "metadata": match.metadata,
            })
        return results
