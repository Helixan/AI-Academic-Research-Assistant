from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
import logging

from src.database.database import get_db
from src.database import crud
from src.api.schemas.paper import Paper, PaperCreate
from src.parsers.pdf_parser import extract_text_from_pdf
from src.agents.summarizer_agent import SummarizerAgent
from src.agents.research_agent import ResearchAgent
from src.agents.lit_review_agent import LitReviewAgent
from src.core.llm import LLM
from src.core.vector_store import VectorStore
from src.core.pinecone_vector_store import PineconeVectorStore
from src.utils.config import load_config

router = APIRouter()
logger = logging.getLogger(__name__)

config = load_config()

global_llm = LLM(api_key=os.getenv("OPENAI_API_KEY", ""))

if config.get("vector_store", {}).get("type") == "pinecone":
    global_vector_store = PineconeVectorStore(
        api_key=config["vector_store"]["api_key"],
        index_name=config["vector_store"].get("index_name", "my-index"),
        dimension=1536,
        metric="cosine",
        cloud="aws",
        region=config["vector_store"].get("environment", "us-east-1"),
    )
else:
    global_vector_store = VectorStore()

summarizer_agent = SummarizerAgent(llm=global_llm)
research_agent = ResearchAgent(llm=global_llm, vector_store=global_vector_store)
lit_review_agent = LitReviewAgent(
    llm=global_llm,
    vector_store=global_vector_store,
    openai_api_key=os.getenv("OPENAI_API_KEY", ""),
    temperature=0.7
)

@router.get("/", response_model=List[Paper])
def get_papers(db: Session = Depends(get_db)):
    papers = crud.get_all_papers(db)
    logger.debug(f"Retrieved {len(papers)} papers from the database.")
    return papers

@router.get("/search")
def search_papers(query: str, top_k: int = 3):
    results = research_agent.find_relevant_papers(query, top_k=top_k)
    logger.debug(f"Search query: '{query}', top_k={top_k}, results_found={len(results)}.")
    return {"results": results}

@router.post("/", response_model=Paper)
def upload_paper(
    title: str = Form(...),
    abstract: str = Form(""),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    file_ext = os.path.splitext(file.filename)[1]
    random_filename = f"{uuid.uuid4()}{file_ext}"
    raw_path = os.path.join("data", "raw", random_filename)

    with open(raw_path, "wb") as f:
        f.write(file.file.read())

    logger.info(f"File '{file.filename}' saved to '{raw_path}'.")
    content = extract_text_from_pdf(raw_path)

    new_paper = PaperCreate(title=title, abstract=abstract, content=content)
    db_paper = crud.create_paper(db, new_paper)

    paper_embedding = global_llm.get_embedding(content)
    global_vector_store.add_document(
        paper_id=db_paper.id,
        embedding=paper_embedding,
        metadata={"title": title, "abstract": abstract}
    )
    logger.info(f"Paper '{db_paper.title}' (ID: {db_paper.id}) embedded and saved.")
    return db_paper

@router.get("/{paper_id}", response_model=Paper)
def get_paper(paper_id: int, db: Session = Depends(get_db)):
    paper = crud.get_paper_by_id(db, paper_id)
    if not paper:
        logger.warning(f"Paper with ID {paper_id} not found.")
        raise HTTPException(status_code=404, detail="Paper not found.")
    return paper

@router.post("/summarize/{paper_id}")
def summarize_paper(paper_id: int, db: Session = Depends(get_db)):
    paper = crud.get_paper_by_id(db, paper_id)
    if not paper:
        logger.warning(f"Paper with ID {paper_id} not found. Cannot summarize.")
        raise HTTPException(status_code=404, detail="Paper not found.")
    summary = summarizer_agent.summarize_text(paper.content or "")
    logger.debug(f"Summary for paper ID {paper_id}: {summary}")
    return {"summary": summary}


@router.post("/literature_review/local")
def literature_review_local(payload: dict):
    topic = payload.get("topic", "").strip()
    top_k = payload.get("top_k", 5)

    if not topic:
        logger.error("Literature review local: 'topic' is required.")
        raise HTTPException(status_code=400, detail="'topic' is required.")

    logger.debug(f"Performing local literature review for topic='{topic}' with top_k={top_k}.")
    results = lit_review_agent.recommend_local_papers(text=topic, top_k=top_k)
    return {"topic": topic, "results": results}


@router.post("/literature_review/external")
def literature_review_external(payload: dict):
    topic = payload.get("topic", "").strip()
    max_results = payload.get("max_results", 3)

    if not topic:
        logger.error("Literature review external: 'topic' is required.")
        raise HTTPException(status_code=400, detail="'topic' is required.")

    logger.debug(f"Performing external literature review for topic='{topic}' with max_results={max_results}.")
    external_refs = lit_review_agent.recommend_external_papers(text=topic, max_results=max_results)

    return {"topic": topic, "external_refs": external_refs}


@router.post("/literature_review/full")
def literature_review_full(payload: dict):
    topic = payload.get("topic", "").strip()
    top_k_local = payload.get("top_k_local", 5)
    max_results_external = payload.get("max_results_external", 3)

    if not topic:
        logger.error("Literature review full: 'topic' is required.")
        raise HTTPException(status_code=400, detail="'topic' is required.")

    logger.debug(f"Performing full literature review for topic='{topic}'.")
    local_results = lit_review_agent.recommend_local_papers(text=topic, top_k=top_k_local)
    external_results = lit_review_agent.recommend_external_papers(text=topic, max_results=max_results_external)

    ranked_external = lit_review_agent.rank_papers_by_relevance(user_text=topic, candidates=external_results,
                                                                top_k=max_results_external)
    return {
        "topic": topic,
        "local_results": local_results,
        "external_results": ranked_external
    }
