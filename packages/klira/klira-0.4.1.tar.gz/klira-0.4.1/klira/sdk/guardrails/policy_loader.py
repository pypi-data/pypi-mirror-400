"""Policy loader abstraction for Klira guardrails.

This module provides a unified interface for loading policies from various sources
(filesystem, remote API, etc.) and eliminates duplicate loading between components.
"""

import os
import re
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, List, Any, Optional, Pattern

# Handle yaml import with proper error handling
try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    yaml = None  # type: ignore[assignment,unused-ignore]

from .policy_http_client import PolicyHTTPClient

logger = logging.getLogger("klira.guardrails.policy_loader")


@dataclass
class PolicyLoadResult:
    """Result of loading policies from any source.

    Attributes:
        policies: List of loaded policy dictionaries
        version: Optional version identifier for the policy set
        updated_at: Optional timestamp when policies were last updated
        source: Source identifier (e.g., "filesystem", "remote", "fallback")
    """

    policies: List[Dict[str, Any]]
    version: Optional[str] = None
    updated_at: Optional[str] = None
    source: str = "unknown"


# --- Pattern Compilation Cache (Memory Optimization) ---


@lru_cache(maxsize=1000)
def compile_pattern(pattern: str) -> Optional[Pattern[str]]:
    """Compile regex pattern with LRU caching to prevent memory leaks.

    Args:
        pattern: Raw regex pattern string

    Returns:
        Compiled Pattern object or None if compilation fails
    """
    try:
        return re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        logger.warning(f"Invalid regex pattern '{pattern}': {e}")
        return None


@lru_cache(maxsize=500)
def compile_domain_pattern(domain: str) -> Optional[Pattern[str]]:
    """Compile domain pattern with word boundaries and LRU caching.

    Args:
        domain: Domain string to convert to word-boundary regex

    Returns:
        Compiled Pattern object or None if compilation fails
    """
    try:
        # Use word boundaries for better matching
        domain_pattern = r"\b" + re.escape(domain) + r"\b"
        return re.compile(domain_pattern, re.IGNORECASE)
    except re.error as e:
        logger.warning(f"Error creating regex for domain '{domain}': {e}")
        return None


class PolicyLoader(ABC):
    """Abstract base class for policy loading implementations.

    Different loaders can fetch policies from various sources
    (filesystem, API, database, etc.) while providing a consistent interface.
    """

    @abstractmethod
    def load_policies(self) -> PolicyLoadResult:
        """Load policies from the configured source.

        Returns:
            PolicyLoadResult containing loaded policies and metadata

        Raises:
            FileNotFoundError: If source is not available
            ValueError: If policies are invalid or cannot be parsed
        """
        pass

    def _parse_policy_data(self, data: Any) -> List[Dict[str, Any]]:
        """Parse raw policy data into standardized list format.

        Handles various input formats:
        - List of policies
        - Dict with "policies" key containing list
        - Single policy dict

        Args:
            data: Raw policy data in various formats

        Returns:
            List of policy dictionaries
        """
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            if "policies" in data and isinstance(data["policies"], list):
                return data["policies"]
            else:
                # Treat single dict as one policy
                return [data]
        else:
            logger.warning(f"Unexpected policy data type: {type(data)}")
            return []

    def _compile_patterns_in_policy(self, policy: Dict[str, Any]) -> Dict[str, Any]:
        """Compile regex patterns and domain patterns in a policy.

        Modifies the policy dict in-place to add compiled patterns.

        Args:
            policy: Policy dictionary to process

        Returns:
            The same policy dict with compiled patterns added
        """

        # Compile regex patterns
        raw_patterns = policy.get("patterns", [])
        if isinstance(raw_patterns, list):
            compiled_patterns = []
            for pattern_str in raw_patterns:
                if isinstance(pattern_str, str):
                    compiled = compile_pattern(pattern_str)
                    if compiled:
                        compiled_patterns.append(compiled)
            if compiled_patterns:
                policy["compiled_patterns"] = compiled_patterns

        # Compile domain patterns
        raw_domains = policy.get("domains", [])
        if isinstance(raw_domains, list):
            compiled_domains = []
            for domain_str in raw_domains:
                if isinstance(domain_str, str):
                    compiled = compile_domain_pattern(domain_str)
                    if compiled:
                        compiled_domains.append(compiled)
            if compiled_domains:
                policy["compiled_domains"] = compiled_domains

        # Set default confidence levels if not present
        if "confidence_pattern" not in policy:
            policy["confidence_pattern"] = 0.8
        if "confidence_domain" not in policy:
            policy["confidence_domain"] = 0.4

        # Set default action if not present
        if "action" not in policy:
            policy["action"] = "allow"

        return policy


class FileSystemPolicyLoader(PolicyLoader):
    """Load policies from local filesystem (YAML or JSON files).

    This consolidates the duplicate loading logic from FastRulesEngine
    and PolicyAugmentation into a single implementation.
    """

    def __init__(self, policies_path: str):
        """Initialize filesystem policy loader.

        Args:
            policies_path: Path to directory containing policy files or single policy file

        Raises:
            FileNotFoundError: If policies_path doesn't exist
        """
        self.policies_path = policies_path

        if not os.path.exists(self.policies_path):
            raise FileNotFoundError(f"Policies path not found: {self.policies_path}")

        logger.info(
            f"FileSystemPolicyLoader initialized with path: {self.policies_path}"
        )

        # Cache for loaded policies - load once and reuse
        self._cached_result: Optional[PolicyLoadResult] = None

    def load_policies(self) -> PolicyLoadResult:
        """Load policies from filesystem.

        Returns:
            PolicyLoadResult with loaded policies (cached after first load)
        """
        # Return cached result if already loaded
        if self._cached_result is not None:
            logger.debug("Using cached policies from FileSystemPolicyLoader")
            return self._cached_result

        policies = []
        files_processed = 0

        # Determine files to process
        if os.path.isfile(self.policies_path):
            files_to_process = [self.policies_path]
        elif os.path.isdir(self.policies_path):
            files_to_process = [
                os.path.join(self.policies_path, f)
                for f in os.listdir(self.policies_path)
                if os.path.isfile(os.path.join(self.policies_path, f))
                and f.lower().endswith((".json", ".yaml", ".yml"))
            ]
        else:
            logger.error(f"Path is neither file nor directory: {self.policies_path}")
            return PolicyLoadResult(policies=[], source="filesystem")

        if not files_to_process:
            logger.warning(f"No policy files found in: {self.policies_path}")
            return PolicyLoadResult(policies=[], source="filesystem")

        # Process each file
        for file_path in files_to_process:
            files_processed += 1
            file_basename = os.path.basename(file_path)

            try:
                raw_data = self._load_file(file_path)
                if raw_data is None:
                    continue

                # Parse into list of policies
                policy_list = self._parse_policy_data(raw_data)

                # Process each policy
                for policy_data in policy_list:
                    if not isinstance(policy_data, dict):
                        logger.warning(  # type: ignore[unreachable]
                            f"Policy in {file_basename} is not a dict. Skipping."
                        )
                        continue  # pragma: no cover

                    policy_id = policy_data.get("id")
                    if not policy_id:
                        logger.warning(
                            f"Policy in {file_basename} missing 'id'. Skipping."
                        )
                        continue

                    # Compile patterns and set defaults
                    processed_policy = self._compile_patterns_in_policy(policy_data)
                    policies.append(processed_policy)

            except Exception as e:
                logger.error(
                    f"Error loading policies from {file_basename}: {e}", exc_info=True
                )

        logger.info(f"Loaded {len(policies)} policies from {files_processed} files")

        # Cache the result
        self._cached_result = PolicyLoadResult(policies=policies, source="filesystem")
        return self._cached_result

    def _load_file(self, file_path: str) -> Optional[Any]:
        """Load a single policy file (JSON or YAML).

        Args:
            file_path: Path to the file to load

        Returns:
            Parsed data or None if loading fails
        """
        file_basename = os.path.basename(file_path)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                if file_path.lower().endswith(".json"):
                    return json.load(f)
                elif file_path.lower().endswith((".yaml", ".yml")):
                    if not YAML_AVAILABLE or yaml is None:
                        logger.warning(
                            f"Cannot load YAML '{file_basename}': PyYAML not installed"
                        )
                        return None
                    return yaml.safe_load(f)
                else:
                    logger.warning(f"Unsupported file format: {file_basename}")
                    return None

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {file_basename}: {e}")
            return None
        except Exception as e:
            if (
                YAML_AVAILABLE
                and yaml
                and hasattr(yaml, "YAMLError")
                and isinstance(e, yaml.YAMLError)
            ):
                logger.error(f"YAML parse error in {file_basename}: {e}")
            else:
                logger.error(f"Error reading {file_basename}: {e}")
            return None


class RemotePolicyLoader(PolicyLoader):
    """
    Load policies from remote API with caching.

    Policies are fetched ONCE during initialization and cached for
    the lifetime of this PolicyLoader instance (no TTL refresh).
    """

    def __init__(
        self,
        http_client: PolicyHTTPClient,
        fallback_loader: Optional[PolicyLoader] = None,
    ):
        """
        Initialize remote policy loader.

        Args:
            http_client: HTTP client for fetching policies
            fallback_loader: Fallback loader if remote fetch fails
        """
        self.http_client = http_client
        self.fallback_loader = fallback_loader

        # Cache state - populated on first load, kept for instance lifetime
        self._cached_result: Optional[PolicyLoadResult] = None
        self._fetch_attempted: bool = False

    def load_policies(self) -> PolicyLoadResult:
        """
        Load policies from remote API with caching and fallback.

        Fetches policies ONCE on first call, caches for instance lifetime.
        """
        # Return cached policies if already fetched
        if self._cached_result is not None:
            logger.debug("Using cached policies from previous fetch")
            return self._cached_result

        # Haven't fetched yet - try remote fetch
        if not self._fetch_attempted:
            self._fetch_attempted = True

            try:
                result = self._fetch_remote_policies()
                self._cached_result = result
                logger.info("Policies fetched and cached for instance lifetime")
                return result

            except Exception as e:
                logger.error(f"Remote policy fetch failed: {e}")

                # Try fallback
                if self.fallback_loader is not None:
                    logger.info("Using fallback policy loader")
                    try:
                        result = self.fallback_loader.load_policies()
                        # Mark as fallback source
                        result.source = "fallback"
                        # Cache the fallback result too
                        self._cached_result = result
                        return result
                    except Exception as fallback_error:
                        logger.error(f"Fallback loader also failed: {fallback_error}")
                        raise
                else:
                    # No fallback available
                    raise ValueError(
                        "Remote fetch failed and no fallback configured"
                    ) from e

        # Should never reach here, but handle gracefully
        if self._cached_result is not None:
            return self._cached_result  # type: ignore[unreachable]  # pragma: no cover
        else:
            raise ValueError("No policies available")  # pragma: no cover

    def _fetch_remote_policies(self) -> PolicyLoadResult:
        """Fetch policies from remote API."""
        data = self.http_client.fetch_policies()

        # Parse policies and compile patterns
        policies = []
        raw_policies = self._parse_policy_data(data.get("policies", []))

        for policy_data in raw_policies:
            if not isinstance(policy_data, dict):
                logger.warning("Policy is not a dict. Skipping.")  # type: ignore[unreachable]
                continue  # pragma: no cover

            policy_id = policy_data.get("id")
            if not policy_id:
                logger.warning("Policy missing 'id'. Skipping.")
                continue

            # Compile patterns and set defaults
            processed_policy = self._compile_patterns_in_policy(policy_data)
            policies.append(processed_policy)

        return PolicyLoadResult(
            policies=policies,
            version=data.get("version"),
            updated_at=data.get("updated_at"),
            source="remote",
        )
