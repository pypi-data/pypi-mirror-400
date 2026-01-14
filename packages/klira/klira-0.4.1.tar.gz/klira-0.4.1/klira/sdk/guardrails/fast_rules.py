"""Fast, pattern-based rules engine for Klira AI guardrail policy enforcement.

This module implements a simple engine that evaluates text against predefined
patterns (regex) and keywords/domains specified in policy files (YAML or JSON).
It's designed for quick checks before potentially involving more complex LLM evaluations.
"""
# mypy: disable-error-code=unreachable

import logging
from typing import Dict, List, Any, Optional, TypedDict, Pattern

from .policy_loader import PolicyLoader, FileSystemPolicyLoader
from klira.sdk.performance import timed_operation

logger = logging.getLogger("klira.guardrails.fast_rules")  # Specific logger

# --- Type Definitions ---


class PolicyRule(TypedDict, total=False):
    """Structure of a single policy rule definition."""

    id: str  # Required
    description: Optional[str]
    action: str  # 'block' or 'allow' (default: allow if matched)
    direction: Optional[str]  # 'inbound', 'outbound', or 'both' (default: 'both')
    patterns: Optional[List[str]]  # List of raw regex strings
    compiled_patterns: Optional[List[Pattern[str]]]  # Pre-compiled regex objects
    domains: Optional[List[str]]  # List of keywords/domains
    compiled_domains: Optional[List[Pattern[str]]]  # Pre-compiled domain regex objects
    guidelines: Optional[List[str]]  # List of guideline strings for policy augmentation


class MatchedPattern(TypedDict):
    """Details of a single matched pattern (PROD-254 Phase 5)."""

    pattern: str  # The pattern/domain/token that matched
    match_type: str  # "pattern", "domain", or "fuzzy"
    similarity: Optional[
        float
    ]  # Similarity score for fuzzy matches (0-100), None otherwise


class PolicyMatch(TypedDict):
    """Details of a matched policy."""

    policy_id: str
    action: str  # "block" or "allow"
    matched_patterns: List[
        MatchedPattern
    ]  # Structured match details (PROD-254 Phase 5)
    guidelines: Optional[List[str]]  # If action="allow"


class FastRulesEvaluationResult(TypedDict):
    """Structure of the result returned by the FastRulesEngine evaluate method."""

    allowed: bool  # True if no blocking policies matched
    matched_policies: List[PolicyMatch]  # ALL policies that matched
    blocking_policies: List[str]  # IDs with action="block"
    augmentation_policies: List[str]  # IDs with action="allow"
    all_guidelines: List[str]  # All guidelines from action="allow" policies
    matched_patterns: List[
        MatchedPattern
    ]  # All specific patterns/domains that matched across policies (PROD-254 Phase 5)


class FuzzyTelemetry(TypedDict):
    """Structure for tracking fuzzy matching telemetry (PROD-151)."""

    total_calls: int
    total_matches: int
    total_duration_ms: float
    policies_with_matches: List[str]


# Default fuzzy matching threshold (PROD-243)
DEFAULT_FUZZY_SIMILARITY_THRESHOLD = 85.0


class FastRulesEngine:
    """Evaluates text against fast-matching rules defined in policies.

    Loads policies from a specified path (directory or file) containing
    YAML or JSON definitions. Each policy can define patterns (regex)
    or domains/keywords to match against input text.

    Attributes:
        policy_loader (PolicyLoader): The loader used to fetch policies.
        policies (List[Dict[str, Any]]): The loaded policy rules.
    """

    def __init__(
        self,
        policies_path: Optional[str] = None,
        policy_loader: Optional[PolicyLoader] = None,
    ):
        """Initializes the FastRulesEngine and loads policies.

        Policies are loaded synchronously during initialization to guarantee
        immediate availability after __init__() returns. This prevents race
        conditions where policies might be empty on first use.

        Args:
            policies_path: Legacy parameter - path to policy files. If provided,
                creates a FileSystemPolicyLoader internally.
            policy_loader: PolicyLoader instance to use. Takes precedence over policies_path.

        Raises:
            ValueError: If neither policies_path nor policy_loader is provided.
            FileNotFoundError: If the provided policies_path does not exist.
        """
        # Handle legacy policies_path parameter for backward compatibility
        if policy_loader is None:
            if policies_path is None:
                raise ValueError(
                    "Either policies_path or policy_loader must be provided"
                )
            logger.info(f"Using legacy policies_path parameter: {policies_path}")
            self.policy_loader: PolicyLoader = FileSystemPolicyLoader(policies_path)
        else:
            self.policy_loader = policy_loader
            logger.info(f"Using provided PolicyLoader: {type(policy_loader).__name__}")

        # Initialize fuzzy matcher (graceful degradation if rapidfuzz not available)
        self.fuzzy_matcher = None
        try:
            from klira.sdk.guardrails.fuzzy_matcher import FuzzyMatcher
            from klira.sdk.config import get_config

            config = get_config()
            threshold_float = getattr(
                config, "fuzzy_similarity_threshold", DEFAULT_FUZZY_SIMILARITY_THRESHOLD
            )
            threshold = int(threshold_float)  # FuzzyMatcher expects int
            self.fuzzy_matcher = FuzzyMatcher(threshold=threshold)
            logger.info(f"FuzzyMatcher initialized with {threshold}% threshold")
        except ImportError:
            logger.warning(
                "RapidFuzz not installed. Fuzzy matching will be disabled. "
                "Install with: pip install rapidfuzz"
            )

        # Load policies synchronously for guaranteed immediate availability (PROD-145)
        result = self.policy_loader.load_policies()
        self.policies: List[Dict[str, Any]] = result.policies
        logger.info(
            f"FastRulesEngine initialized with {len(self.policies)} policies from {result.source}"
        )
        self._validate_policies_loaded()

    def _validate_policies_loaded(self) -> None:
        """Validates that policies were loaded successfully.

        Logs a warning if no policies were found, which means all evaluations
        will return default allowed behavior.
        """
        if not self.policies:
            logger.warning(
                "No policies loaded. All evaluations will return default allowed behavior."
            )

    def evaluate(
        self,
        text: str,
        direction: str = "inbound",
        context: Optional[Dict[str, Any]] = None,
    ) -> FastRulesEvaluationResult:
        """Evaluates the given text against loaded policy rules.

        Performs pattern matching using compiled regex patterns and domain keywords.
        Returns detailed information about matched policies, blocking policies,
        augmentation policies, and extracted guidelines.

        Args:
            text: The text to evaluate against policy rules.
            direction: The direction of the text ('inbound' or 'outbound').
            context: Optional additional context for evaluation.

        Returns:
            FastRulesEvaluationResult containing evaluation details with:
            - allowed: True if no blocking policies matched
            - matched_policies: List of PolicyMatch objects for all matched policies
            - blocking_policies: List of policy IDs with action="block"
            - augmentation_policies: List of policy IDs with action="allow"
            - all_guidelines: All guidelines extracted from action="allow" policies
            - matched_patterns: All patterns that matched across all policies
        """
        with timed_operation("fast_rules", "guardrails"):
            matched_policy_objects: List[PolicyMatch] = []
            blocking_policy_ids: List[str] = []
            augmentation_policy_ids: List[str] = []
            all_guidelines: List[str] = []
            all_matched_patterns: List[
                MatchedPattern
            ] = []  # PROD-254 Phase 5: Structured match data

            # Track fuzzy matching for telemetry (PROD-151)
            fuzzy_matches_found = []

            for policy in self.policies:
                policy_direction = policy.get("direction", "both")
                if policy_direction:
                    policy_direction = policy_direction.lower()
                else:
                    policy_direction = "both"

                # Skip if direction doesn't match (case-insensitive)
                if policy_direction != "both" and policy_direction != direction.lower():
                    continue

                matched_patterns_in_policy: List[
                    MatchedPattern
                ] = []  # PROD-254 Phase 5

                # Check compiled regex patterns
                compiled_patterns = policy.get("compiled_patterns", [])
                if compiled_patterns:
                    for pattern in compiled_patterns:
                        if pattern.search(text):
                            pattern_str = pattern.pattern
                            # PROD-254 Phase 5: Create structured match object
                            match_obj = MatchedPattern(
                                pattern=pattern_str,
                                match_type="pattern",
                                similarity=None,
                            )
                            matched_patterns_in_policy.append(match_obj)
                            all_matched_patterns.append(match_obj)
                            logger.debug(
                                f"Pattern match: '{pattern_str}' in policy {policy['id']}"
                            )

                # Check compiled domain patterns
                compiled_domains = policy.get("compiled_domains", [])
                original_domains = policy.get("domains", [])
                if compiled_domains and original_domains:
                    for idx, domain_pattern in enumerate(compiled_domains):
                        if domain_pattern.search(text):
                            # Use original domain string, not the compiled pattern
                            domain_str = (
                                original_domains[idx]
                                if idx < len(original_domains)
                                else domain_pattern.pattern
                            )
                            # PROD-254 Phase 5: Create structured match object
                            match_obj = MatchedPattern(
                                pattern=domain_str, match_type="domain", similarity=None
                            )
                            matched_patterns_in_policy.append(match_obj)
                            all_matched_patterns.append(match_obj)
                            logger.debug(
                                f"Domain match: '{domain_str}' in policy {policy['id']}"
                            )

                # Check fuzzy matching if no exact matches found and fuzzy matcher is available
                domains = policy.get("domains", [])
                if not matched_patterns_in_policy and self.fuzzy_matcher and domains:
                    fuzzy_matches = self.fuzzy_matcher.check_fuzzy_match(
                        text, domains if domains else []
                    )
                    if fuzzy_matches:
                        for match in fuzzy_matches:
                            token = match[0]
                            similarity_score = match[
                                2
                            ]  # PROD-254 Phase 5: Extract similarity score
                            # PROD-254 Phase 5: Create structured match object with similarity
                            match_obj = MatchedPattern(
                                pattern=token,
                                match_type="fuzzy",
                                similarity=similarity_score,
                            )
                            matched_patterns_in_policy.append(match_obj)
                            all_matched_patterns.append(match_obj)
                            fuzzy_matches_found.append(policy["id"])

                        # Log fuzzy match details
                        max_similarity = max([match[2] for match in fuzzy_matches])
                        logger.debug(
                            f"Fuzzy matches in policy {policy['id']}: {[match[0] for match in fuzzy_matches]} "
                            f"(similarity: {max_similarity}%)"
                        )

                # If this policy matched, process it based on action
                if matched_patterns_in_policy:
                    action = policy.get("action", "allow")
                    policy_id = policy.get("id", "unknown")

                    # Extract guidelines if action="allow"
                    guidelines = None
                    if action == "allow":
                        guidelines = policy.get("guidelines", [])
                        # Always add allow policies to augmentation_policies, even without guidelines
                        # This ensures decision_layer correctly shows "policy_augmentation" (PROD-254 fix)
                        augmentation_policy_ids.append(policy_id)
                        if guidelines:
                            all_guidelines.extend(guidelines)
                            logger.debug(
                                f"Extracted {len(guidelines)} guidelines from policy {policy_id}"
                            )
                        else:
                            logger.debug(
                                f"Policy {policy_id} matched with action='allow' but no guidelines"
                            )
                    elif action == "block":
                        blocking_policy_ids.append(policy_id)
                        logger.debug(f"Blocking policy matched: {policy_id}")
                    # Note: "warn" action is deprecated but treated as "block" for backward compatibility
                    elif action == "warn":
                        logger.warning(
                            f"Policy {policy_id} uses deprecated 'warn' action - treating as 'block'"
                        )
                        blocking_policy_ids.append(policy_id)

                    # Create PolicyMatch object
                    policy_match = PolicyMatch(
                        policy_id=policy_id,
                        action=action,
                        matched_patterns=matched_patterns_in_policy,
                        guidelines=guidelines,
                    )
                    matched_policy_objects.append(policy_match)

            # Log fuzzy telemetry if matches were found (PROD-151)
            if fuzzy_matches_found:
                logger.info(
                    f"Fuzzy matching found matches in policies: {fuzzy_matches_found}"
                )

            # Determine if allowed based on blocking policies only
            # (not confidence levels - action determines behavior)
            allowed = len(blocking_policy_ids) == 0

            return FastRulesEvaluationResult(
                allowed=allowed,
                matched_policies=matched_policy_objects,
                blocking_policies=blocking_policy_ids,
                augmentation_policies=augmentation_policy_ids,
                all_guidelines=all_guidelines,
                matched_patterns=all_matched_patterns,
            )
