"""Dataset loading from local files (CSV/JSON)."""

import csv
import json
from pathlib import Path
from typing import List, Dict, Any

from deepeval.test_case import LLMTestCase


class DatasetLoader:
    """Loads evaluation datasets from local CSV or JSON files."""

    @staticmethod
    def load_csv(file_path: str) -> List[LLMTestCase]:
        """
        Load test cases from CSV file.

        Expected CSV columns:
        - input (required): Input message/query
        - expected_output (optional): Expected AI response
        - expected_guardrail_decision (optional): "ALLOW" or "BLOCK"
        - expected_blocked_policies (optional): Comma-separated policy IDs
        - category (optional): Test case category
        - context (optional): JSON array of context strings

        Args:
            file_path: Path to CSV file

        Returns:
            List of DeepEval LLMTestCase objects
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Dataset not found: {file_path}")

        test_cases = []
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                test_case = DatasetLoader._row_to_test_case(row, idx)
                test_cases.append(test_case)

        return test_cases

    @staticmethod
    def load_json(file_path: str) -> List[LLMTestCase]:
        """
        Load test cases from JSON file.

        Expected JSON format:
        [
            {
                "input": "...",
                "expected_output": "...",
                "expected_guardrail_decision": "ALLOW",
                "expected_blocked_policies": ["pii", "toxicity"],
                "category": "...",
                "context": ["...", "..."]
            }
        ]

        Args:
            file_path: Path to JSON file

        Returns:
            List of DeepEval LLMTestCase objects
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Dataset not found: {file_path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("JSON dataset must be an array of test cases")

        test_cases = []
        for idx, row in enumerate(data):
            test_case = DatasetLoader._row_to_test_case(row, idx)
            test_cases.append(test_case)

        return test_cases

    @staticmethod
    def _row_to_test_case(row: Dict[str, Any], idx: int) -> LLMTestCase:
        """Convert dataset row to DeepEval test case."""
        # Required field
        if "input" not in row or not row["input"]:
            raise ValueError(f"Row {idx}: 'input' field is required")

        # Parse context (JSON array string or list)
        context = row.get("context", [])
        if isinstance(context, str):
            try:
                context = json.loads(context)
            except json.JSONDecodeError:
                context = [context]  # Treat as single context string

        # Create test case
        test_case = LLMTestCase(
            input=row["input"],
            actual_output=None,  # Populated during eval run
            expected_output=row.get("expected_output"),
            context=context if isinstance(context, list) else [],
            retrieval_context=row.get("retrieval_context", []),
        )

        # Add Klira-specific metadata
        test_case.additional_metadata = {
            "klira": {
                "test_case_id": f"tc_{idx}",
                "expected_guardrail_decision": row.get("expected_guardrail_decision"),
                "expected_blocked_policies": _parse_policy_list(
                    row.get("expected_blocked_policies", "")
                ),
                "category": row.get("category"),
            }
        }

        return test_case


def _parse_policy_list(policy_str: Any) -> List[str]:
    """Parse comma-separated policy IDs."""
    if not policy_str:
        return []
    if isinstance(policy_str, list):
        return policy_str
    return [p.strip() for p in str(policy_str).split(",") if p.strip()]
