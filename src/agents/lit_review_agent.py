import logging
from typing import List, Dict, Any
from langchain.llms import OpenAI
from langchain.utilities import ArxivAPIWrapper

from src.core.llm import LLM
from src.core.vector_store import VectorStore

logger = logging.getLogger(__name__)

class LitReviewAgent:

    def __init__(
        self,
        llm: LLM,
        vector_store: VectorStore,
        openai_api_key: str,
        temperature: float = 0.7
    ):
        self.llm = llm
        self.vector_store = vector_store
        self.openai_api_key = openai_api_key

        self.langchain_llm = OpenAI(
            openai_api_key=openai_api_key,
            temperature=temperature
        )
        self.arxiv_tool = ArxivAPIWrapper()

    def recommend_local_papers(self, text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        logger.info("Generating embedding for input text to find relevant local papers...")
        query_embedding = self.llm.get_embedding(text)
        results = self.vector_store.similarity_search(query_embedding, top_k=top_k)
        logger.info(f"Found {len(results)} local paper(s) as candidates.")
        return results

    def recommend_external_papers(self, text: str, max_results: int = 3) -> List[Dict[str, Any]]:
        logger.info(f"Querying Arxiv for text: '{text}' (max_results={max_results})")
        search_results = self.arxiv_tool.run(text)

        external_papers = []
        for entry in search_results.split("\n\n"):
            if entry.strip() == "":
                continue
            paper_info = {}
            lines = entry.split("\n")
            for line in lines:
                if line.startswith("Title: "):
                    paper_info["title"] = line.replace("Title: ", "").strip()
                elif line.startswith("Authors: "):
                    paper_info["authors"] = line.replace("Authors: ", "").strip()
                elif line.startswith("Abstract: "):
                    paper_info["abstract"] = line.replace("Abstract: ", "").strip()
                elif line.startswith("Published: "):
                    paper_info["published"] = line.replace("Published: ", "").strip()
                elif line.startswith("URL: "):
                    paper_info["url"] = line.replace("URL: ", "").strip()
            if paper_info:
                external_papers.append(paper_info)
                if len(external_papers) >= max_results:
                    break

        logger.info(f"Retrieved {len(external_papers)} external paper(s) from Arxiv.")
        return external_papers

    def rank_papers_by_relevance(self, user_text: str, candidates: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        query_embedding = self.llm.get_embedding(user_text)
        ranked_papers = []

        for candidate in candidates:
            candidate_text = candidate.get("abstract", "") or candidate.get("title", "")
            candidate_embedding = self.llm.get_embedding(candidate_text)
            sim_score = self.cosine_similarity(query_embedding, candidate_embedding)
            candidate["similarity_score"] = sim_score
            ranked_papers.append(candidate)

        ranked_papers.sort(key=lambda x: x.get("similarity_score", 0), reverse=True)
        return ranked_papers[:top_k]

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        from numpy import dot
        from numpy.linalg import norm
        return dot(vec1, vec2) / (norm(vec1) * norm(vec2)) if norm(vec1) and norm(vec2) else 0.0

    def explain_relevance(self, user_text: str, candidate_text: str) -> str:
        prompt = f"""
        The user is researching: {user_text}

        Below is a paper abstract or summary:
        {candidate_text}

        Briefly explain why this paper might be relevant 
        to the user's research. Provide a concise paragraph.
        """
        explanation = self.langchain_llm(prompt)
        return explanation.strip()
