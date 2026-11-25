"""
The frontend: a Streamlit dashboard for a business owner.

Paste customer reviews (one per line), click Analyze, and see the results.
This app does NOT call Gemini directly. It calls OUR OWN backend (fastapi_api.py).

Run it (in a SECOND terminal, while fastapi_api.py is also running)
Use any one option to run:
    streamlit run src/app/streamlit_app.py
    python -m streamlit run src/app/streamlit_app.py
    uv run streamlit run src/app/streamlit_app.py
"""

from collections import Counter
import os
from pathlib import Path
import sys

import altair as alt
import requests
import streamlit as st

# Resolve project imports relative to this file, not the process working directory.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Our own database code, kept in a separate file (feedback_dao.py).
from src.dao.feedback_dao import init_db, save_results, load_history, DB_FILE

# The address of our own backend service.
API_URL = os.getenv("ANALYSIS_API_URL", "http://127.0.0.1:8000/analyze")

# Make sure the table exists before the app uses it.
init_db()

st.title("📝 Customer Feedback Analyzer")

uploaded_file = st.file_uploader("Browse for a reviews file", type=["txt"])

if uploaded_file is not None:
    upload_id = f"{uploaded_file.name}:{uploaded_file.size}"
    if st.session_state.get("_loaded_upload_id") != upload_id:
        try:
            st.session_state.reviews_text = uploaded_file.getvalue().decode("utf-8")
            st.session_state._loaded_upload_id = upload_id
        except UnicodeDecodeError:
            st.warning("Please choose a UTF-8 encoded text file.")

st.write("Paste your customer reviews below, one review per line.")
reviews_text = st.text_area("Reviews", height=200, key="reviews_text")

if st.button("Analyze"):
    # Split the text box into separate reviews, ignoring blank lines.
    reviews = [line.strip() for line in reviews_text.split("\n") if line.strip()]

    if not reviews:
        st.warning("Please paste at least one review.")
    else:
        results = []
        # Go through each review and ask our backend to analyze it.
        for review in reviews:
            try:
                response = requests.post(API_URL, json={"text": review}, timeout=30)
                response.raise_for_status()
                data = response.json()
                results.append({
                    "review": review,
                    "label": data["label"],
                    "score": data["score"],
                    "theme": data["theme"],
                    "suggestion": data.get("suggestion", ""),
                })
            except (requests.RequestException, ValueError, KeyError, TypeError):
                # One bad review should not stop the whole batch.
                results.append({
                    "review": review,
                    "label": "error",
                    "score": 0,
                    "theme": "error",
                    "suggestion": "",
                })

        # Save results in session_state so they survive button clicks.
        st.session_state.results = results

# Show the results if we have any.
if "results" in st.session_state:

    results = st.session_state.results

    st.subheader("Results")
    review_filter = st.selectbox(
        "Show reviews",
        ["negative", "positive", "neutral", "all"],
    )
    visible_results = results if review_filter == "all" else [
        result for result in results
        if result["label"] == review_filter
    ]
    st.dataframe(visible_results)

    # ---- A simple summary for the business owner ----
    scores = [r["score"] for r in results if r["label"] != "error"]
    positive = [r for r in results if r["label"] == "positive"]
    themes = [r["theme"] for r in results if r["theme"] != "error"]

    st.subheader("Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Reviews", len(results))
    if scores:
        col2.metric("Average score", round(sum(scores) / len(scores), 1))
        successful_count = len([r for r in results if r["label"] != "error"])
        col3.metric(
            "% Positive",
            f"{round(len(positive) / successful_count * 100)}%"
            if successful_count else "0%",
        )

    if themes:
        # Counter tells us which theme appears most often.
        top_theme = Counter(themes).most_common(1)[0][0]
        st.info(f"Customers talk most about: **{top_theme}**")

    # ---- Save the full report to the database (Lesson 12) ----
    if st.button("💾 Save to database"):
        saved_count = save_results(results)
        if saved_count:
            st.success(f"Saved {saved_count} reviews to {DB_FILE}")
        else:
            st.warning("There are no successful results to save.")

# ---- Show everything we have ever saved (reads from the database) ----
with st.expander("📚 Saved history (all reviews in the database)"):
    history = load_history()
    if history:
        st.write(f"Total saved so far: {len(history)}")
        st.dataframe(
            [{"review": r[0], "label": r[1], "score": r[2], "theme": r[3]} for r in history]
        )
    else:
        st.write("Nothing saved yet. Analyze some reviews and click Save.")

with st.expander("View Reviews As Chart"):
    history = load_history()
    if history:
        theme_counts = Counter(r[3] for r in history if r[3] != "error")
        if theme_counts:
            st.bar_chart(theme_counts)
            pie_chart = alt.Chart(
                alt.Data(
                    values=[
                        {"theme": theme, "reviews": count}
                        for theme, count in theme_counts.items()
                    ]
                )
            ).mark_arc().encode(
                theta=alt.Theta("reviews:Q"),
                color=alt.Color("theme:N", legend=alt.Legend(title="Theme")),
                tooltip=[
                    alt.Tooltip("theme:N", title="Theme"),
                    alt.Tooltip("reviews:Q", title="Reviews"),
                ],
            )
            st.altair_chart(pie_chart, use_container_width=True)
        else:
            st.write("No theme data available yet.")
    else:
        st.write("Nothing saved yet.")
