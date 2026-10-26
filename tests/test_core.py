from src.analyzer import analyze_prompt, optimize_prompt
from src.evaluator import evaluate_response


def test_analysis_identifies_missing_context():
    analysis = analyze_prompt("Explain machine learning.")
    assert analysis.weaknesses
    assert "Output format compliance" not in analysis.detected_techniques


def test_optimizer_preserves_original_task():
    analysis = analyze_prompt("Explain machine learning.")
    optimized = optimize_prompt("Explain machine learning.", analysis)
    assert "Explain machine learning." in optimized
    assert "Requirements" in optimized


def test_evaluator_returns_all_rubric_criteria():
    evaluation = evaluate_response("Explain this with headings.", "# Answer\n\nA complete explanation.")
    assert set(evaluation.scores) == {
        "Relevance",
        "Completeness",
        "Instruction compliance",
        "Output format compliance",
        "Factual support",
    }
    assert 5 <= evaluation.total <= 25
