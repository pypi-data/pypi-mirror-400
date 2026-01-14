"""Abstraction extractor for ATLAS learning pipeline.

Extracts reusable patterns from trajectories to improve memory.
Implements both LLM-based and text-based pattern extraction strategies.
"""

from __future__ import annotations

import ast
import json
import logging
import re
import uuid
from collections import Counter
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from cognitive_core.config import LearningConfig
from cognitive_core.core.types import CodeConcept, Strategy, Trajectory

if TYPE_CHECKING:
    from cognitive_core.llm.simple import SimpleLLM

logger = logging.getLogger("cognitive_core.learning.extractor")


# =============================================================================
# Pattern Extractor Protocol
# =============================================================================


@runtime_checkable
class PatternExtractor(Protocol):
    """Strategy for extracting patterns from trajectories.

    Implementations can use different approaches:
    - LLM-based: Use language models to identify conceptual patterns
    - Text-based: Use AST/regex analysis for syntactic patterns
    - Combined: Use both approaches and merge results
    """

    def extract_concepts(
        self,
        trajectories: list[Trajectory],
    ) -> list[CodeConcept]:
        """Extract reusable code concepts from trajectories.

        Args:
            trajectories: List of trajectories to analyze.

        Returns:
            List of extracted CodeConcept objects.
        """
        ...

    def extract_strategies(
        self,
        trajectories: list[Trajectory],
    ) -> list[Strategy]:
        """Extract abstract reasoning strategies from trajectories.

        Args:
            trajectories: List of trajectories to analyze.

        Returns:
            List of extracted Strategy objects.
        """
        ...


# =============================================================================
# LLM Pattern Extractor
# =============================================================================


class LLMPatternExtractor:
    """LLM-based pattern extraction.

    Uses language models to identify conceptual patterns and strategies
    from successful trajectories. Groups trajectories by domain for
    focused extraction.

    Example:
        ```python
        extractor = LLMPatternExtractor(llm=SimpleLLM())
        concepts = extractor.extract_concepts(trajectories)
        strategies = extractor.extract_strategies(trajectories)
        ```
    """

    def __init__(self, llm: SimpleLLM) -> None:
        """Initialize LLM pattern extractor.

        Args:
            llm: LLM adapter for generating patterns.
        """
        self._llm = llm

    def extract_concepts(
        self,
        trajectories: list[Trajectory],
    ) -> list[CodeConcept]:
        """Prompt LLM to identify reusable code patterns across trajectories.

        Collects code from successful trajectories, groups by domain,
        and prompts the LLM to identify common patterns.

        Args:
            trajectories: List of trajectories to analyze.

        Returns:
            List of CodeConcept objects extracted from trajectories.
        """
        # Filter to successful trajectories only
        successful = [t for t in trajectories if t.outcome.success]
        if not successful:
            return []

        # Group by domain for focused extraction
        by_domain = self._group_by_domain(successful)

        concepts: list[CodeConcept] = []
        for domain, domain_trajs in by_domain.items():
            domain_concepts = self._extract_concepts_for_domain(domain, domain_trajs)
            concepts.extend(domain_concepts)

        return concepts

    def extract_strategies(
        self,
        trajectories: list[Trajectory],
    ) -> list[Strategy]:
        """Prompt LLM to identify abstract reasoning strategies.

        Analyzes successful trajectories to extract situation/suggestion
        patterns that can be applied to similar tasks.

        Args:
            trajectories: List of trajectories to analyze.

        Returns:
            List of Strategy objects extracted from trajectories.
        """
        # Filter to successful trajectories only
        successful = [t for t in trajectories if t.outcome.success]
        if not successful:
            return []

        strategies: list[Strategy] = []
        for traj in successful:
            strategy = self._extract_strategy_from_trajectory(traj)
            if strategy:
                strategies.append(strategy)

        return strategies

    def _group_by_domain(
        self,
        trajectories: list[Trajectory],
    ) -> dict[str, list[Trajectory]]:
        """Group trajectories by their task domain.

        Args:
            trajectories: Trajectories to group.

        Returns:
            Dictionary mapping domain to list of trajectories.
        """
        by_domain: dict[str, list[Trajectory]] = {}
        for traj in trajectories:
            domain = traj.task.domain
            if domain not in by_domain:
                by_domain[domain] = []
            by_domain[domain].append(traj)
        return by_domain

    def _extract_concepts_for_domain(
        self,
        domain: str,
        trajectories: list[Trajectory],
    ) -> list[CodeConcept]:
        """Extract code concepts for a specific domain.

        Args:
            domain: Task domain (e.g., 'arc', 'swe').
            trajectories: Trajectories from this domain.

        Returns:
            List of CodeConcept objects.
        """
        # Format trajectories for the prompt
        traj_summaries = self._format_trajectories(trajectories)

        prompt = f"""Analyze these successful trajectories for {domain} tasks.
Identify reusable code patterns that appear across multiple solutions.

Trajectories:
{traj_summaries}

Return a JSON array of patterns found. Each pattern should have:
- name: A descriptive snake_case name
- description: What the pattern does
- code: The reusable code pattern
- signature: Type signature if applicable

Example format:
[
  {{"name": "pattern_name", "description": "What it does", "code": "def example(): pass", "signature": "() -> None"}}
]

Return only the JSON array, no other text."""

        try:
            result = self._llm.extract_json(prompt)
            if not isinstance(result, list):
                result = []
        except Exception as e:
            logger.warning(f"Failed to extract concepts for domain {domain}: {e}")
            return []

        concepts = []
        for item in result:
            if not isinstance(item, dict):
                continue

            concept = CodeConcept(
                id=f"concept-{uuid.uuid4().hex[:8]}",
                name=item.get("name", "unnamed_pattern"),
                description=item.get("description", ""),
                code=item.get("code", ""),
                signature=item.get("signature", ""),
                examples=item.get("examples", []),
                source="learned",
            )
            concepts.append(concept)

        return concepts

    def _extract_strategy_from_trajectory(
        self,
        trajectory: Trajectory,
    ) -> Strategy | None:
        """Extract a strategy from a single trajectory.

        Args:
            trajectory: Trajectory to analyze.

        Returns:
            Strategy object or None if extraction fails.
        """
        # Format steps for the prompt
        steps_summary = self._format_steps(trajectory)

        prompt = f"""Analyze this successful task solution and extract an abstract strategy.

Task: {trajectory.task.description}
Domain: {trajectory.task.domain}

Steps taken:
{steps_summary}

Extract a reusable strategy with:
- situation: When to apply this strategy (generalized from the task)
- suggestion: What approach to take (generalized from the solution)
- parameters: Key variables that would change between applications

Return JSON:
{{"situation": "...", "suggestion": "...", "parameters": [{{"name": "param1", "type": "string"}}, ...]}}

Return only the JSON, no other text."""

        try:
            result = self._llm.extract_json(prompt)
            if not isinstance(result, dict):
                return None
        except Exception as e:
            logger.warning(f"Failed to extract strategy: {e}")
            return None

        return Strategy(
            id=f"strategy-{uuid.uuid4().hex[:8]}",
            situation=result.get("situation", ""),
            suggestion=result.get("suggestion", ""),
            parameters=result.get("parameters", []),
            source="learned",
        )

    def _format_trajectories(self, trajectories: list[Trajectory]) -> str:
        """Format trajectories for LLM prompt.

        Args:
            trajectories: Trajectories to format.

        Returns:
            Formatted string representation.
        """
        summaries = []
        for i, traj in enumerate(trajectories[:5], 1):  # Limit to 5
            steps = [s.action for s in traj.steps[:3]]  # First 3 actions
            summaries.append(f"{i}. Task: {traj.task.description[:100]}")
            summaries.append(f"   Actions: {', '.join(steps)}")
        return "\n".join(summaries)

    def _format_steps(self, trajectory: Trajectory) -> str:
        """Format trajectory steps for LLM prompt.

        Args:
            trajectory: Trajectory to format.

        Returns:
            Formatted string representation of steps.
        """
        lines = []
        for i, step in enumerate(trajectory.steps[:10], 1):  # Limit to 10
            lines.append(f"{i}. Action: {step.action[:100]}")
            if step.thought:
                lines.append(f"   Thought: {step.thought[:100]}")
        return "\n".join(lines)


# =============================================================================
# Text Pattern Extractor
# =============================================================================


class TextPatternExtractor:
    """Text-based pattern extraction using heuristics.

    Uses AST parsing and text analysis to find common code structures
    without requiring an LLM. Good for syntactic patterns like:
    - Common function/method calls
    - Import patterns
    - Control flow structures

    Example:
        ```python
        extractor = TextPatternExtractor()
        concepts = extractor.extract_concepts(trajectories)
        strategies = extractor.extract_strategies(trajectories)
        ```
    """

    def __init__(self) -> None:
        """Initialize text pattern extractor."""
        self._min_frequency = 2  # Pattern must appear at least this many times

    def extract_concepts(
        self,
        trajectories: list[Trajectory],
    ) -> list[CodeConcept]:
        """Extract code patterns using text analysis.

        Finds repeated code patterns across trajectories using
        frequency analysis of function calls and imports.

        Args:
            trajectories: List of trajectories to analyze.

        Returns:
            List of CodeConcept objects.
        """
        # Filter to successful trajectories
        successful = [t for t in trajectories if t.outcome.success]
        if not successful:
            return []

        # Extract code from trajectories
        code_samples = self._extract_code_samples(successful)
        if not code_samples:
            return []

        # Find common patterns
        patterns = self._find_common_patterns(code_samples)

        return [self._pattern_to_concept(name, freq) for name, freq in patterns]

    def extract_strategies(
        self,
        trajectories: list[Trajectory],
    ) -> list[Strategy]:
        """Extract strategies using text heuristics.

        Looks for common action sequences in successful trajectories
        and creates generalized strategies.

        Args:
            trajectories: List of trajectories to analyze.

        Returns:
            List of Strategy objects.
        """
        # Filter to successful trajectories
        successful = [t for t in trajectories if t.outcome.success]
        if not successful:
            return []

        # Find common action sequences
        sequences = self._find_common_action_sequences(successful)

        return [self._sequence_to_strategy(seq, freq) for seq, freq in sequences]

    def _extract_code_samples(
        self,
        trajectories: list[Trajectory],
    ) -> list[str]:
        """Extract code from trajectory steps.

        Args:
            trajectories: Trajectories to extract code from.

        Returns:
            List of code strings.
        """
        code_samples = []
        for traj in trajectories:
            for step in traj.steps:
                # Look for code in action or observation
                code = self._extract_code_from_text(step.action)
                if code:
                    code_samples.append(code)
                code = self._extract_code_from_text(step.observation)
                if code:
                    code_samples.append(code)
        return code_samples

    def _extract_code_from_text(self, text: str) -> str | None:
        """Extract code blocks from text.

        Args:
            text: Text that may contain code.

        Returns:
            Extracted code or None.
        """
        # Look for markdown code blocks
        pattern = r"```(?:python)?\s*([\s\S]*?)\s*```"
        matches = re.findall(pattern, text)
        if matches:
            return matches[0]

        # Check if text looks like Python code
        if "def " in text or "import " in text or "class " in text:
            return text

        return None

    def _find_common_patterns(
        self,
        code_samples: list[str],
    ) -> list[tuple[str, int]]:
        """Find common patterns in code samples using AST analysis.

        Args:
            code_samples: List of code strings.

        Returns:
            List of (pattern_name, frequency) tuples.
        """
        call_counter: Counter[str] = Counter()
        import_counter: Counter[str] = Counter()

        for code in code_samples:
            try:
                tree = ast.parse(code)

                # Count function/method calls
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        name = self._get_call_name(node)
                        if name:
                            call_counter[name] += 1
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            import_counter[alias.name] += 1
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            import_counter[node.module] += 1
            except SyntaxError:
                continue

        # Combine and filter by frequency
        all_patterns: Counter[str] = Counter()
        for name, count in call_counter.items():
            if count >= self._min_frequency:
                all_patterns[f"call:{name}"] = count
        for name, count in import_counter.items():
            if count >= self._min_frequency:
                all_patterns[f"import:{name}"] = count

        return all_patterns.most_common(10)  # Top 10 patterns

    def _get_call_name(self, node: ast.Call) -> str | None:
        """Extract function/method name from a Call node.

        Args:
            node: AST Call node.

        Returns:
            Function name or None.
        """
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr
        return None

    def _find_common_action_sequences(
        self,
        trajectories: list[Trajectory],
    ) -> list[tuple[str, int]]:
        """Find common action sequences across trajectories.

        Args:
            trajectories: Trajectories to analyze.

        Returns:
            List of (sequence_description, frequency) tuples.
        """
        # Extract action patterns (simplified action types)
        sequence_counter: Counter[tuple[str, ...]] = Counter()

        for traj in trajectories:
            # Create a sequence of simplified action types
            actions = tuple(
                self._simplify_action(step.action) for step in traj.steps[:5]
            )
            if len(actions) >= 2:
                sequence_counter[actions] += 1

        # Filter and convert to descriptions
        results = []
        for seq, count in sequence_counter.most_common(5):
            if count >= self._min_frequency:
                desc = " -> ".join(seq)
                results.append((desc, count))

        return results

    def _simplify_action(self, action: str) -> str:
        """Simplify an action to a category.

        Args:
            action: Full action text.

        Returns:
            Simplified action category.
        """
        action_lower = action.lower()

        if "read" in action_lower or "cat " in action_lower:
            return "read_file"
        elif "write" in action_lower or "edit" in action_lower:
            return "edit_file"
        elif "run" in action_lower or "execute" in action_lower:
            return "execute"
        elif "search" in action_lower or "grep" in action_lower or "find" in action_lower:
            return "search"
        elif "test" in action_lower or "pytest" in action_lower:
            return "test"
        else:
            return "other"

    def _pattern_to_concept(
        self,
        pattern: str,
        frequency: int,
    ) -> CodeConcept:
        """Convert a pattern to a CodeConcept.

        Args:
            pattern: Pattern string (e.g., "call:sort").
            frequency: How often the pattern appears.

        Returns:
            CodeConcept object.
        """
        pattern_type, name = pattern.split(":", 1)

        if pattern_type == "call":
            description = f"Common function call: {name}()"
            code = f"{name}(...)"
        else:
            description = f"Common import: {name}"
            code = f"import {name}"

        return CodeConcept(
            id=f"concept-{uuid.uuid4().hex[:8]}",
            name=name.replace(".", "_"),
            description=description,
            code=code,
            signature="",
            usage_count=frequency,
            source="learned",
        )

    def _sequence_to_strategy(
        self,
        sequence: str,
        frequency: int,
    ) -> Strategy:
        """Convert an action sequence to a Strategy.

        Args:
            sequence: Sequence description string.
            frequency: How often the sequence appears.

        Returns:
            Strategy object.
        """
        return Strategy(
            id=f"strategy-{uuid.uuid4().hex[:8]}",
            situation=f"When solving tasks that require: {sequence.split(' -> ')[0]}",
            suggestion=f"Follow this approach: {sequence}",
            parameters=[],
            usage_count=frequency,
            source="learned",
        )


# =============================================================================
# Combined Pattern Extractor
# =============================================================================


class CombinedPatternExtractor:
    """Combined LLM and text-based pattern extraction.

    Uses both LLM analysis and text heuristics, then merges and
    deduplicates the results for comprehensive pattern coverage.

    Example:
        ```python
        extractor = CombinedPatternExtractor(llm=SimpleLLM())
        concepts = extractor.extract_concepts(trajectories)
        strategies = extractor.extract_strategies(trajectories)
        ```
    """

    def __init__(self, llm: SimpleLLM) -> None:
        """Initialize combined pattern extractor.

        Args:
            llm: LLM adapter for the LLM-based extractor.
        """
        self._llm_extractor = LLMPatternExtractor(llm)
        self._text_extractor = TextPatternExtractor()

    def extract_concepts(
        self,
        trajectories: list[Trajectory],
    ) -> list[CodeConcept]:
        """Combine LLM and text extraction, deduplicate.

        Args:
            trajectories: List of trajectories to analyze.

        Returns:
            Merged and deduplicated list of CodeConcept objects.
        """
        llm_concepts = self._llm_extractor.extract_concepts(trajectories)
        text_concepts = self._text_extractor.extract_concepts(trajectories)

        # Merge and deduplicate by name
        seen_names: set[str] = set()
        merged: list[CodeConcept] = []

        # Prefer LLM concepts (richer descriptions)
        for concept in llm_concepts:
            if concept.name not in seen_names:
                seen_names.add(concept.name)
                merged.append(concept)

        # Add unique text concepts
        for concept in text_concepts:
            if concept.name not in seen_names:
                seen_names.add(concept.name)
                merged.append(concept)

        return merged

    def extract_strategies(
        self,
        trajectories: list[Trajectory],
    ) -> list[Strategy]:
        """Combine LLM and text extraction, deduplicate.

        Args:
            trajectories: List of trajectories to analyze.

        Returns:
            Merged and deduplicated list of Strategy objects.
        """
        llm_strategies = self._llm_extractor.extract_strategies(trajectories)
        text_strategies = self._text_extractor.extract_strategies(trajectories)

        # Merge and deduplicate by situation
        seen_situations: set[str] = set()
        merged: list[Strategy] = []

        # Prefer LLM strategies (richer descriptions)
        for strategy in llm_strategies:
            if strategy.situation not in seen_situations:
                seen_situations.add(strategy.situation)
                merged.append(strategy)

        # Add unique text strategies
        for strategy in text_strategies:
            if strategy.situation not in seen_situations:
                seen_situations.add(strategy.situation)
                merged.append(strategy)

        return merged


# =============================================================================
# Abstraction Extractor
# =============================================================================


class AbstractionExtractor:
    """Extracts reusable abstractions from trajectory batches.

    Coordinates pattern extraction and handles deduplication against
    existing knowledge in memory. Uses embedding similarity for
    deduplication.

    Example:
        ```python
        extractor = AbstractionExtractor(
            pattern_extractor=LLMPatternExtractor(llm),
            embedding_service=embedding_service,
        )
        new_concepts, new_strategies = extractor.extract_from_batch(
            trajectories,
            existing_concepts=memory.concepts,
            existing_strategies=memory.strategies,
        )
        ```
    """

    # Similarity threshold for deduplication (0.9 = very similar)
    DEDUP_THRESHOLD = 0.9

    def __init__(
        self,
        pattern_extractor: PatternExtractor,
        embedding_service: Any | None = None,
    ) -> None:
        """Initialize abstraction extractor.

        Args:
            pattern_extractor: Strategy for extracting patterns.
            embedding_service: Service for computing embeddings (for deduplication).
        """
        self._extractor = pattern_extractor
        self._embedding = embedding_service

    def extract_from_batch(
        self,
        trajectories: list[Trajectory],
        existing_concepts: list[CodeConcept] | None = None,
        existing_strategies: list[Strategy] | None = None,
    ) -> tuple[list[CodeConcept], list[Strategy]]:
        """Extract concepts and strategies from trajectory batch.

        Deduplicates against existing knowledge to avoid storing
        redundant patterns.

        Args:
            trajectories: Trajectories to extract patterns from.
            existing_concepts: Known concepts to deduplicate against.
            existing_strategies: Known strategies to deduplicate against.

        Returns:
            Tuple of (new_concepts, new_strategies) that are novel.
        """
        # Extract patterns
        new_concepts = self._extractor.extract_concepts(trajectories)
        new_strategies = self._extractor.extract_strategies(trajectories)

        # Deduplicate
        unique_concepts = self._deduplicate_concepts(new_concepts, existing_concepts)
        unique_strategies = self._deduplicate_strategies(
            new_strategies, existing_strategies
        )

        logger.info(
            f"Extracted {len(unique_concepts)} concepts, "
            f"{len(unique_strategies)} strategies "
            f"({len(new_concepts) - len(unique_concepts)} duplicate concepts, "
            f"{len(new_strategies) - len(unique_strategies)} duplicate strategies)"
        )

        return unique_concepts, unique_strategies

    def _deduplicate_concepts(
        self,
        new_concepts: list[CodeConcept],
        existing: list[CodeConcept] | None,
    ) -> list[CodeConcept]:
        """Remove concepts similar to existing ones.

        Uses embedding similarity if available, otherwise falls back
        to name-based deduplication.

        Args:
            new_concepts: Newly extracted concepts.
            existing: Existing concepts to check against.

        Returns:
            Concepts that are sufficiently novel.
        """
        if not existing:
            return new_concepts

        if self._embedding is None:
            # Fall back to name-based deduplication
            existing_names = {c.name.lower() for c in existing}
            return [c for c in new_concepts if c.name.lower() not in existing_names]

        # Use embedding similarity
        unique = []
        for concept in new_concepts:
            if not self._is_similar_to_existing_concept(concept, existing):
                unique.append(concept)

        return unique

    def _deduplicate_strategies(
        self,
        new_strategies: list[Strategy],
        existing: list[Strategy] | None,
    ) -> list[Strategy]:
        """Remove strategies similar to existing ones.

        Uses embedding similarity if available, otherwise falls back
        to situation-based deduplication.

        Args:
            new_strategies: Newly extracted strategies.
            existing: Existing strategies to check against.

        Returns:
            Strategies that are sufficiently novel.
        """
        if not existing:
            return new_strategies

        if self._embedding is None:
            # Fall back to situation-based deduplication
            existing_situations = {s.situation.lower() for s in existing}
            return [
                s for s in new_strategies if s.situation.lower() not in existing_situations
            ]

        # Use embedding similarity
        unique = []
        for strategy in new_strategies:
            if not self._is_similar_to_existing_strategy(strategy, existing):
                unique.append(strategy)

        return unique

    def _is_similar_to_existing_concept(
        self,
        concept: CodeConcept,
        existing: list[CodeConcept],
    ) -> bool:
        """Check if concept is similar to any existing concept.

        Args:
            concept: Concept to check.
            existing: List of existing concepts.

        Returns:
            True if similar to an existing concept.
        """
        # Compute embedding for new concept
        concept_text = f"{concept.name}: {concept.description}"
        try:
            concept_embedding = self._embedding.embed(concept_text)
        except Exception:
            return False

        # Check against existing
        for existing_concept in existing:
            existing_text = f"{existing_concept.name}: {existing_concept.description}"
            try:
                existing_embedding = self._embedding.embed(existing_text)
                similarity = self._cosine_similarity(
                    concept_embedding, existing_embedding
                )
                if similarity >= self.DEDUP_THRESHOLD:
                    return True
            except Exception:
                continue

        return False

    def _is_similar_to_existing_strategy(
        self,
        strategy: Strategy,
        existing: list[Strategy],
    ) -> bool:
        """Check if strategy is similar to any existing strategy.

        Args:
            strategy: Strategy to check.
            existing: List of existing strategies.

        Returns:
            True if similar to an existing strategy.
        """
        # Compute embedding for new strategy
        strategy_text = f"{strategy.situation} -> {strategy.suggestion}"
        try:
            strategy_embedding = self._embedding.embed(strategy_text)
        except Exception:
            return False

        # Check against existing
        for existing_strategy in existing:
            existing_text = (
                f"{existing_strategy.situation} -> {existing_strategy.suggestion}"
            )
            try:
                existing_embedding = self._embedding.embed(existing_text)
                similarity = self._cosine_similarity(
                    strategy_embedding, existing_embedding
                )
                if similarity >= self.DEDUP_THRESHOLD:
                    return True
            except Exception:
                continue

        return False

    def _cosine_similarity(
        self,
        vec1: Any,
        vec2: Any,
    ) -> float:
        """Compute cosine similarity between two vectors.

        Args:
            vec1: First vector (numpy array).
            vec2: Second vector (numpy array).

        Returns:
            Cosine similarity (0.0-1.0).
        """
        import numpy as np

        vec1 = np.asarray(vec1)
        vec2 = np.asarray(vec2)

        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(np.dot(vec1, vec2) / (norm1 * norm2))


# =============================================================================
# Factory Function
# =============================================================================


def create_extractor(
    config: LearningConfig,
    llm: SimpleLLM,
    embedding_service: Any | None = None,
) -> AbstractionExtractor:
    """Create AbstractionExtractor based on config.

    Factory function that creates the appropriate pattern extractor
    based on the configuration, then wraps it in an AbstractionExtractor.

    Args:
        config: Learning pipeline configuration.
        llm: LLM adapter for LLM-based extraction.
        embedding_service: Optional embedding service for deduplication.

    Returns:
        Configured AbstractionExtractor.

    Raises:
        ValueError: If unknown pattern extractor type is specified.

    Example:
        ```python
        config = LearningConfig(pattern_extractor="both")
        extractor = create_extractor(config, llm, embedding_service)
        concepts, strategies = extractor.extract_from_batch(trajectories)
        ```
    """
    if config.pattern_extractor == "llm":
        extractor: PatternExtractor = LLMPatternExtractor(llm)
    elif config.pattern_extractor == "text":
        extractor = TextPatternExtractor()
    elif config.pattern_extractor == "both":
        extractor = CombinedPatternExtractor(llm)
    else:
        raise ValueError(f"Unknown pattern extractor: {config.pattern_extractor}")

    return AbstractionExtractor(
        pattern_extractor=extractor,
        embedding_service=embedding_service,
    )
