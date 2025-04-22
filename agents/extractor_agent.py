"""
Extractor Agent
---------------
• For *Financial Statement* PDFs: pulls Expense line‑items from the
  Income Statement and returns them as structured JSON.
• For other docs we simply return basic stats (page‑count, size).

Relies only on pdfplumber (keeps docker image slim).
"""

import pdfplumber, re, json, pathlib
from typing import List, Dict, Any

CURRENCY_RE = re.compile(
    r"([A-Z]?[\\$€£])?\\s*([-+]?[0-9]{1,3}(?:[,0-9]{3})*(?:\\.[0-9]{2})?)",
    re.I,
)

def _clean_amount(raw: str) -> float | None:
    """Strip commas / symbols and convert to float."""
    raw = raw.replace(",", "").replace("$", "").replace("€", "").replace("£", "").strip()
    try:
        return float(raw)
    except ValueError:
        return None

def extract_expenses(pdf_path: str) -> Dict[str, Any]:
    expenses: List[Dict[str, Any]] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            # stop scanning after 4 pages –  most INCO statements are near front
            if page.page_number > 4:
                break
            if "statement of operations" in text.lower() or "income statement" in text.lower():
                lines = text.splitlines()
                for ln in lines:
                    if "expense" in ln.lower():
                        cols = ln.split()
                        # grab last token that matches a number
                        for token in reversed(cols):
                            m = CURRENCY_RE.search(token)
                            if m:
                                amt = _clean_amount(m.group(2))
                                if amt is not None:
                                    expenses.append({"description": ln.strip(), "amount": amt})
                                break
    return {"expenses": expenses, "source_pages": len(expenses)}

def generic_stats(pdf_path: str) -> Dict[str, Any]:
    with pdfplumber.open(pdf_path) as pdf:
        return {"pages": len(pdf.pages), "filename": pathlib.Path(pdf_path).name}

# ------------------------------------------------------------------
# LangChain‑compatible TOOL wrapper
# ------------------------------------------------------------------
from langchain.tools import tool

@tool
def parse_pdf(pdf_path: str, doc_type: str = "Other") -> dict:
    """
    Parse a PDF; behavior depends on doc_type.
    Returns JSON.
    """
    if doc_type == "Financial Statement":
        return extract_expenses(pdf_path)
    return generic_stats(pdf_path)
