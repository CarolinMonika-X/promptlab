import json
import sqlite3
from pathlib import Path

from .models import Experiment


def save_experiment(experiment: Experiment, database_path: str = "prompt_evaluator.db") -> None:
    connection = sqlite3.connect(database_path)
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS experiments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            model TEXT NOT NULL,
            mode TEXT NOT NULL,
            original_prompt TEXT NOT NULL,
            optimized_prompt TEXT NOT NULL,
            original_response TEXT NOT NULL,
            optimized_response TEXT NOT NULL,
            original_evaluation TEXT NOT NULL,
            optimized_evaluation TEXT NOT NULL,
            analysis TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        INSERT INTO experiments
        (created_at, model, mode, original_prompt, optimized_prompt, original_response,
         optimized_response, original_evaluation, optimized_evaluation, analysis)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            experiment.created_at,
            experiment.model,
            experiment.mode,
            experiment.original_prompt,
            experiment.optimized_prompt,
            experiment.original_response,
            experiment.optimized_response,
            json.dumps(experiment.original_evaluation.to_dict()),
            json.dumps(experiment.optimized_evaluation.to_dict()),
            json.dumps(experiment.analysis.to_dict()),
        ),
    )
    connection.commit()
    connection.close()


def export_experiment(experiment: Experiment, output_path: str) -> None:
    Path(output_path).write_text(
        json.dumps(
            {
                "created_at": experiment.created_at,
                "model": experiment.model,
                "mode": experiment.mode,
                "original_prompt": experiment.original_prompt,
                "optimized_prompt": experiment.optimized_prompt,
                "original_response": experiment.original_response,
                "optimized_response": experiment.optimized_response,
                "original_evaluation": experiment.original_evaluation.to_dict(),
                "optimized_evaluation": experiment.optimized_evaluation.to_dict(),
                "analysis": experiment.analysis.to_dict(),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
