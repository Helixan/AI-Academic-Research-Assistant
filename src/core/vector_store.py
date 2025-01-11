from typing import Dict, List, Any
import numpy as np

class VectorStore:

    def __init__(self):
        self.docs: Dict[int, Dict[str, Any]] = {}

    def add_document(self, paper_id: int, embedding: List[float], metadata: dict):
        self.docs[paper_id] = {
            "embedding": embedding,
            "metadata": metadata
        }

    def similarity_search(self, query_embedding: List[float], top_k: int = 3) -> List[dict]:
        if not self.docs:
            return []

        similarities = []
        query_vec = np.array(query_embedding)

        for paper_id, entry in self.docs.items():
            doc_vec = np.array(entry["embedding"])
            if np.linalg.norm(doc_vec) == 0 or np.linalg.norm(query_vec) == 0:
                sim_score = 0.0
            else:
                sim_score = float(np.dot(query_vec, doc_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(doc_vec)))
            similarities.append((paper_id, sim_score))

        similarities.sort(key=lambda x: x[1], reverse=True)

        results = []
        for paper_id, score in similarities[:top_k]:
            doc_data = self.docs[paper_id]
            results.append({
                "paper_id": paper_id,
                "score": score,
                "metadata": doc_data["metadata"]
            })
        return results
