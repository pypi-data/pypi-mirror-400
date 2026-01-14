"""SAGE-style hindsight learning for ATLAS.

HindsightLearner improves memory without fine-tuning. Instead of updating model
weights, we analyze trajectories and store improved examples in memory for
future in-context learning.

Key insights from SAGE:
- Memory improvement > weight updates for many tasks
- Hindsight can turn failures into valuable learning data
- Better examples in memory = better retrieval = better performance
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from cognitive_core.config import LearningConfig
from cognitive_core.core.types import AnalysisResult, Experience, Trajectory

if TYPE_CHECKING:
    from cognitive_core.protocols.llm import LLM
    from cognitive_core.protocols.memory import MemorySystem

logger = logging.getLogger("cognitive_core.learning.hindsight")


class HindsightLearner:
    """SAGE-style learning: improve memory, not weights.

    Instead of fine-tuning models, we:
    1. Analyze trajectory outcomes
    2. Generate improved examples using hindsight
    3. Store better examples in memory for future retrieval

    This enables in-context learning from accumulated experience without
    requiring model weight updates.

    Example:
        ```python
        learner = HindsightLearner(llm=llm, memory=memory_system)
        experiences = learner.learn_from_trajectory(trajectory, analysis)
        learner.update_memory(experiences)
        ```
    """

    def __init__(
        self,
        llm: LLM | None = None,
        memory: MemorySystem | None = None,
        config: LearningConfig | None = None,
    ) -> None:
        """Initialize HindsightLearner.

        Args:
            llm: Language model for generating hindsight examples.
                If None, only extracts examples from successful trajectories.
            memory: Memory system for storing experiences.
                If None, experiences are returned but not stored.
            config: Learning configuration. Uses defaults if not provided.
        """
        self._llm = llm
        self._memory = memory
        self._config = config or LearningConfig()
        self._accumulated: list[Trajectory] = []
        self._last_batch_time: datetime | None = None

    def learn_from_trajectory(
        self,
        trajectory: Trajectory,
        analysis: AnalysisResult,
    ) -> list[Experience]:
        """Generate improved examples from trajectory using hindsight.

        For successful trajectories:
        - Extract key decision points as positive examples
        - Optionally generate alternative approaches (for diversity)

        For failed trajectories:
        - Use hindsight to generate "what should have been done"
        - Create corrected examples

        Args:
            trajectory: The trajectory to learn from.
            analysis: Analysis result containing key steps and attribution.

        Returns:
            List of Experience objects to store in memory.
        """
        if trajectory.outcome.success:
            return self._learn_from_success(trajectory, analysis)
        else:
            return self._learn_from_failure(trajectory, analysis)

    def _learn_from_success(
        self,
        trajectory: Trajectory,
        analysis: AnalysisResult,
    ) -> list[Experience]:
        """Extract positive examples from successful trajectory.

        Identifies key steps from analysis and creates experiences
        for each key decision point.

        Args:
            trajectory: Successful trajectory.
            analysis: Analysis with key_steps and step_attribution.

        Returns:
            List of Experience objects from successful trajectory.
        """
        experiences: list[Experience] = []

        # Create main experience for the full trajectory
        main_exp = self._create_experience(
            trajectory=trajectory,
            task_input=trajectory.task.description,
            solution_output=self._extract_full_solution(trajectory),
            feedback="Successful completion",
            success=True,
            metadata={"source": "success", "type": "full_trajectory"},
        )
        experiences.append(main_exp)

        # Extract experiences for key steps
        for step_idx in analysis.key_steps:
            if step_idx < len(trajectory.steps):
                step = trajectory.steps[step_idx]
                attribution = (
                    analysis.step_attribution[step_idx]
                    if step_idx < len(analysis.step_attribution)
                    else 0.0
                )

                # Only create experience for high-attribution steps
                if attribution >= 0.3:
                    # Build context up to this step
                    context = self._build_step_context(trajectory, step_idx)

                    step_exp = self._create_experience(
                        trajectory=trajectory,
                        task_input=context,
                        solution_output=step.action,
                        feedback=f"Key step with attribution {attribution:.2f}",
                        success=True,
                        metadata={
                            "source": "success",
                            "type": "key_step",
                            "step_index": step_idx,
                            "attribution": attribution,
                        },
                    )
                    experiences.append(step_exp)

        # Optionally generate alternative successful approaches
        if self._llm is not None and len(analysis.key_steps) > 0:
            alternatives = self._generate_alternatives(trajectory, analysis)
            for alt in alternatives:
                alt_exp = self._create_experience(
                    trajectory=trajectory,
                    task_input=trajectory.task.description,
                    solution_output=alt["solution"],
                    feedback=alt.get("reasoning", "Alternative approach"),
                    success=True,
                    metadata={
                        "source": "hindsight",
                        "type": "alternative",
                        "generated": True,
                    },
                )
                experiences.append(alt_exp)

        return experiences

    def _learn_from_failure(
        self,
        trajectory: Trajectory,
        analysis: AnalysisResult,
    ) -> list[Experience]:
        """Generate corrected examples using hindsight.

        Analyzes what went wrong and uses LLM to generate corrected
        approaches, creating experiences with the correct solution.

        Args:
            trajectory: Failed trajectory.
            analysis: Analysis with error patterns and failure info.

        Returns:
            List of Experience objects with corrected examples.
        """
        experiences: list[Experience] = []

        # Store the failure as a negative example
        failure_exp = self._create_experience(
            trajectory=trajectory,
            task_input=trajectory.task.description,
            solution_output=self._extract_full_solution(trajectory),
            feedback=trajectory.outcome.error_info or "Failed",
            success=False,
            metadata={
                "source": "failure",
                "type": "negative_example",
                "error_patterns": [
                    p.get("name", "unknown") for p in analysis.error_patterns
                ],
            },
        )
        experiences.append(failure_exp)

        # Use LLM to generate corrected examples via hindsight
        if self._llm is not None:
            hindsight_examples = self._generate_hindsight_examples(
                trajectory, analysis
            )
            corrected_experiences = self._convert_to_experiences(
                trajectory, hindsight_examples
            )
            experiences.extend(corrected_experiences)

        return experiences

    def _generate_hindsight_examples(
        self,
        trajectory: Trajectory,
        analysis: AnalysisResult,
    ) -> list[dict[str, Any]]:
        """Use LLM to generate hindsight-improved examples.

        Prompts the LLM to analyze what went wrong and generate
        corrected approaches.

        Args:
            trajectory: The trajectory to analyze.
            analysis: Analysis result with error patterns.

        Returns:
            List of generated examples as dicts with 'solution' and 'reasoning'.
        """
        if self._llm is None:
            return []

        # Build the hindsight prompt
        task_desc = trajectory.task.description
        error_info = trajectory.outcome.error_info or "Unknown error"
        steps_taken = self._format_steps_for_prompt(trajectory)
        error_patterns = ", ".join(
            p.get("name", "unknown") for p in analysis.error_patterns
        ) or "none identified"

        prompt = f"""You are analyzing a failed task attempt to learn from the mistakes.

Task: {task_desc}

Steps taken (that failed):
{steps_taken}

Error: {error_info}
Identified error patterns: {error_patterns}

Given the outcome, what would have been a better approach? Provide a corrected solution that addresses the failure.

Respond with JSON in this exact format:
{{
    "corrected_solution": "The corrected approach/solution",
    "reasoning": "Brief explanation of what went wrong and why this approach is better",
    "key_insight": "The main lesson learned from this failure"
}}
"""

        try:
            response = self._llm.generate(prompt, temperature=0.2)

            # Parse JSON from response
            import json
            import re

            # Try to extract JSON
            json_match = re.search(r"\{[\s\S]*\}", response)
            if json_match:
                data = json.loads(json_match.group())
                return [
                    {
                        "solution": data.get("corrected_solution", ""),
                        "reasoning": data.get("reasoning", ""),
                        "key_insight": data.get("key_insight", ""),
                    }
                ]
        except Exception as e:
            logger.warning(
                "Failed to generate hindsight examples",
                extra={"error": str(e)},
            )

        return []

    def _generate_alternatives(
        self,
        trajectory: Trajectory,
        analysis: AnalysisResult,
    ) -> list[dict[str, Any]]:
        """Generate alternative successful approaches for diversity.

        Args:
            trajectory: Successful trajectory.
            analysis: Analysis result.

        Returns:
            List of alternative approaches as dicts.
        """
        if self._llm is None:
            return []

        task_desc = trajectory.task.description
        original_solution = self._extract_full_solution(trajectory)

        prompt = f"""Given a successful task completion, suggest an alternative approach that would also solve the task.

Task: {task_desc}

Original successful solution:
{original_solution}

Suggest a different but equally valid approach. Focus on diversity - a meaningfully different strategy.

Respond with JSON in this exact format:
{{
    "alternative_solution": "A different approach to solve the task",
    "reasoning": "Why this alternative approach would also work"
}}
"""

        try:
            response = self._llm.generate(prompt, temperature=0.7)

            import json
            import re

            json_match = re.search(r"\{[\s\S]*\}", response)
            if json_match:
                data = json.loads(json_match.group())
                return [
                    {
                        "solution": data.get("alternative_solution", ""),
                        "reasoning": data.get("reasoning", ""),
                    }
                ]
        except Exception as e:
            logger.warning(
                "Failed to generate alternatives",
                extra={"error": str(e)},
            )

        return []

    def _convert_to_experiences(
        self,
        trajectory: Trajectory,
        examples: list[dict[str, Any]],
    ) -> list[Experience]:
        """Convert raw examples to Experience objects.

        Args:
            trajectory: Source trajectory for context.
            examples: List of example dicts with 'solution' and 'reasoning'.

        Returns:
            List of Experience objects.
        """
        experiences: list[Experience] = []

        for example in examples:
            if not example.get("solution"):
                continue

            exp = self._create_experience(
                trajectory=trajectory,
                task_input=trajectory.task.description,
                solution_output=example["solution"],
                feedback=example.get("reasoning", "Generated via hindsight"),
                success=True,  # Hindsight examples are corrected/improved
                metadata={
                    "source": "hindsight",
                    "type": "corrected",
                    "generated": True,
                    "key_insight": example.get("key_insight", ""),
                },
            )
            experiences.append(exp)

        return experiences

    def _create_experience(
        self,
        trajectory: Trajectory,
        task_input: str,
        solution_output: str,
        feedback: str,
        success: bool,
        metadata: dict[str, Any],
    ) -> Experience:
        """Create an Experience object with proper ID and timestamp.

        Args:
            trajectory: Source trajectory.
            task_input: Task description or context.
            solution_output: The solution or action taken.
            feedback: Outcome or learning feedback.
            success: Whether this represents a successful approach.
            metadata: Additional metadata.

        Returns:
            New Experience object.
        """
        return Experience(
            id=f"exp-{uuid.uuid4().hex[:12]}",
            task_input=task_input,
            solution_output=solution_output,
            feedback=feedback,
            success=success,
            embedding=None,  # Will be computed by memory system
            trajectory_id=trajectory.task.id,
            timestamp=datetime.now(timezone.utc),
            metadata=metadata,
        )

    def update_memory(
        self,
        experiences: list[Experience],
    ) -> None:
        """Store new experiences in memory system.

        Args:
            experiences: List of experiences to store.
        """
        if self._memory is None:
            logger.warning("No memory system configured, experiences not stored")
            return

        exp_memory = self._memory.experience_memory
        if exp_memory is None:
            logger.warning("No experience memory available, experiences not stored")
            return

        # Note: The ExperienceMemory protocol expects Trajectory objects,
        # but we have Experience objects. We need to store them directly.
        # This depends on the memory implementation supporting direct Experience storage.
        # For now, we'll log what we would store.
        for exp in experiences:
            logger.info(
                "Would store experience",
                extra={
                    "experience_id": exp.id,
                    "success": exp.success,
                    "source": exp.metadata.get("source", "unknown"),
                },
            )

    def accumulate(self, trajectory: Trajectory) -> None:
        """Add trajectory to accumulator for batch learning.

        Args:
            trajectory: Trajectory to accumulate.
        """
        self._accumulated.append(trajectory)

    def should_finetune(self) -> bool:
        """Check if fine-tuning should run.

        For SAGE-style, always returns False.

        Returns:
            Always False for SAGE-style learning.
        """
        return False  # SAGE: no fine-tuning

    def should_run_batch(self) -> bool:
        """Check if batch learning should run.

        Checks:
        1. min_trajectories threshold met
        2. Optional time trigger (min_hours_since_last)
        3. Optional quality trigger (min_success_rate)

        Returns:
            True if batch learning should run.
        """
        if len(self._accumulated) < self._config.min_trajectories:
            return False

        # Time trigger
        if self._config.min_hours_since_last is not None:
            if self._last_batch_time is not None:
                hours = (
                    datetime.now(timezone.utc) - self._last_batch_time
                ).total_seconds() / 3600
                if hours < self._config.min_hours_since_last:
                    return False

        # Quality trigger
        if self._config.min_success_rate is not None:
            success_count = sum(1 for t in self._accumulated if t.outcome.success)
            success_rate = success_count / len(self._accumulated)
            if success_rate < self._config.min_success_rate:
                return False

        return True

    def prepare_training_data(
        self,
        trajectories: list[Trajectory] | None = None,
    ) -> dict[str, Any]:
        """Prepare SOAR-style training data.

        Formats trajectories into training examples for future
        fine-tuning support. Not used in SAGE mode but prepared
        for potential future use.

        Args:
            trajectories: Trajectories to process. Uses accumulated if None.

        Returns:
            Dict with 'sampling', 'refinement', and 'error' training data.
        """
        trajs = trajectories or self._accumulated

        sampling_data: list[dict[str, Any]] = []
        refinement_data: list[dict[str, Any]] = []
        error_data: list[dict[str, Any]] = []

        for traj in trajs:
            if traj.outcome.success:
                # Sampling: full solution (2x weight)
                sampling_data.append(
                    {
                        "input": self._format_task(traj.task),
                        "output": self._extract_full_solution(traj),
                        "weight": 2.0,
                    }
                )

                # Refinement: key steps (1.5x weight)
                for i, step in enumerate(traj.steps):
                    if self._is_key_step(traj, i):
                        refinement_data.append(
                            {
                                "input": self._build_step_context(traj, i),
                                "output": step.action,
                                "weight": 1.5,
                            }
                        )
            else:
                # Error: learn from failures (1x weight)
                if traj.outcome.error_info:
                    error_data.append(
                        {
                            "input": self._build_step_context(traj, len(traj.steps)),
                            "output": f"[ERROR] {traj.outcome.error_info}",
                            "weight": 1.0,
                        }
                    )

        return {
            "sampling": sampling_data,
            "refinement": refinement_data,
            "error": error_data,
        }

    def get_accumulated(self) -> list[Trajectory]:
        """Get accumulated trajectories.

        Returns:
            Copy of accumulated trajectories list.
        """
        return self._accumulated.copy()

    def clear_accumulated(self) -> None:
        """Clear accumulated trajectories after batch processing."""
        self._accumulated = []
        self._last_batch_time = datetime.now(timezone.utc)

    @property
    def accumulated_count(self) -> int:
        """Number of accumulated trajectories."""
        return len(self._accumulated)

    def prune_low_value_experiences(
        self,
        threshold: float = 0.3,
    ) -> int:
        """Remove low-value experiences from memory.

        Criteria for removal:
        - Low retrieval frequency
        - Superseded by better examples
        - Conflicting with high-success experiences

        Args:
            threshold: Success rate threshold below which to prune.

        Returns:
            Number of experiences pruned.
        """
        if self._memory is None:
            return 0

        exp_memory = self._memory.experience_memory
        if exp_memory is None:
            return 0

        # Use the prune method of ExperienceMemory
        return exp_memory.prune({"min_success_rate": threshold})

    # Helper methods

    def _extract_full_solution(self, trajectory: Trajectory) -> str:
        """Extract full solution from trajectory steps.

        Args:
            trajectory: The trajectory to extract from.

        Returns:
            Formatted solution string.
        """
        if not trajectory.steps:
            return ""

        # Combine all actions as the full solution
        actions = [step.action for step in trajectory.steps if step.action]
        return "\n".join(actions) if actions else trajectory.steps[-1].action

    def _build_step_context(self, trajectory: Trajectory, step_idx: int) -> str:
        """Build context string up to a specific step.

        Args:
            trajectory: The trajectory.
            step_idx: Index of the target step.

        Returns:
            Formatted context string.
        """
        context_parts = [f"Task: {trajectory.task.description}"]

        # Add previous steps as context
        for i in range(min(step_idx, len(trajectory.steps))):
            step = trajectory.steps[i]
            if step.thought:
                context_parts.append(f"Thought {i+1}: {step.thought}")
            context_parts.append(f"Action {i+1}: {step.action}")
            if step.observation:
                context_parts.append(f"Observation {i+1}: {step.observation}")

        return "\n".join(context_parts)

    def _format_steps_for_prompt(self, trajectory: Trajectory) -> str:
        """Format trajectory steps for LLM prompt.

        Args:
            trajectory: The trajectory to format.

        Returns:
            Formatted steps string.
        """
        lines = []
        for i, step in enumerate(trajectory.steps):
            if step.thought:
                lines.append(f"Step {i+1} thought: {step.thought}")
            lines.append(f"Step {i+1} action: {step.action}")
            if step.observation:
                lines.append(f"Step {i+1} observation: {step.observation}")

        return "\n".join(lines) if lines else "No steps recorded"

    def _format_task(self, task: Any) -> str:
        """Format task for training data.

        Args:
            task: Task object.

        Returns:
            Formatted task string.
        """
        return f"Task: {task.description}\nDomain: {task.domain}"

    def _is_key_step(self, trajectory: Trajectory, step_idx: int) -> bool:
        """Determine if a step is a key step for refinement data.

        Uses simple heuristics: first step, last step, or steps with
        significant observations.

        Args:
            trajectory: The trajectory.
            step_idx: Index of the step.

        Returns:
            True if this is a key step.
        """
        if step_idx >= len(trajectory.steps):
            return False

        # First and last steps are always key
        if step_idx == 0 or step_idx == len(trajectory.steps) - 1:
            return True

        # Steps with substantial observations are key
        step = trajectory.steps[step_idx]
        if step.observation and len(step.observation) > 100:
            return True

        # Steps with attribution scores are key
        if step.attribution_score is not None and step.attribution_score > 0.3:
            return True

        return False
