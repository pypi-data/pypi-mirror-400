# Klira SDK Evaluations

Evaluation orchestration for the Klira SDK using a **trace-based model**. The SDK captures execution traces automatically via OpenTelemetry, and the Klira platform evaluates them using an LLM judge for comprehensive analysis.

## Quick Start

```python
from klira import Klira
from klira.sdk.evals import evaluate

# Initialize Klira
Klira.init(api_key="klira_...", evals_run="eval_123")

# Define your agent/function
@Klira.agent
def my_agent(question: str) -> str:
    return "answer"

# Run evaluation
result = evaluate(
    target=my_agent,
    data="test_cases.csv"
)

print(f"Evaluated {result.total_test_cases} test cases")
# Traces automatically sent to platform for evaluation
```

## Architecture

### Trace-Based Evaluation Model

The Klira SDK uses a **platform-side trace-based evaluation model**:

```
SDK Side:
1. Load test cases from CSV/JSON
2. Run target function on each case
3. Capture execution traces via OTLP
4. Send traces to platform

Platform Side:
5. Analyze traces with LLM judge
6. Generate metrics and insights
7. Make available via API/dashboard

Result:
8. SDK returns basic metadata + test cases
9. User fetches detailed results from platform
```

**Key Benefits:**
- ✓ LLM-based evaluation (more accurate)
- ✓ Comprehensive trace analysis (full context)
- ✓ Asynchronous evaluation (non-blocking)
- ✓ Detailed insights and recommendations
- ✓ Automatic trace routing via OTLP

### Old Model vs New Model

| Aspect | Old (SDK-Side) | New (Platform-Side) |
|--------|---|---|
| Evaluation | SDK runs DeepEval metrics | Platform uses LLM judge |
| Timing | Synchronous (blocks) | Asynchronous (non-blocking) |
| Data Analyzed | Inputs/outputs only | Complete execution traces |
| Results | In result object | Via platform API/dashboard |
| Flexibility | Limited (fixed metrics) | High (LLM judge) |

## API Reference

### evaluate()

```python
def evaluate(
    target: Callable[[str], str],
    data: str,
    experiment_id: Optional[str] = None,
    organization_id: Optional[str] = None,
    project_id: Optional[str] = None,
    **kwargs: Any,
) -> KliraEvalResult:
    """
    Run evaluation on target function with trace-based model.

    Args:
        target: Function to evaluate (must be decorated with @Klira.agent, etc.)
        data: Path to CSV or JSON dataset with test cases
        experiment_id: Optional ID for experiment tracking
        organization_id: Optional organization context
        project_id: Optional project context

    Returns:
        KliraEvalResult with test_cases and metadata
    """
```

### KliraEvalResult

```python
@dataclass
class KliraEvalResult:
    # Primary fields (trace-based model)
    total_test_cases: int
    test_cases: Optional[List[LLMTestCase]] = None
    dataset_path: Optional[str] = None
    evals_run: Optional[str] = None
    created_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None

    # Context
    experiment_id: Optional[str] = None
    organization_id: Optional[str] = None
    project_id: Optional[str] = None

    # Deprecated (for backward compatibility)
    pass_rate: float = 0.0  # Use platform API
    passed_test_cases: int = 0  # Use platform API
    failed_test_cases: int = 0  # Use platform API
    avg_scores: Dict[str, float] = {}  # Use platform API
    metric_results: Dict[str, List] = {}  # Use platform API
    compliance_report: Optional[ComplianceReport] = None  # Use platform API
```

## Dataset Format

### CSV Format
```csv
input,expected_output
"What is 2+2?","4"
"What is the capital of France?","Paris"
...
```

### JSON Format
```json
[
  {
    "input": "What is 2+2?",
    "expected_output": "4"
  },
  {
    "input": "What is the capital of France?",
    "expected_output": "Paris"
  }
]
```

## Usage Examples

### Basic Evaluation

```python
from klira.sdk.evals import evaluate

result = evaluate(
    target=my_agent,
    data="test_cases.csv"
)

print(f"Test cases: {result.total_test_cases}")
print(f"Duration: {result.duration_seconds}s")

# Access test cases with outputs
for test_case in result.test_cases:
    print(f"Input: {test_case.input}")
    print(f"Output: {test_case.actual_output}")
```

### With Experiment Tracking

```python
result = evaluate(
    target=my_agent,
    data="test_cases.csv",
    experiment_id="exp_v2_improvements",
    organization_id="org_123",
    project_id="proj_456"
)

# Results automatically tagged with experiment context
print(f"Experiment: {result.experiment_id}")
print(f"Org: {result.organization_id}")
print(f"Project: {result.project_id}")
```

### Fetch Results from Platform

```python
import requests

result = evaluate(target=my_agent, data="test_cases.csv")

# Get detailed results from platform
response = requests.get(
    f"https://api.getklira.com/api/v1/eval-runs/{result.evals_run}",
    headers={"Authorization": f"Bearer {api_key}"}
)

eval_results = response.json()
print(f"Pass Rate: {eval_results['pass_rate']:.1%}")
print(f"Guardrail Recall: {eval_results['compliance_report']['guardrail_recall']:.1%}")
```

### Error Handling

```python
from klira.sdk.evals import evaluate

try:
    result = evaluate(
        target=my_agent,
        data="test_cases.csv"
    )
except ValueError as e:
    print(f"Invalid dataset format: {e}")
except Exception as e:
    print(f"Evaluation failed: {e}")

# Check for errors in specific test cases
for test_case in result.test_cases:
    if test_case.additional_metadata and "error" in test_case.additional_metadata:
        print(f"Error in {test_case.input}: {test_case.additional_metadata['error']}")
```

## Configuration

### Environment Variables

```bash
# Required
KLIRA_API_KEY=klira_...

# Optional: Evaluation run ID (auto-generated if not set)
KLIRA_EVALS_RUN=eval_12345

# Optional: OpenTelemetry endpoint
KLIRA_OPENTELEMETRY_ENDPOINT=http://localhost:4318

# Optional: Enable debug logging
KLIRA_DEBUG=true
```

### Programmatic Configuration

```python
from klira import Klira

Klira.init(
    api_key="klira_...",
    evals_run="eval_123",  # Routes traces to platform
    debug=True,
    opentelemetry_endpoint="http://localhost:4318"
)
```

## How It Works

### Execution Flow

1. **Load Dataset**: CSV or JSON file with test cases
2. **Run Target**: Execute decorated function on each test case
3. **Capture Traces**: OTLP automatically captures execution traces
4. **Send to Platform**: Traces routed to /evals/v1/traces
5. **Return Result**: SDK returns test cases and metadata
6. **Platform Evaluation**: Platform evaluates traces asynchronously
7. **Access Results**: User fetches results via API/dashboard

### Trace Capture

Traces are automatically captured by Klira decorators:

```python
@Klira.agent  # Creates trace span for the agent
def my_agent(question: str) -> str:
    response = openai.chat.create(...)  # Instrumented by Klira
    return response

# Execution automatically creates:
# - Agent span: execution, errors, timing
# - LLM span: model, tokens, latency
# - Guardrail span: compliance decisions
```

### Guardrail Integration

Guardrails are evaluated as part of trace-based model:

```python
@Klira.agent
@Klira.guardrails
def protected_agent(question: str) -> str:
    return response

# Evaluation captures:
# - Input guardrail decision (block/allow/augment)
# - Output guardrail decision
# - Which policies matched
# - Decision confidence and layer
```

## Migration from Old Model

If you were using the old `evaluate()` with DeepEval metrics:

**Before:**
```python
result = evaluate(
    target=my_agent,
    data="test_cases.csv",
    evaluators=[GuardrailsEffectivenessMetric()],
    upload_to_hub=True
)
print(result.pass_rate)  # Computed by SDK
```

**After:**
```python
result = evaluate(
    target=my_agent,
    data="test_cases.csv"
)

# Get results from platform
response = requests.get(
    f"https://api.getklira.com/api/v1/eval-runs/{result.evals_run}",
    headers={"Authorization": f"Bearer {api_key}"}
)
print(response.json()["pass_rate"])  # From platform
```

See [MIGRATION_TRACE_BASED_EVALS.md](../../docs/MIGRATION_TRACE_BASED_EVALS.md) for detailed migration guide.

## Deprecated Components

The following components are deprecated and will be removed in v2.0:

**Metric Classes** (metrics/ directory):
- `GuardrailsEffectivenessMetric`
- `PolicyCoverageMetric`
- `LayerConfidenceMetric`
- And 7 others...

**Result Upload**:
- `HubUploader` class
- `upload_to_hub` parameter

**Decision Capture**:
- `capture_guardrails_decision()` - utility only, not called by evaluate()

These are kept for backward compatibility but no longer used by `evaluate()`.

## Troubleshooting

### Traces Not Reaching Platform

**Check:**
1. Is `evals_run` configured? Set in Klira.init() or KLIRA_EVALS_RUN env var
2. Is OTLP endpoint correct? Check KLIRA_OPENTELEMETRY_ENDPOINT
3. Is API key valid? Must start with "klira_"

```python
from klira import Klira

config = Klira.get_config()
print(f"Evals run: {config.evals_run}")
print(f"OTLP endpoint: {config.opentelemetry_endpoint}")
```

### Test Cases Not Getting Outputs

**Check:**
1. Is target function decorated? Must use @Klira.agent, @Klira.workflow, etc.
2. Does target function accept string input? evaluate() passes test_case.input
3. Are there errors? Check test_case.additional_metadata["error"]

```python
for test_case in result.test_cases:
    if not test_case.actual_output:
        metadata = test_case.additional_metadata or {}
        print(f"Error: {metadata.get('error')}")
```

### Invalid Dataset Format

**Check:**
1. Is file path correct?
2. Is format supported? (.csv or .json)
3. Does CSV have "input" column?
4. Is JSON an array of objects?

```python
# Valid CSV
input,expected_output
"What is 2+2?","4"

# Valid JSON
[{"input": "What is 2+2?", "expected_output": "4"}]
```

## Files and Components

```
klira/sdk/evals/
├── runner.py                          # Main evaluate() function
├── types.py                           # KliraEvalResult and other types
├── dataset_loader.py                  # CSV/JSON dataset loading
├── guardrails_capture.py              # Advanced: capture guardrail decisions
├── hub_uploader.py                    # DEPRECATED: results upload
├── metrics/                           # DEPRECATED: metric classes
│   ├── guardrails_effectiveness.py
│   ├── policy_coverage.py
│   └── ... (10 total metric files)
└── README.md                          # This file
```

## API Reference

### Klira.init()

```python
Klira.init(
    api_key="klira_...",              # Required
    evals_run="eval_123",              # Optional: evaluation run ID
    opentelemetry_endpoint="...",      # Optional: OTLP endpoint
    debug=False,                       # Optional: debug logging
    tracing_enabled=True,              # Optional: enable tracing
    policy_enforcement=True,           # Optional: enable guardrails
)
```

### evaluate()

```python
evaluate(
    target: Callable[[str], str],      # Function to evaluate
    data: str,                         # Dataset file path
    experiment_id: Optional[str] = None,      # Experiment tracking
    organization_id: Optional[str] = None,    # Organization context
    project_id: Optional[str] = None,         # Project context
    **kwargs: Any,                     # Reserved for future use
) -> KliraEvalResult
```

## See Also

- [Example: Trace-Based Evaluation](../../examples/evals_trace_based_example.py)
- [Migration Guide](../../docs/MIGRATION_TRACE_BASED_EVALS.md)
- [Klira Documentation](https://docs.getklira.com)
- [Platform API Reference](https://docs.getklira.com/api)
- [Klira Dashboard](https://dashboard.getklira.com)

## Support

- **GitHub Issues**: https://github.com/getklira/klira-sdk/issues
- **GitHub Discussions**: https://github.com/getklira/klira-sdk/discussions
- **Documentation**: https://docs.getklira.com
- **Email**: support@getklira.com
