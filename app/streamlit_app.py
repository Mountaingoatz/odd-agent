"""
Streamlit UI
------------
• Multi‑file upload (optional) – if none, pipeline runs on CRD only.
• Shows classification table, extracted expense table, and full memo.
"""
import streamlit as st, tempfile, os, json, pandas as pd
from orchestrator.flow import odd_pipeline
from agents.doc_classifier import classify
from agents.extractor_agent import extract_expenses

st.set_page_config(page_title="ODD Agent", layout="wide", page_icon="📊")
st.title("📊 Operational Due Diligence Agent")

# -------------------------------------------------
# Inputs
# -------------------------------------------------
with st.sidebar:
    crd = st.text_input("Manager CRD", value="106176")
    uploaded_files = st.file_uploader("Upload supporting PDFs (optional)",
                                      type=["pdf"], accept_multiple_files=True)
    run_btn = st.button("Run ODD Agent 🚀")

# -------------------------------------------------
# Run pipeline
# -------------------------------------------------
if run_btn:
    temp_paths = []
    for up in uploaded_files or []:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp.write(up.read()); tmp.close()
        temp_paths.append(tmp.name)

    with st.spinner("Running full pipeline… this might take a minute"):
        report_md = odd_pipeline(crd, temp_paths)

    # -------------------------------------------------
    # Display results
    # -------------------------------------------------
    st.success("Pipeline complete!")

    # 1. Doc classification overview
    if temp_paths:
        cats = [{"File": os.path.basename(p),
                 "Category": classify(p, None)} for p in temp_paths]
        st.subheader("📂 Document Categories")
        st.table(pd.DataFrame(cats))

        # 2. Expense extraction preview
        exp_rows = []
        for p in temp_paths:
            if classify(p, None) == "Financial Statement":
                parsed = extract_expenses(p)
                for row in parsed["expenses"]:
                    exp_rows.append({"File": os.path.basename(p),
                                     "Line": row["description"][:60],
                                     "Amount": row["amount"]})
        if exp_rows:
            st.subheader("💸 Extracted Expense Lines")
            st.table(pd.DataFrame(exp_rows))

    # 3. Memo (Markdown) – in an expander with download option
    st.subheader("📝 Draft Memo")
    st.markdown(report_md)
    st.download_button("📥 Download Markdown", report_md,
                       file_name="ODD_Report.md", mime="text/markdown")
