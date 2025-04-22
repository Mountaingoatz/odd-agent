"""
Report‑Writer Agent
-------------------
Uses RAG: retrieves the top‑K most relevant chunks from the Chroma
vector DB to ground the memo.

Inputs:
    - data: dict of structured extracts & gaps
    - vectordb: a LangChain VectorStore (Chroma)
Returns:
    - Markdown report string
"""
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from langchain.vectorstores.base import VectorStore

SYS_PROMPT = """
You are a senior Operational Due Diligence analyst.
Write a clear, consultative memo with the sections below.
Where helpful, integrate verbatim quotes from <context>
to support your points.

Sections:
1. Executive Summary
2. Key Risks & Mitigants
3. Open Items / Follow‑Ups
4. Detailed Findings
5. Appendices
Return Markdown only.
"""

def write_report(data: dict, vectordb: VectorStore, k: int = 6) -> str:
    # Build context –  concatenate retrieved docs
    context_docs = vectordb.similarity_search("operational due diligence key risks", k=k)
    context = "\n\n".join(d.page_content for d in context_docs)

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    messages = [
        SystemMessage(content=SYS_PROMPT.replace("<context>", context)),
        HumanMessage(content=str(data)),
    ]
    return llm(messages).content
