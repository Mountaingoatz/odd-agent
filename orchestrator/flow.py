"""
Prefect flow orchestrating:
  1. ADV pull  2. Doc classification  3. Parsing
  4. Vector‑store embedding  5. Gap check  6. Report
"""
from __future__ import annotations
from prefect import flow, task
from typing import List
import tempfile, pathlib, os

from ingest.sec_ingest import fetch_adv
from agents.doc_classifier import classify
from agents.extractor_agent import parse_pdf
from agents.gap_analyzer import find_gaps
from agents.report_writer import write_report

# Vector store + embeddings
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader

EMBED_MODEL = OpenAIEmbeddings()

@task
def ingest_adv(crd: str):
    return fetch_adv(crd)

@task
def classify_and_parse(path: str):
    first_page = PyPDFLoader(path).load()[0].page_content
    doc_type = classify(path, first_page)
    parsed = parse_pdf.run({"pdf_path": path, "doc_type": doc_type})
    return {"type": doc_type, "parsed": parsed, "path": path}

@task
def build_vectordb(paths: List[str]) -> Chroma:
    docs = []
    for p in paths:
        docs.extend(PyPDFLoader(p).load())
    vectordb = Chroma.from_documents(docs, EMBED_MODEL, persist_directory="chroma_db")
    return vectordb

@flow
def odd_pipeline(crd: str, pdf_paths: List[str] | None = None) -> str:
    adv_data = ingest_adv(crd)

    pdf_paths = pdf_paths or []
    parsed_docs = [classify_and_parse(p) for p in pdf_paths]

    vectordb = build_vectordb(pdf_paths) if pdf_paths else Chroma.from_documents([], EMBED_MODEL)

    gaps = find_gaps({p["type"]: p["parsed"] for p in parsed_docs})
    report = write_report({"adv": adv_data, "docs": parsed_docs, "gaps": gaps}, vectordb)
    return report
