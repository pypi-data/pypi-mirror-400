"""Klira AI Guardrail component for policy-based prompt augmentation and response generation.

Matches input text against defined policies, extracts relevant guidelines,
and uses these to augment prompts or generate policy-aware responses via an LLM.
"""
# mypy: disable-error-code=unreachable

import logging
import inspect
import asyncio
from typing import Dict, Any, List, Optional, TypedDict

# Import shared types/protocols
from .llm_service import (
    LLMServiceProtocol,
    LLMEvaluationResult,
    DefaultLLMService,
)  # Use the defined protocol
from .policy_loader import PolicyLoader, FileSystemPolicyLoader
from klira.sdk.utils.span_utils import safe_set_span_attribute
from opentelemetry import trace

logger = logging.getLogger("klira.guardrails.augmentation")


# Define expected result structure for augmentation processing
class AugmentationResult(TypedDict, total=False):
    matched_policies: List[Dict[str, Any]]
    extracted_guidelines: List[str]
    augmented_prompt: Optional[str]
    generated_response: Optional[str]  # If LLM generated a direct response
    llm_evaluation: Optional[
        LLMEvaluationResult
    ]  # If LLM was used for evaluation/generation


class PolicyAugmentation:
    """Matches messages to policies and augments prompts or generates responses.

    Loads policies (YAML/JSON), matches them against input messages,
    extracts guidelines, and optionally uses an LLM service to augment
    prompts or generate policy-aware responses.

    Attributes:
        policy_loader: PolicyLoader used to fetch policies.
        llm_service: An instance conforming to LLMServiceProtocol.
        policies: List of loaded and processed policy rules.
    """

    policy_loader: PolicyLoader
    llm_service: LLMServiceProtocol
    policies: List[Dict[str, Any]]

    def __init__(
        self,
        policies_path: Optional[str] = None,
        llm_service: Optional[LLMServiceProtocol] = None,
        policy_loader: Optional[PolicyLoader] = None,
    ):
        """Initializes the PolicyAugmentation component.

        Policies are loaded synchronously during initialization to guarantee
        immediate availability after __init__() returns. This prevents race
        conditions where policies might be empty on first use.

        Args:
            policies_path: Legacy parameter - path to policy files. If provided,
                creates a FileSystemPolicyLoader internally.
            llm_service: An optional LLM service instance (LLMServiceProtocol).
                         If None, uses DefaultLLMService (passthrough).
            policy_loader: PolicyLoader instance to use. Takes precedence over policies_path.

        Raises:
            ValueError: If neither policies_path nor policy_loader is provided.
            FileNotFoundError: If the policies_path does not exist.
        """
        # Handle legacy policies_path parameter for backward compatibility
        if policy_loader is None:
            if policies_path is None:
                raise ValueError(
                    "Either policies_path or policy_loader must be provided"
                )
            logger.info(
                f"[Augmentation] Using legacy policies_path parameter: {policies_path}"
            )
            self.policy_loader = FileSystemPolicyLoader(policies_path)
        else:
            self.policy_loader = policy_loader
            logger.info(
                f"[Augmentation] Using provided PolicyLoader: {type(policy_loader).__name__}"
            )

        if llm_service is None:
            logger.warning(
                "No LLM service provided to PolicyAugmentation, using DefaultLLMService."
            )
            self.llm_service = DefaultLLMService()
        else:
            self.llm_service = llm_service

        # Initialize fuzzy matcher (graceful degradation if rapidfuzz not available)
        self.fuzzy_matcher = None
        try:
            from klira.sdk.guardrails.fuzzy_matcher import FuzzyMatcher

            self.fuzzy_matcher = FuzzyMatcher(threshold=70)
            logger.info("[Augmentation] FuzzyMatcher initialized with 70% threshold")
        except ImportError:
            logger.warning(
                "[Augmentation] RapidFuzz not installed. Fuzzy matching will be disabled. "
                "Install with: pip install rapidfuzz"
            )

        # Load policies synchronously for guaranteed immediate availability (PROD-145)
        result = self.policy_loader.load_policies()
        self.policies: List[Dict[str, Any]] = result.policies
        logger.info(
            f"[Augmentation] PolicyAugmentation initialized with {len(self.policies)} policies from {result.source}"
        )
        self._validate_policies_loaded()

        # Get tracer for telemetry
        self.tracer = trace.get_tracer("klira.guardrails.augmentation")

    def _validate_policies_loaded(self) -> None:
        """Validates that policies were loaded successfully.

        Logs a warning if no policies were found, which means all evaluations
        will return default allowed behavior.
        """
        if not self.policies:
            logger.warning(
                "[Augmentation] No policies loaded. "
                "All evaluations will return default allowed behavior."
            )

    def _match_policies(
        self, text: str, direction: str = "inbound"
    ) -> List[Dict[str, Any]]:
        """Match the input text against policies.

        Args:
            text: The text to match against policies.
            direction: The direction of the text ('inbound' or 'outbound').

        Returns:
            List of matched policy dictionaries.
        """
        matched_policies: List[Dict[str, Any]] = []

        for policy in self.policies:
            policy_direction = policy.get("direction", "both")

            # Skip if direction doesn't match
            if policy_direction != "both" and policy_direction != direction:
                continue

            matched = False

            # Check compiled regex patterns
            compiled_patterns = policy.get("compiled_patterns", [])
            if compiled_patterns:
                for pattern in compiled_patterns:
                    if pattern.search(text):
                        matched = True
                        logger.debug(
                            f"[Augmentation] Pattern match: '{pattern.pattern}' in policy {policy['id']}"
                        )
                        break

            # Check compiled domain patterns
            if not matched:
                compiled_domains = policy.get("compiled_domains", [])
                if compiled_domains:
                    for domain_pattern in compiled_domains:
                        if domain_pattern.search(text):
                            matched = True
                            logger.debug(
                                f"[Augmentation] Domain match: '{domain_pattern.pattern}' in policy {policy['id']}"
                            )
                            break

            # Check fuzzy matching if no exact matches and fuzzy matcher available
            domains = policy.get("domains", [])
            if not matched and self.fuzzy_matcher and domains:
                fuzzy_matches = self.fuzzy_matcher.check_fuzzy_match(
                    text, domains if domains else []
                )
                if fuzzy_matches:
                    matched = True
                    # Calculate fuzzy confidence like in fast_rules
                    max_similarity = max([match[2] for match in fuzzy_matches])
                    fuzzy_confidence = 0.35 + (max_similarity / 100.0 * 0.2)
                    logger.debug(
                        f"[Augmentation] Fuzzy matches in policy {policy['id']}: "
                        f"{[match[0] for match in fuzzy_matches]} (confidence: {fuzzy_confidence})"
                    )

            if matched:
                matched_policies.append(policy)

        return matched_policies

    def _extract_guidelines(self, policies: List[Dict[str, Any]]) -> List[str]:
        """Extract guidelines from matched policies.

        Args:
            policies: List of matched policy dictionaries.

        Returns:
            List of unique guideline strings.
        """
        guidelines = []
        seen_guidelines = set()

        for policy in policies:
            policy_guidelines = policy.get("guidelines", [])
            if policy_guidelines:
                for guideline in policy_guidelines:
                    if guideline and guideline not in seen_guidelines:
                        guidelines.append(guideline)
                        seen_guidelines.add(guideline)
                        logger.debug(
                            f"[Augmentation] Extracted guideline from policy {policy['id']}: {guideline[:50]}..."
                        )

        return guidelines

    def process(
        self,
        message: str,
        direction: str = "inbound",
        context: Optional[Dict[str, Any]] = None,
    ) -> AugmentationResult:
        """Process a message for policy augmentation synchronously.

        Args:
            message: The message to process.
            direction: The direction of the message ('inbound' or 'outbound').
            context: Optional context for processing.

        Returns:
            AugmentationResult with matched policies and extracted guidelines.
        """
        with self.tracer.start_as_current_span("policy_augmentation_process") as span:
            safe_set_span_attribute(span, "augmentation.direction", direction)
            safe_set_span_attribute(span, "augmentation.message_length", len(message))

            # Match policies
            matched_policies = self._match_policies(message, direction)
            safe_set_span_attribute(
                span, "augmentation.matched_policies", len(matched_policies)
            )

            # Extract guidelines
            guidelines = self._extract_guidelines(matched_policies)
            safe_set_span_attribute(
                span, "augmentation.guidelines_count", len(guidelines)
            )

            # Create augmented prompt if guidelines were found
            augmented_prompt = None
            if guidelines and direction == "inbound":
                augmented_prompt = self._create_augmented_prompt(message, guidelines)

            result = AugmentationResult(
                matched_policies=matched_policies,
                extracted_guidelines=guidelines,
                augmented_prompt=augmented_prompt,
            )

            logger.info(
                f"[Augmentation] Processed message: matched {len(matched_policies)} policies, "
                f"extracted {len(guidelines)} guidelines"
            )

            return result

    async def process_async(
        self,
        message: str,
        direction: str = "inbound",
        context: Optional[Dict[str, Any]] = None,
    ) -> AugmentationResult:
        """Process a message for policy augmentation asynchronously.

        Args:
            message: The message to process.
            direction: The direction of the message ('inbound' or 'outbound').
            context: Optional context for processing.

        Returns:
            AugmentationResult with matched policies and extracted guidelines.
        """
        # For now, just run the sync version in an executor
        # Future: could optimize with async I/O if needed
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.process, message, direction, context
        )

    def _create_augmented_prompt(
        self, original_message: str, guidelines: List[str]
    ) -> str:
        """Create an augmented prompt with policy guidelines.

        Args:
            original_message: The original user message.
            guidelines: List of policy guidelines to include.

        Returns:
            Augmented prompt string.
        """
        guidelines_text = "\n".join(f"- {guideline}" for guideline in guidelines)

        augmented = f"""You are an AI assistant that follows specific guidelines.

IMPORTANT GUIDELINES TO FOLLOW:
{guidelines_text}

Please respond to the following message while adhering to the above guidelines:

USER MESSAGE: {original_message}
"""
        return augmented

    async def evaluate_with_llm(
        self,
        message: str,
        guidelines: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[LLMEvaluationResult]:
        """Evaluate a message with guidelines using the LLM service.

        Args:
            message: The message to evaluate.
            guidelines: Guidelines to use for evaluation.
            context: Optional context for evaluation.

        Returns:
            LLMEvaluationResult if evaluation was performed, None otherwise.
        """
        if not guidelines:
            return None

        prompt = self._create_augmented_prompt(message, guidelines)

        # Check if the LLM service's evaluate method is async
        if inspect.iscoroutinefunction(self.llm_service.evaluate):
            return await self.llm_service.evaluate(  # type: ignore[call-arg]
                prompt=prompt,
                context=context or {},
            )
        else:
            # Run sync method in executor
            loop = asyncio.get_event_loop()
            result: Any = await loop.run_in_executor(
                None,
                lambda: self.llm_service.evaluate(prompt, context or {}),
            )
            return result
