import re

from .models import PromptAnalysis


def analyze_prompt(prompt: str, expected_outcome: str = "", audience: str = "") -> PromptAnalysis:
    text = prompt.strip()
    lowered = text.lower()
    strengths: list[str] = []
    weaknesses: list[str] = []
    recommendations: list[str] = []
    techniques: list[str] = ["Zero-shot prompting"]

    if len(text) >= 40:
        strengths.append("The prompt gives the model enough initial context to begin the task.")
    else:
        weaknesses.append("The prompt is very short and may leave important context implicit.")
        recommendations.append("Add background context and define the intended outcome.")
    if re.search(r"\b(explain|create|summarize|compare|classify|write|extract|analyze)\b", lowered):
        strengths.append("A recognizable task verb is present.")
    else:
        weaknesses.append("The primary action or objective is not explicit.")
        recommendations.append("Start with a precise action verb and a measurable objective.")
    if expected_outcome:
        strengths.append("An expected outcome was supplied.")
    else:
        weaknesses.append("No success criteria or expected outcome were supplied.")
        recommendations.append("Describe what a successful answer must contain.")
    if audience:
        strengths.append("The target audience is specified.")
        techniques.append("Context injection")
    else:
        weaknesses.append("The target audience and assumed knowledge are unspecified.")
        recommendations.append("Name the audience and desired level of technical detail.")
    if any(word in lowered for word in ("format", "table", "json", "bullet", "heading", "steps")):
        strengths.append("The output structure is at least partially specified.")
        techniques.append("Structured output prompting")
    else:
        weaknesses.append("The output format is not defined.")
        recommendations.append("Specify the format, length, tone, and organization of the answer.")
    if any(word in lowered for word in ("example", "for instance", "sample")):
        techniques.append("Few-shot prompting")
    if any(word in lowered for word in ("role", "act as", "you are")):
        techniques.append("Role-based prompting")

    if not strengths:
        strengths.append("The prompt provides a starting point for refinement.")
    if not recommendations:
        recommendations.append("Test the prompt against representative tasks and review the result.")
    objective = expected_outcome.strip() or text.split(".")[0].strip() or "Complete the requested task."
    return PromptAnalysis(objective, strengths, weaknesses, recommendations, list(dict.fromkeys(techniques)))


def optimize_prompt(prompt: str, analysis: PromptAnalysis, expected_outcome: str = "", audience: str = "") -> str:
    outcome = expected_outcome.strip() or analysis.objective
    audience_text = audience.strip() or "the intended audience"
    return (
        "You are a careful subject-matter expert. Complete the task below accurately and transparently.\n\n"
        f"Task: {prompt.strip()}\n"
        f"Objective: {outcome}\n"
        f"Audience: {audience_text}\n\n"
        "Requirements:\n"
        "- Preserve the user's intent and do not invent missing facts.\n"
        "- State important assumptions briefly before answering.\n"
        "- Use clear headings and concise, easy-to-scan language.\n"
        "- Include all requested elements and label uncertainty where relevant.\n\n"
        "Output format:\n"
        "1. Direct answer\n"
        "2. Supporting explanation or examples\n"
        "3. Short limitations or next steps"
    )
