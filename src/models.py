from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any


CRITERIA = (
    "Relevance",
    "Completeness",
    "Instruction compliance",
    "Output format compliance",
    "Factual support",
)


@dataclass
class PromptAnalysis:
    objective: str
    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[str]
    detected_techniques: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Evaluation:
    scores: dict[str, int]
    notes: dict[str, str]

    @property
    def total(self) -> int:
        return sum(self.scores.values())

    @property
    def percentage(self) -> float:
        return round(self.total / (len(CRITERIA) * 5) * 100, 1)

    def to_dict(self) -> dict[str, Any]:
        return {
            "scores": self.scores,
            "notes": self.notes,
            "total": self.total,
            "percentage": self.percentage,
        }


@dataclass
class Experiment:
    original_prompt: str
    optimized_prompt: str
    original_response: str
    optimized_response: str
    original_evaluation: Evaluation
    optimized_evaluation: Evaluation
    analysis: PromptAnalysis
    model: str
    mode: str
    created_at: str

    @classmethod
    def create(
        cls,
        original_prompt: str,
        optimized_prompt: str,
        original_response: str,
        optimized_response: str,
        original_evaluation: Evaluation,
        optimized_evaluation: Evaluation,
        analysis: PromptAnalysis,
        model: str,
        mode: str,
    ) -> "Experiment":
        return cls(
            original_prompt=original_prompt,
            optimized_prompt=optimized_prompt,
            original_response=original_response,
            optimized_response=optimized_response,
            original_evaluation=original_evaluation,
            optimized_evaluation=optimized_evaluation,
            analysis=analysis,
            model=model,
            mode=mode,
            created_at=datetime.now().isoformat(timespec="seconds"),
        )
