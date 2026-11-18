"""CaneMitra chat UI (Day 10).

Run from the repository root:
    uvicorn app.main:app --reload          (terminal 1, the API)
    streamlit run ui/app.py                (terminal 2, this UI)

Features:
  * chat that calls the API's /ask or /agent endpoint
  * shows citations (sources) under each answer
  * thumbs up / thumbs down saved to data/feedback.jsonl
  * season timeline bar: planting, fertiliser splits, harvest window
"""

import os
import sys
from datetime import date
from pathlib import Path

import altair as alt
import pandas as pd
import requests
import streamlit as st

# Make "from ui.xxx import ..." work when started with `streamlit run ui/app.py`.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ui.feedback import save_feedback  # noqa: E402
from ui.timeline import SEASONS, build_timeline  # noqa: E402

DEFAULT_API_URL = os.getenv("CANEMITRA_API_URL", "http://127.0.0.1:8000")
QUESTION_FIELD = "question"  # change if your /ask or /agent expects another key

STAGE_COLORS = {
    "planting": "#2e7d32",
    "fertiliser": "#f9a825",
    "growth": "#9ccc65",
    "harvest": "#e65100",
}

st.set_page_config(page_title="CaneMitra", page_icon="🌾", layout="wide")


# ---------------------------------------------------------------- API call
def call_api(api_url: str, endpoint: str, question: str) -> dict:
    """POST the question and return the parsed reply as a small dict."""
    url = f"{api_url.rstrip('/')}/{endpoint}"
    try:
        resp = requests.post(url, json={QUESTION_FIELD: question}, timeout=60)
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.ConnectionError:
        return {"error": f"Cannot reach the API at {api_url}. Start it with: uvicorn app.main:app --reload"}
    except requests.exceptions.Timeout:
        return {"error": "The API took more than 60 seconds. Try again."}
    except requests.exceptions.HTTPError as e:
        return {"error": f"API returned an error: {e}"}
    except ValueError:
        return {"error": "The API did not return valid JSON."}

    if not isinstance(data, dict):
        return {"answer": str(data), "sources": []}

    answer = data.get("answer") or data.get("response") or data.get("reply") or str(data)
    sources = data.get("sources") or data.get("citations") or []
    steps = data.get("steps") or data.get("trace") or data.get("tool_calls") or []
    return {
        "answer": answer,
        "sources": sources if isinstance(sources, list) else [sources],
        "confidence": data.get("confidence"),
        "follow_up": data.get("follow_up"),
        "steps": steps,
    }


def source_label(src) -> str:
    """One readable line for a citation, whether it is a string or a dict."""
    if isinstance(src, str):
        return src
    if isinstance(src, dict):
        name = src.get("variety_name") or src.get("title") or src.get("id") or "source"
        rid = f" ({src['id']})" if src.get("id") and src.get("variety_name") else ""
        url = src.get("source_url") or src.get("url")
        return f"[{name}{rid}]({url})" if url else f"{name}{rid}"
    return str(src)


# ---------------------------------------------------------------- feedback
def rate(index: int, rating: str) -> None:
    """Button callback: save the rating once and remember it."""
    msg = st.session_state.messages[index]
    if msg.get("rating"):
        return
    question = st.session_state.messages[index - 1]["content"] if index > 0 else ""
    save_feedback(rating, question, msg["content"], msg.get("endpoint", ""), msg.get("sources", []))
    msg["rating"] = rating


# ---------------------------------------------------------------- timeline
def show_timeline(season: str, planting: date) -> None:
    t = build_timeline(season, planting)
    rows = [
        {
            "Stage": s.name,
            "Start": pd.Timestamp(s.start),
            "End": pd.Timestamp(s.end),
            "Type": s.kind,
        }
        for s in t["stages"]
    ]
    df = pd.DataFrame(rows)
    order = list(df["Stage"])

    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadius=3, height=18)
        .encode(
            x=alt.X("Start:T", title=None, axis=alt.Axis(format="%b %Y", labelAngle=0, tickCount="month")),
            x2="End:T",
            y=alt.Y("Stage:N", sort=order, title=None),
            color=alt.Color(
                "Type:N",
                scale=alt.Scale(domain=list(STAGE_COLORS), range=list(STAGE_COLORS.values())),
                legend=alt.Legend(title=None, orient="bottom"),
            ),
            tooltip=[
                "Stage",
                alt.Tooltip("Start:T", format="%d %b %Y"),
                alt.Tooltip("End:T", format="%d %b %Y"),
            ],
        )
        .properties(height=34 * len(order) + 40)
    )
    try:
        st.altair_chart(chart, width="stretch")  # newer Streamlit
    except TypeError:
        st.altair_chart(chart, use_container_width=True)  # older Streamlit

    c1, c2, c3 = st.columns(3)
    c1.metric("Planting", planting.strftime("%d %b %Y"))
    c2.metric("Harvest window", f"{t['harvest_start']:%d %b %Y} to {t['harvest_end']:%d %b %Y}")
    c3.metric("Harvest months", ", ".join(t["harvest_months"]))

    split_text = ", ".join(f"{s.name}: {s.start:%d %b %Y}" for s in t["stages"] if s.kind == "fertiliser")
    st.caption(f"Fertiliser splits: {split_text}")
    st.caption(
        f"Assumes a {t['duration_months']}-month {season} crop and a harvest window of 30 days either side. "
        "These numbers are placeholders and are not yet verified against the MPKV guide."
    )


# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.header("Settings")
    api_url = st.text_input("API URL", DEFAULT_API_URL)
    endpoint = st.radio("Endpoint", ["ask", "agent"], horizontal=True)
    st.divider()
    st.header("Season timeline")
    season = st.selectbox("Season", SEASONS)
    planting_date = st.date_input("Planting date", value=date.today())
    if st.button("Clear chat"):
        st.session_state.messages = []

# ---------------------------------------------------------------- main page
st.title("🌾 CaneMitra")
st.caption("Your friend for sugarcane questions. Answers come from university variety guides.")

with st.expander(f"Season timeline: {season}, planted {planting_date:%d %b %Y}", expanded=True):
    show_timeline(season, planting_date)

if "messages" not in st.session_state:
    st.session_state.messages = []

for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] != "assistant" or msg.get("error"):
            continue
        if msg.get("confidence"):
            st.caption(f"Confidence: {msg['confidence']}")
        if msg.get("sources"):
            with st.expander(f"Citations ({len(msg['sources'])})"):
                for src in msg["sources"]:
                    st.markdown(f"- {source_label(src)}")
        if msg.get("steps"):
            with st.expander("Agent steps"):
                st.write(msg["steps"])
        if msg.get("follow_up"):
            st.caption(f"Follow-up: {msg['follow_up']}")

        if msg.get("rating"):
            st.caption("Thanks for the feedback " + ("👍" if msg["rating"] == "up" else "👎"))
        else:
            b1, b2, _ = st.columns([1, 1, 8])
            b1.button("👍", key=f"up_{i}", on_click=rate, args=(i, "up"))
            b2.button("👎", key=f"down_{i}", on_click=rate, args=(i, "down"))

question = st.chat_input("Ask about sugarcane varieties, seasons, yield...")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.spinner("Thinking..."):
        result = call_api(api_url, endpoint, question)
    if "error" in result:
        st.session_state.messages.append({"role": "assistant", "content": result["error"], "error": True})
    else:
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": result["answer"],
                "sources": result["sources"],
                "confidence": result["confidence"],
                "follow_up": result["follow_up"],
                "steps": result["steps"],
                "endpoint": endpoint,
            }
        )
    st.rerun()
