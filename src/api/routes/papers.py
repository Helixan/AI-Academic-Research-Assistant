from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import List
import os
import uuid

from src.database.database import get_db
from src.database import crud
from src.api.schemas.paper import Paper, PaperCreate
from src.parsers.pdf_parser import extract_text_from_pdf
from src.agents.summarizer_agent import SummarizerAgent
from src.agents.research_agent import ResearchAgent
from src.core.llm import LLM
from src.core.vector_store import VectorStore
from src.core.pinecone_vector_store import PineconeVectorStore
from src.utils.config import load_config

router = APIRouter()

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

@router.get("/", response_model=List[Paper])
def get_papers(db: Session = Depends(get_db)):
    papers = crud.get_all_papers(db)
    return papers

@router.get("/search")
def search_papers(query: str, top_k: int = 3):
    results = research_agent.find_relevant_papers(query, top_k=top_k)
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

    content = extract_text_from_pdf(raw_path)

    new_paper = PaperCreate(title=title, abstract=abstract, content=content)
    db_paper = crud.create_paper(db, new_paper)

    paper_embedding = global_llm.get_embedding(content)
    global_vector_store.add_document(
        paper_id=db_paper.id,
        embedding=paper_embedding,
        metadata={"title": title, "abstract": abstract}
    )
    return db_paper

@router.get("/{paper_id}", response_model=Paper)
def get_paper(paper_id: int, db: Session = Depends(get_db)):
    paper = crud.get_paper_by_id(db, paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")
    return paper

@router.post("/summarize/{paper_id}")
def summarize_paper(paper_id: int, db: Session = Depends(get_db)):
    paper = crud.get_paper_by_id(db, paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")
    summary = summarizer_agent.summarize_text(paper.content or "")
    return {"summary": summary}
