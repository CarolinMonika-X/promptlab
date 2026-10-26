import re

from .models import CRITERIA, Evaluation


def _score(condition: bool, strong: bool = False) -> int:
    return 5 if strong and condition else 4 if condition else 2


def evaluate_response(prompt: str, response: str, expected_outcome: str = "") -> Evaluation:
    prompt_lower = prompt.lower()
    response_lower = response.lower()
    words = response.split()
    has_structure = bool(re.search(r"(^|\n)(#|[-*]|\d+[.)])", response))
    asks_for_format = any(term in prompt_lower for term in ("table", "json", "bullet", "heading", "steps"))
    scores = {
        "Relevance": _score(bool(response.strip()), len(words) >= 25),
        "Completeness": _score(len(words) >= 30, len(words) >= 80),
        "Instruction compliance": _score(
            not any(marker in response_lower for marker in ("i cannot", "i'm unable")),
            "requirements" in prompt_lower or len(words) >= 40,
        ),
        "Output format compliance": _score(has_structure or not asks_for_format, has_structure and asks_for_format),
        "Factual support": _score(
            bool(response.strip()) and ("assum" in response_lower or "source" in response_lower or not expected_outcome),
            "source" in response_lower or "according" in response_lower,
        ),
    }
    notes = {
        "Relevance": "Measures whether a substantive answer was returned for the requested task.",
        "Completeness": "Estimated from response coverage and length; review manually for important omissions.",
        "Instruction compliance": "Checks for explicit structure and signs of refusal, not semantic correctness.",
        "Output format compliance": "Checks for headings/lists when the prompt requests a structured answer.",
        "Factual support": "A heuristic estimate; this is not a substitute for fact-checking.",
    }
    return Evaluation({criterion: min(5, max(1, value)) for criterion, value in scores.items()}, notes)
