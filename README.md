# 📊 Operational Due Diligence (ODD) Agent

A one-click pipeline that ingests public filings and internal documents, classifies them, extracts key facts (e.g., expense lines), grounds an LLM with a retrieval-augmented-generation (RAG) knowledge base, and produces a senior-ready memo.  
Everything runs in Docker, so you can spin it up with **zero local setup**.

---

## 🚀 Quick Start

```bash
# 1  Clone the repo
git clone https://github.com/Mountaingoatz/odd-agent.git
cd odd-agent

# 2  Create a .env file with your API keys
cp .env.example .env
# Edit .env with your actual API keys

# 3  Build & run
docker compose up --build
```

Open <http://localhost:8501>  
* Enter a **CRD** number.  
* (Optional) drag-and-drop one or more PDFs.  
* Click **Run ODD Agent 🚀**.

You'll see file categories, any expenses parsed from financial statements, and a full Markdown memo (downloadable).

---

## 🏗️  High-Level Architecture

```
 ┌───────────────┐  upload PDFs    ┌──────────────┐
 │  Streamlit UI ├────────────────►│ Prefect Flow │───► SEC / News APIs
 └───────────────┘                 └──────┬───────┘
                                          ▼
          Chroma Vector DB  ◄───── Embeddings (OpenAI)
                                          ▼
                 LangGraph Agents (Classifier ▸ Extractor ▸ Gap-Analyzer ▸ Writer)
```

All components live in one Docker service; swap them out as you scale.

---

## 📂  Directory Layout

```
ingest/              pull external data (ADV, 13F)
agents/
   ├─ doc_classifier.py       # categorises docs
   ├─ extractor_agent.py      # parses PDFs (expense lines, etc.)
   ├─ gap_analyzer.py         # compares answers vs. checklist.json
   └─ report_writer.py        # RAG-grounded memo generator
orchestrator/        Prefect flow tying it all together
app/                 Streamlit front-end
checklist.json       your firm's ODD questionnaire
requirements.txt     python deps (installed inside container)
Dockerfile
docker-compose.yml
README.md            (this file)
```

---

## ⚙️  Environment Variables

| Var | Required | Purpose |
|-----|----------|---------|
|`OPENAI_API_KEY`|✅|Embeddings + GPT-4o for memo generation|
|`SEC_API_KEY`|✅|sec-api.io ADV + 13F endpoints|
|`NEWS_API_KEY`|optional|enables future news-scrape scripts|

Set them in your shell or create a **`.env`** file (Docker Compose loads it automatically).

---

## 🔧  How to Customise

### 1 .  Change what gets extracted  
**File:** `agents/extractor_agent.py`

* **Add a new doc-type**  
  1. Extend the `if doc_type == ...` branch.  
  2. Write a helper that scans pages and returns the structure you need.  
* **Tweak expense logic**  
  * Update `CURRENCY_RE` if you need different currency symbols or decimal formats.  
  * Raise / lower the `page.page_number > 4` cutoff.

### 2 .  Re-label or add document categories  
**File:** `agents/doc_classifier.py`

* Edit the `_KEYWORDS` dictionary.  
  *Keys are categories*, *values are regex tuples*.  
  Eg. to catch ESG reports:

```python
_KEYWORDS["ESG Report"] = (r"\besg\b", r"sustainability report")
```

### 3 .  Update the ODD questionnaire  
**File:** `checklist.json`

Plain JSON with `"sections" → "questions"`.  
The Gap-Analyzer flags anything not answered by the agents.

### 4 .  Change memo structure / tone  
**File:** `agents/report_writer.py`

* Adapt `SYS_PROMPT` to reorder sections, add style guides, or change tone.  
* Increase `k` in `write_report()` to retrieve more context documents.  
* Swap `gpt-4o-mini` for any OpenAI model you prefer (or use the Assistants API).

### 5 .  Swap vector store  
Currently using **Chroma (local, persisted in `./chroma_db`)**.

*Self-host*: nothing to change.  
*Cloud (Pinecone, Weaviate, etc.):*

1. `pip install` that provider's client.  
2. Replace the `build_vectordb()` function in `orchestrator/flow.py` with the relevant constructor; pass API keys via env vars.

### 6 .  Expand the dashboard  
**File:** `app/streamlit_app.py`

* Add new tabs / charts with `st.tabs()` or `st.altair_chart()`.  
* Use Streamlit Session State if you need multi-page workflows.  
* For richer visuals (e.g., Gantt), pull Plotly or Altair—just add to `requirements.txt` and rebuild the container.

### 7 .  Schedule automated runs  
**File:** `orchestrator/flow.py`

Prefect already wraps the pipeline—register the flow in Prefect Cloud or a Prefect Server, then add a Deployment with a cron schedule (e.g., every Monday pull fresh filings).

---

## 🧩  Adding a Brand-New Agent

1. Create `agents/new_agent.py` with a LangChain `@tool` or simple function.  
2. Import & call it from `orchestrator/flow.py` at the correct step.  
3. Feed its output into `write_report()` (add another key in the `data` dict).

---

## 🐳  Docker Tips

* **Rebuild after dependency changes**

```bash
docker compose build
```

* **Persist Chroma outside the container**

Edit `docker-compose.yml`:

```yaml
volumes:
  - ./local_chroma:/app/chroma_db
```

* **Debug inside the container**

```bash
docker compose exec odd_agent bash
python             # open REPL, run modules, etc.
```

---

## 🛠️  Troubleshooting

| Symptom | Fix |
|---------|-----|
|`ModuleNotFoundError` after editing deps|`docker compose build` again|
|"OpenAI quota exceeded"|Check usage & billing; reduce doc size or temperature|
|PDF parsed but no expenses found|Verify the statement actually contains "Income Statement / Statement of Operations" on the first four pages; update regexes |
|Chroma errors on start|Delete `./chroma_db` (schema mismatch) or bump Chroma version|

---

## 📜  License

For internal due-diligence prototyping only.  
You're responsible for compliance with SEC and data-privacy rules when running on live manager documents.

---
