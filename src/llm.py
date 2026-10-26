import os
from typing import Callable

from .analyzer import optimize_prompt
from .models import PromptAnalysis


def _demo_response(prompt: str) -> str:
    return (
        "## Response\n\n"
        f"This is a local demonstration response for the task: **{prompt[:180]}**\n\n"
        "- The task has been interpreted using the supplied objective.\n"
        "- Add a Gemini API key in `.env` to generate a model response.\n\n"
        "### Assumptions\n"
        "This demo uses deterministic placeholder content, so its score is illustrative rather than an LLM result."
    )


def _get_model(model_name: str):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)


def generate_pair(
    original: str,
    analysis: PromptAnalysis,
    expected_outcome: str,
    audience: str,
    model_name: str,
) -> tuple[str, str, str]:
    optimized = optimize_prompt(original, analysis, expected_outcome, audience)
    model = _get_model(model_name)
    if model is None:
        return _demo_response(original), _demo_response(optimized), "Demo mode"
    original_result = model.generate_content(original)
    optimized_result = model.generate_content(optimized)
    return original_result.text, optimized_result.text, model_name


def generate_optimized(
    original: str,
    analysis: PromptAnalysis,
    expected_outcome: str,
    audience: str,
    model_name: str,
) -> tuple[str, str]:
    optimized = optimize_prompt(original, analysis, expected_outcome, audience)
    model = _get_model(model_name)
    if model is None:
        return optimized, "Demo mode"
    instruction = (
        "Rewrite the following optimized prompt to be more precise while preserving user intent. "
        "Return only the rewritten prompt.\n\n" + optimized
    )
    return model.generate_content(instruction).text, model_name
