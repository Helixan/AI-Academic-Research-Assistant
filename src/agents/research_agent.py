from typing import List
from src.core.llm import LLM
from src.core.vector_store import VectorStore

class ResearchAgent:
    def __init__(self, llm: LLM, vector_store: VectorStore):
        self.llm = llm
        self.vector_store = vector_store

    def find_relevant_papers(self, query: str, top_k: int = 3) -> List[dict]:
        query_embedding = self.llm.get_embedding(query)
        results = self.vector_store.similarity_search(query_embedding, top_k=top_k)
        return results
