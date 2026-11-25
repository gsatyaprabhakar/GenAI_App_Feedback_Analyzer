# Project 1: Customer Feedback Analyzer (Gen AI)

**The problem:** A restaurant owner has dozens of customer reviews and no time to read them all. They want a simple tool: paste the reviews, click a button, and instantly see how customers feel and what they keep complaining about.

**What you will build:**
- A **backend** (FastAPI) that uses Gemini to analyze one review.
- A **frontend** (Streamlit dashboard) Owner actually clicks on. It sends every review to backend and shows a summary.

---

## Step 1: Set up the project

```bash
uv init 11_project_feedback_analyzer
cd 11_project_feedback_analyzer
uv add "fastapi[standard]" google-genai python-dotenv pydantic streamlit requests
```

Put your Gemini key in a `.env` file:
```
GOOGLE_API_KEY=your_key_here
```

Install dependencies from the project root:
```bash
python -m pip install -r requirements.txt
```

---

## Step 2: The backend (`src/api/fastapi_api.py`)

This is a sentiment API.

The full code is in `src/api/fastapi_api.py`. The important part is the answer shape:

```python
class Analysis(BaseModel):
    label: str   # "positive", "negative", or "neutral"
    score: int   # 1 (very bad) to 5 (very good)
    theme: str   # one word, e.g. "delivery"
```

Run the backend in its **own terminal** and leave it running:

```bash
uv run fastapi dev src/api/fastapi_api.py
```

Quick test: open **http://127.0.0.1:8000/docs**, try `/analyze` with a review, and confirm you get back a label, score, and theme.

---

## Step 3: The frontend (`src/app/streamlit_app.py`)

Open a **second terminal** (keep the backend running in the first one) and run:

```bash
uv run streamlit run src/app/streamlit_app.py
```

Paste a few reviews (one per line) and click **Analyze**. You can copy test reviews from `sample_reviews.txt`.

The key idea in the frontend is this loop. For each review, we call our own backend and collect the answer:

```python
for review in reviews:
    try:
        response = requests.post(API_URL, json={"text": review})
        data = response.json()
        results.append({
            "review": review,
            "label": data["label"],
            "score": data["score"],
            "theme": data["theme"],
        })
    except Exception:
        # one bad review should not stop the whole batch
        results.append({"review": review, "label": "error", "score": 0, "theme": "error"})
```

Then we build a small summary the owner cares about: how many reviews, the average score, the percent that are positive, and the single theme people mention most. Finally, a **Save to database** button writes every review into a SQLite table (`feedback.db`), and a **Saved history** section reads them all back.

---

## Step 4: Keep code tidy (`database.py`)

When a file gets long, we split it. All the database code (create table, save, load) lives in its own file, **`src/dao/feedback_dao.py`**. Then `streamlit_app.py` imports it at the top:

```python
from src.dao.feedback_dao import init_db, save_results, load_history, DB_FILE
```

---

## How to run the whole thing (two terminals)

| Terminal 1 (backend)								|  Terminal 2 (frontend)								|
|---------------------------------------------------|-------------------------------------------------------|
|  fastapi dev src/api/fastapi_api.py				|  streamlit run src/app/streamlit_app.py 				|
|  stays running									|  opens in your browser								|

If the frontend shows "error" rows, the most common reason is that the backend is not running. Start it first.

---

## Other option to run the whole thing (two terminals)

| Terminal 1 (backend)								|  Terminal 2 (frontend)								|
|---------------------------------------------------|-------------------------------------------------------|
|  python -m fastapi dev src/api/fastapi_api.py		|  python -m streamlit run src/app/streamlit_app.py 	|
|  uv run fastapi dev src/api/fastapi_api.py		|  uv run streamlit run src/app/streamlit_app.py 		|

