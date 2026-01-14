"""CI/CD integration helpers for build gating and quality enforcement."""

from typing import Optional

from klira.sdk.evals.types import KliraEvalResult


def fail_build_on_threshold(
    result: KliraEvalResult,
    min_pass_rate: float = 0.90,
    min_guardrail_recall: float = 0.95,
    min_guardrail_precision: float = 0.95,
    max_llm_fallback_rate: Optional[float] = None,
    min_policy_coverage: Optional[float] = None,
) -> None:
    """
    Fail build if evaluation results don't meet quality thresholds.

    This function is designed for CI/CD pipelines to enforce quality gates
    based on evaluation results. It raises AssertionError if any threshold
    is not met, causing the build to fail.

    Args:
        result: KliraEvalResult from evaluate()
        min_pass_rate: Minimum overall pass rate (default: 0.90)
        min_guardrail_recall: Minimum guardrails recall (default: 0.95)
        min_guardrail_precision: Minimum guardrails precision (default: 0.95)
        max_llm_fallback_rate: Maximum LLM fallback rate (optional)
        min_policy_coverage: Minimum policy coverage rate (optional)

    Raises:
        AssertionError: If any threshold is not met

    Example:
        >>> from klira.sdk.evals import evaluate
        >>> from klira.sdk.evals.ci import fail_build_on_threshold
        >>>
        >>> result = evaluate(
        ...     target=my_agent,
        ...     data="tests/regression_suite.csv",
        ...     evaluators=[...],
        ... )
        >>>
        >>> # Fail build if quality gates not met
        >>> fail_build_on_threshold(
        ...     result,
        ...     min_pass_rate=0.95,
        ...     min_guardrail_recall=0.98,
        ... )

    CI/CD Integration Examples:

        GitHub Actions:
            - name: Run Klira Evaluation
              run: |
                python -m pytest tests/test_evals.py
                python ci_eval_check.py  # Contains fail_build_on_threshold

        GitLab CI:
            test:
              script:
                - python run_evals.py
                - python ci_eval_check.py

        Jenkins:
            stage('Quality Gate') {
              steps {
                sh 'python run_evals.py'
                sh 'python ci_eval_check.py'
              }
            }
    """
    # Check pass rate
    assert result.pass_rate >= min_pass_rate, (
        f"Pass rate too low: {result.pass_rate:.1%} < {min_pass_rate:.1%}. "
        f"({result.failed_test_cases}/{result.total_test_cases} test cases failed)"
    )

    # Check compliance report exists
    if result.compliance_report is None:
        raise ValueError(
            "Compliance report is not available. "
            "Ensure evaluate() was run with guardrails enabled."
        )

    # Check guardrail recall
    assert result.compliance_report.guardrail_recall >= min_guardrail_recall, (
        f"Guardrail recall too low: {result.compliance_report.guardrail_recall:.1%} < {min_guardrail_recall:.1%}. "
        f"Guardrails are missing too many violations."
    )

    # Check guardrail precision
    assert result.compliance_report.guardrail_precision >= min_guardrail_precision, (
        f"Guardrail precision too low: {result.compliance_report.guardrail_precision:.1%} < {min_guardrail_precision:.1%}. "
        f"Guardrails are blocking too many valid requests (false positives)."
    )

    # Optional: Check LLM fallback rate (cost control)
    if max_llm_fallback_rate is not None:
        assert result.compliance_report.llm_fallback_rate <= max_llm_fallback_rate, (
            f"LLM fallback rate too high: {result.compliance_report.llm_fallback_rate:.1%} > {max_llm_fallback_rate:.1%}. "
            f"Too many expensive LLM calls - consider adding more fast rules patterns."
        )

    # Optional: Check policy coverage
    if (
        min_policy_coverage is not None
        and result.compliance_report.policy_coverage_rate is not None
    ):
        assert result.compliance_report.policy_coverage_rate >= min_policy_coverage, (
            f"Policy coverage too low: {result.compliance_report.policy_coverage_rate:.1%} < {min_policy_coverage:.1%}. "
            f"Untested policies: {', '.join(result.compliance_report.untested_policies)}"
        )


def print_build_status(result: KliraEvalResult, verbose: bool = False) -> None:
    """
    Print build status summary for CI/CD logs.

    Args:
        result: KliraEvalResult from evaluate()
        verbose: Whether to print detailed metrics (default: False)

    Example:
        >>> result = evaluate(...)
        >>> print_build_status(result, verbose=True)
        ✅ BUILD PASSED - Evaluation Quality Gates Met
        ================================================
        Pass Rate: 95.0% (95/100 passed)
        Guardrail Recall: 98.0%
        Guardrail Precision: 97.0%
        ...
    """
    passed = result.is_passing()
    status = "✅ BUILD PASSED" if passed else "❌ BUILD FAILED"

    print(f"\n{status} - Evaluation Quality Gates")
    print("=" * 60)
    print(
        f"Pass Rate: {result.pass_rate:.1%} ({result.passed_test_cases}/{result.total_test_cases} passed)"
    )

    if verbose and result.compliance_report is not None:
        print("\nCompliance Metrics:")
        print(f"  Guardrail Recall: {result.compliance_report.guardrail_recall:.1%}")
        print(
            f"  Guardrail Precision: {result.compliance_report.guardrail_precision:.1%}"
        )
        print(f"  Policy Coverage: {result.compliance_report.policy_coverage_rate:.1%}")
        print(f"  LLM Fallback Rate: {result.compliance_report.llm_fallback_rate:.1%}")

        if result.compliance_report.untested_policies:
            print(
                f"  Untested Policies: {', '.join(result.compliance_report.untested_policies)}"
            )

        if result.compliance_report.recommendations:
            print("\nRecommendations:")
            for rec in result.compliance_report.recommendations:
                print(f"  • {rec}")

    if result.hub_url:
        print(f"\nView full results: {result.hub_url}")

    print()


def generate_quality_report(result: KliraEvalResult, output_path: str) -> None:
    """
    Generate a quality report file for CI/CD artifacts.

    Creates a markdown report that can be uploaded as a build artifact
    or attached to pull requests.

    Args:
        result: KliraEvalResult from evaluate()
        output_path: Path to write the markdown report

    Example:
        >>> result = evaluate(...)
        >>> generate_quality_report(result, "quality_report.md")
        # Then in CI/CD, upload as artifact or comment on PR
    """
    report_lines = [
        "# Klira Evaluation Quality Report",
        "",
        f"**Experiment ID:** {result.experiment_id or 'N/A'}",
        f"**Dataset:** {result.dataset_path}",
        f"**Date:** {result.created_at.strftime('%Y-%m-%d %H:%M:%S') if result.created_at else 'N/A'}",
        f"**Duration:** {result.duration_seconds:.2f}s"
        if result.duration_seconds
        else "",
        "",
        "## Overall Results",
        "",
        f"- **Pass Rate:** {result.pass_rate:.1%} ({result.passed_test_cases}/{result.total_test_cases} passed)",
        f"- **Failed Cases:** {result.failed_test_cases}",
    ]

    if result.compliance_report is not None:
        report_lines.extend(
            [
                "",
                "## Compliance Metrics",
                "",
                f"- **Guardrail Recall:** {result.compliance_report.guardrail_recall:.1%}",
                f"- **Guardrail Precision:** {result.compliance_report.guardrail_precision:.1%}",
                f"- **Policy Coverage:** {result.compliance_report.policy_coverage_rate:.1%}",
                f"- **Average Confidence:** {result.compliance_report.avg_confidence:.2f}",
                f"- **LLM Fallback Rate:** {result.compliance_report.llm_fallback_rate:.1%}",
            ]
        )

        if result.compliance_report.untested_policies:
            report_lines.extend(
                [
                    "",
                    "## Untested Policies",
                    "",
                ]
            )
            for policy in result.compliance_report.untested_policies:
                report_lines.append(f"- {policy}")

        if result.compliance_report.recommendations:
            report_lines.extend(
                [
                    "",
                    "## Recommendations",
                    "",
                ]
            )
            for rec in result.compliance_report.recommendations:
                report_lines.append(f"- {rec}")

    if result.hub_url:
        report_lines.extend(
            [
                "",
                "## Full Results",
                "",
                f"[View in Klira Hub]({result.hub_url})",
            ]
        )

    # Write report
    with open(output_path, "w") as f:
        f.write("\n".join(report_lines))


def assert_no_regressions(
    current_result: KliraEvalResult,
    baseline_result: KliraEvalResult,
    tolerance: float = 0.02,
) -> None:
    """
    Assert that current results don't regress from baseline.

    Compares current evaluation results against a baseline to detect
    quality regressions. Fails if any metric drops by more than tolerance.

    Args:
        current_result: Current evaluation result
        baseline_result: Baseline evaluation result to compare against
        tolerance: Maximum allowed regression (default: 0.02 = 2%)

    Raises:
        AssertionError: If regression detected

    Example:
        >>> # Load baseline from previous successful build
        >>> baseline = load_baseline_result("baseline.json")
        >>>
        >>> # Run current evaluation
        >>> current = evaluate(...)
        >>>
        >>> # Fail if quality regressed
        >>> assert_no_regressions(current, baseline, tolerance=0.03)
    """
    # Check pass rate
    pass_rate_diff = current_result.pass_rate - baseline_result.pass_rate
    assert pass_rate_diff >= -tolerance, (
        f"Pass rate regressed: {baseline_result.pass_rate:.1%} → {current_result.pass_rate:.1%} "
        f"({pass_rate_diff:+.1%})"
    )

    # Check compliance reports exist
    if current_result.compliance_report is None:
        raise ValueError(
            "Current result compliance report is not available. "
            "Ensure evaluate() was run with guardrails enabled."
        )
    if baseline_result.compliance_report is None:
        raise ValueError(
            "Baseline result compliance report is not available. "
            "Ensure baseline was generated with guardrails enabled."
        )

    # Check guardrail recall
    recall_diff = (
        current_result.compliance_report.guardrail_recall
        - baseline_result.compliance_report.guardrail_recall
    )
    assert recall_diff >= -tolerance, (
        f"Guardrail recall regressed: {baseline_result.compliance_report.guardrail_recall:.1%} → "
        f"{current_result.compliance_report.guardrail_recall:.1%} ({recall_diff:+.1%})"
    )

    # Check guardrail precision
    precision_diff = (
        current_result.compliance_report.guardrail_precision
        - baseline_result.compliance_report.guardrail_precision
    )
    assert precision_diff >= -tolerance, (
        f"Guardrail precision regressed: {baseline_result.compliance_report.guardrail_precision:.1%} → "
        f"{current_result.compliance_report.guardrail_precision:.1%} ({precision_diff:+.1%})"
    )
