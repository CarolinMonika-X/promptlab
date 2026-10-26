import os
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from src.analyzer import analyze_prompt, optimize_prompt
from src.evaluator import evaluate_response
from src.llm import generate_pair
from src.models import CRITERIA, Experiment
from src.storage import export_experiment, save_experiment

load_dotenv()
st.set_page_config(page_title="PromptLab", page_icon="🧪", layout="wide")

st.title("🧪 PromptLab")
st.caption("Prompt quality evaluator and optimizer for measurable LLM experiments")

with st.sidebar:
    st.header("Experiment settings")
    model_name = st.text_input("Gemini model", value=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))
    st.info("Without GEMINI_API_KEY, the app runs in local demo mode. Demo scores are heuristic estimates.")
    st.markdown("**Workflow**\n1. Describe the task\n2. Analyze weaknesses\n3. Optimize the prompt\n4. Compare responses\n5. Review and export")

if "experiment" not in st.session_state:
    st.session_state.experiment = None

with st.form("prompt_form"):
    st.subheader("1. Define your experiment")
    prompt = st.text_area(
        "Original prompt",
        placeholder="Example: Explain machine learning.",
        height=150,
    )
    col1, col2 = st.columns(2)
    with col1:
        expected_outcome = st.text_input("Expected outcome", placeholder="A beginner-friendly explanation with examples")
    with col2:
        audience = st.text_input("Target audience", placeholder="First-year computer science students")
    submitted = st.form_submit_button("Analyze and run comparison", type="primary", use_container_width=True)

if submitted:
    if not prompt.strip():
        st.error("Enter an original prompt before starting the experiment.")
    else:
        with st.spinner("Analyzing, optimizing, generating, and evaluating..."):
            analysis = analyze_prompt(prompt, expected_outcome, audience)
            original_response, optimized_response, used_model = generate_pair(
                prompt, analysis, expected_outcome, audience, model_name
            )
            optimized_prompt = optimize_prompt(prompt, analysis, expected_outcome, audience)
            experiment = Experiment.create(
                prompt,
                optimized_prompt,
                original_response,
                optimized_response,
                evaluate_response(prompt, original_response, expected_outcome),
                evaluate_response(optimized_prompt, optimized_response, expected_outcome),
                analysis,
                used_model,
                "Gemini" if used_model != "Demo mode" else "Demo",
            )
            st.session_state.experiment = experiment
            save_experiment(experiment)

experiment = st.session_state.experiment
if experiment is None:
    st.success("Ready. Start with a prompt above to run your first evaluation.")
else:
    st.divider()
    st.subheader("2. Prompt analysis")
    analysis_col, recommendation_col = st.columns(2)
    with analysis_col:
        st.markdown("**Strengths**")
        for item in experiment.analysis.strengths:
            st.markdown(f"- {item}")
        st.markdown("**Detected techniques:** " + ", ".join(experiment.analysis.detected_techniques))
    with recommendation_col:
        st.markdown("**Weaknesses and improvements**")
        for item in experiment.analysis.weaknesses + experiment.analysis.recommendations:
            st.markdown(f"- {item}")

    st.subheader("3. Prompt versions")
    prompt_col1, prompt_col2 = st.columns(2)
    with prompt_col1:
        st.markdown("**Original**")
        st.code(experiment.original_prompt, language="text")
    with prompt_col2:
        st.markdown("**Optimized**")
        st.code(experiment.optimized_prompt, language="text")

    st.subheader("4. Response comparison")
    response_col1, response_col2 = st.columns(2)
    with response_col1:
        st.markdown("**Original response**")
        st.markdown(experiment.original_response)
    with response_col2:
        st.markdown("**Optimized response**")
        st.markdown(experiment.optimized_response)

    st.subheader("5. Rubric results")
    score_rows = [
        {
            "Criterion": criterion,
            "Original": experiment.original_evaluation.scores[criterion],
            "Optimized": experiment.optimized_evaluation.scores[criterion],
            "Change": experiment.optimized_evaluation.scores[criterion]
            - experiment.original_evaluation.scores[criterion],
        }
        for criterion in CRITERIA
    ]
    st.dataframe(pd.DataFrame(score_rows), hide_index=True, use_container_width=True)
    chart = go.Figure(
        [
            go.Bar(name="Original", x=list(CRITERIA), y=[row["Original"] for row in score_rows]),
            go.Bar(name="Optimized", x=list(CRITERIA), y=[row["Optimized"] for row in score_rows]),
        ]
    )
    chart.update_layout(barmode="group", yaxis={"range": [0, 5], "title": "Score (1–5)"}, height=380)
    st.plotly_chart(chart, use_container_width=True)
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    metric_col1.metric("Original total", f"{experiment.original_evaluation.total}/25")
    metric_col2.metric("Optimized total", f"{experiment.optimized_evaluation.total}/25")
    delta = experiment.optimized_evaluation.percentage - experiment.original_evaluation.percentage
    metric_col3.metric("Percentage change", f"{delta:+.1f} pts")
    st.caption(f"Generated with {experiment.model} in {experiment.mode} mode. Scores are estimates and should be human-validated.")

    export_path = Path("promptlab-experiment.json")
    export_experiment(experiment, str(export_path))
    st.download_button(
        "Download evaluation report (JSON)",
        data=export_path.read_text(encoding="utf-8"),
        file_name="promptlab-experiment.json",
        mime="application/json",
    )
