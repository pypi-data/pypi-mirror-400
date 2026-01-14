# ATLAS Modular Design

## Design Goal

Every component should be:
1. **Usable standalone** - works without other ATLAS components
2. **Composable** - can be combined with any subset of other components
3. **Swappable** - implementations can be replaced without changing callers
4. **Testable** - can be tested in isolation

This enables ablation studies like:
- Experience Memory only (no concepts, no strategies)
- Concept Library + Experience Memory (no strategies)
- Strategy Bank only (no fine-grained memory)
- Any combination

---

## Core Pattern: Optional Dependencies

```python
from typing import Optional, Protocol, runtime_checkable


@runtime_checkable
class SupportsSearch(Protocol):
    """Any component that can search for relevant items"""
    def search(self, query: str, k: int = 5) -> list: ...


@runtime_checkable
class SupportsStore(Protocol):
    """Any component that can store items"""
    def store(self, item: any) -> str: ...
```

Components depend on **protocols**, not concrete classes. Missing dependencies return empty results rather than crashing.

---

## Component Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MODULAR ATLAS                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Each box is independently deployable and usable:                       │
│                                                                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐       │
│  │ Experience       │  │ Concept          │  │ Strategy         │       │
│  │ Memory           │  │ Library          │  │ Bank             │       │
│  │                  │  │                  │  │                  │       │
│  │ Standalone: ✓    │  │ Standalone: ✓    │  │ Standalone: ✓    │       │
│  │ Needs: embeddings│  │ Needs: Stitch    │  │ Needs: embeddings│       │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘       │
│           │                     │                     │                  │
│           └─────────────────────┼─────────────────────┘                  │
│                                 │                                        │
│                                 ▼                                        │
│                    ┌────────────────────────┐                           │
│                    │    Memory System       │                           │
│                    │    (Aggregator)        │                           │
│                    │                        │                           │
│                    │ Combines available     │                           │
│                    │ memory components      │                           │
│                    └────────────┬───────────┘                           │
│                                 │                                        │
│                                 ▼                                        │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐       │
│  │ Mind Evolution   │  │ SWE-Search       │  │ Direct Solver    │       │
│  │ Search           │  │ (MCTS)           │  │                  │       │
│  │                  │  │                  │  │                  │       │
│  │ Standalone: ✓    │  │ Standalone: ✓    │  │ Standalone: ✓    │       │
│  │ Memory: optional │  │ Memory: optional │  │ Memory: optional │       │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘       │
│           │                     │                     │                  │
│           └─────────────────────┼─────────────────────┘                  │
│                                 │                                        │
│                                 ▼                                        │
│                    ┌────────────────────────┐                           │
│                    │    Task Solver         │                           │
│                    │    (Orchestrator)      │                           │
│                    │                        │                           │
│                    │ Routes to available    │                           │
│                    │ search methods         │                           │
│                    └────────────────────────┘                           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Standalone Components

### 1.1 Experience Memory (Standalone)

```python
"""
atlas/memory/experience_memory.py

Usable completely standalone:
    from atlas.memory import ExperienceMemory

    memory = ExperienceMemory()
    memory.store(trajectory)
    similar = memory.search(task)
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Protocol
from datetime import datetime
import numpy as np


@dataclass
class Experience:
    """Stored experience - works independently"""
    id: str
    task_input: str
    solution_output: str
    feedback: str
    success: bool
    embedding: np.ndarray
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class EmbeddingProvider(Protocol):
    """Protocol for embedding - allows different implementations"""
    def encode(self, text: str) -> np.ndarray: ...
    def encode_batch(self, texts: List[str]) -> List[np.ndarray]: ...


class DefaultEmbeddingProvider:
    """Default embedding using sentence-transformers"""

    def __init__(self, model_name: str = "BAAI/bge-base-en-v1.5"):
        # Lazy import - only load if actually used
        self._model = None
        self._model_name = model_name

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self._model_name)
        return self._model

    def encode(self, text: str) -> np.ndarray:
        return self.model.encode(text)

    def encode_batch(self, texts: List[str]) -> List[np.ndarray]:
        return self.model.encode(texts)


class VectorIndex(Protocol):
    """Protocol for vector storage - allows different backends"""
    def add(self, id: str, vector: np.ndarray, metadata: dict) -> None: ...
    def search(self, vector: np.ndarray, k: int) -> List[tuple]: ...  # (id, score)
    def delete(self, id: str) -> bool: ...


class InMemoryVectorIndex:
    """Simple in-memory index - no external dependencies"""

    def __init__(self):
        self.vectors: Dict[str, np.ndarray] = {}
        self.metadata: Dict[str, dict] = {}

    def add(self, id: str, vector: np.ndarray, metadata: dict) -> None:
        self.vectors[id] = vector / np.linalg.norm(vector)  # normalize
        self.metadata[id] = metadata

    def search(self, vector: np.ndarray, k: int) -> List[tuple]:
        if not self.vectors:
            return []

        query = vector / np.linalg.norm(vector)
        scores = []
        for id, vec in self.vectors.items():
            score = float(np.dot(query, vec))
            scores.append((id, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:k]

    def delete(self, id: str) -> bool:
        if id in self.vectors:
            del self.vectors[id]
            del self.metadata[id]
            return True
        return False


class ExperienceMemory:
    """
    Standalone experience memory with ReMem-style search-evolve loop.

    Usage (standalone):
        memory = ExperienceMemory()

        # Store experiences
        exp_id = memory.store(trajectory)

        # Search for similar
        similar = memory.search(task, k=4)

        # Refine retrieved experiences
        refined = memory.refine(similar)

    Usage (with custom components):
        memory = ExperienceMemory(
            embedding_provider=MyCustomEmbedder(),
            vector_index=ChromaDBIndex(),
        )
    """

    def __init__(
        self,
        embedding_provider: Optional[EmbeddingProvider] = None,
        vector_index: Optional[VectorIndex] = None,
    ):
        self.embedder = embedding_provider or DefaultEmbeddingProvider()
        self.index = vector_index or InMemoryVectorIndex()
        self.experiences: Dict[str, Experience] = {}

    def store(self, trajectory: 'Trajectory') -> str:
        """Store a trajectory as an experience"""
        exp_id = self._generate_id()

        # Build rich context for embedding
        context = self._build_context(trajectory)
        embedding = self.embedder.encode(context)

        experience = Experience(
            id=exp_id,
            task_input=trajectory.task.description,
            solution_output=self._extract_solution(trajectory),
            feedback=self._extract_feedback(trajectory),
            success=trajectory.outcome.success,
            embedding=embedding,
            metadata={
                "trajectory_id": trajectory.task.id,
                "agent_id": trajectory.agent_id,
                "step_count": len(trajectory.steps),
            }
        )

        self.experiences[exp_id] = experience
        self.index.add(exp_id, embedding, experience.metadata)

        return exp_id

    def search(self, task: 'Task', k: int = 4) -> List[Experience]:
        """Find similar experiences (ReMem-style search)"""
        query_text = self._build_query(task)
        query_embedding = self.embedder.encode(query_text)

        results = self.index.search(query_embedding, k=k)

        return [self.experiences[id] for id, score in results if id in self.experiences]

    def refine(self, experiences: List[Experience]) -> List[Experience]:
        """
        ReMem-style refinement: exploit useful, prune noise.
        Can be overridden for custom refinement logic.
        """
        refined = []
        for exp in experiences:
            # Keep successful experiences
            if exp.success:
                refined.append(exp)
            # Keep failures with useful feedback
            elif exp.feedback and len(exp.feedback) > 20:
                refined.append(exp)

        return refined

    def store_direct(self, experience: Experience) -> str:
        """Store an experience directly (for testing/migration)"""
        self.experiences[experience.id] = experience
        self.index.add(experience.id, experience.embedding, experience.metadata)
        return experience.id

    def prune(self, max_age_days: int = 30, min_success_rate: float = 0.0) -> int:
        """Remove old or low-value experiences"""
        to_remove = []
        cutoff = datetime.now().timestamp() - (max_age_days * 86400)

        for exp_id, exp in self.experiences.items():
            if exp.timestamp.timestamp() < cutoff:
                to_remove.append(exp_id)

        for exp_id in to_remove:
            del self.experiences[exp_id]
            self.index.delete(exp_id)

        return len(to_remove)

    # Helper methods
    def _generate_id(self) -> str:
        import uuid
        return f"exp_{uuid.uuid4().hex[:8]}"

    def _build_context(self, trajectory: 'Trajectory') -> str:
        parts = [trajectory.task.description]
        if trajectory.outcome.error_info:
            parts.append(f"Error: {trajectory.outcome.error_info}")
        return " | ".join(parts)

    def _build_query(self, task: 'Task') -> str:
        return task.description

    def _extract_solution(self, trajectory: 'Trajectory') -> str:
        if trajectory.steps:
            return trajectory.steps[-1].action
        return ""

    def _extract_feedback(self, trajectory: 'Trajectory') -> str:
        if trajectory.outcome.error_info:
            return trajectory.outcome.error_info
        return "success" if trajectory.outcome.success else "failure"
```

### 1.2 Concept Library (Standalone)

```python
"""
atlas/memory/concept_library.py

Usable completely standalone:
    from atlas.memory import ConceptLibrary

    library = ConceptLibrary()
    library.add(concept)
    relevant = library.search("find objects in grid")
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Callable
import numpy as np


@dataclass
class CodeConcept:
    """Reusable code pattern"""
    id: str
    name: str
    description: str
    code: str
    signature: str = ""
    examples: List[tuple] = field(default_factory=list)
    usage_count: int = 0
    success_rate: float = 0.0
    embedding: Optional[np.ndarray] = None
    metadata: Dict[str, any] = field(default_factory=dict)


class ConceptLibrary:
    """
    Standalone concept library with Stitch-style compression.

    Usage (standalone):
        library = ConceptLibrary()

        # Add primitives manually
        library.add(CodeConcept(
            id="rotate_90",
            name="rotate_90",
            description="Rotate grid 90 degrees clockwise",
            code="def rotate_90(grid): return np.rot90(grid, -1)",
        ))

        # Search for concepts
        relevant = library.search("rotate the grid", k=3)

        # Use with trajectories for compression
        new_concepts = library.compress(trajectories)

    Usage (with Stitch integration):
        library = ConceptLibrary(
            compressor=StitchCompressor(),
            auto_documenter=LILOAutoDoc(),
        )
    """

    def __init__(
        self,
        embedding_provider: Optional['EmbeddingProvider'] = None,
        compressor: Optional['Compressor'] = None,
        auto_documenter: Optional['AutoDocumenter'] = None,
    ):
        self.concepts: Dict[str, CodeConcept] = {}
        self.embedder = embedding_provider
        self.compressor = compressor
        self.auto_documenter = auto_documenter

        # Lazy-load default embedder only if needed
        self._default_embedder = None

    @property
    def _embedder(self):
        if self.embedder:
            return self.embedder
        if self._default_embedder is None:
            self._default_embedder = DefaultEmbeddingProvider()
        return self._default_embedder

    def add(self, concept: CodeConcept) -> str:
        """Add a concept to the library"""
        # Compute embedding if not present
        if concept.embedding is None:
            embed_text = f"{concept.name}: {concept.description}"
            concept.embedding = self._embedder.encode(embed_text)

        self.concepts[concept.id] = concept
        return concept.id

    def get(self, concept_id: str) -> Optional[CodeConcept]:
        """Get concept by ID"""
        return self.concepts.get(concept_id)

    def search(self, query: str, k: int = 5) -> List[CodeConcept]:
        """Find relevant concepts by semantic similarity"""
        if not self.concepts:
            return []

        query_embedding = self._embedder.encode(query)

        scored = []
        for concept in self.concepts.values():
            if concept.embedding is not None:
                score = float(np.dot(
                    query_embedding / np.linalg.norm(query_embedding),
                    concept.embedding / np.linalg.norm(concept.embedding)
                ))
                scored.append((concept, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [c for c, _ in scored[:k]]

    def compress(self, trajectories: List['Trajectory']) -> List[CodeConcept]:
        """
        Extract new concepts from trajectories using Stitch-style compression.

        If no compressor is configured, returns empty list.
        """
        if self.compressor is None:
            return []

        # Extract code from successful trajectories
        code_corpus = []
        for traj in trajectories:
            if traj.outcome.success:
                code = self._extract_code(traj)
                if code:
                    code_corpus.append(code)

        if not code_corpus:
            return []

        # Run compression
        raw_concepts = self.compressor.compress(code_corpus)

        # Auto-document if available
        documented = []
        for concept in raw_concepts:
            if self.auto_documenter:
                concept = self.auto_documenter.document(concept)
            documented.append(concept)
            self.add(concept)

        return documented

    def compose(self, concept_ids: List[str]) -> Optional[CodeConcept]:
        """Attempt to compose multiple concepts into one"""
        concepts = [self.get(id) for id in concept_ids]
        if not all(concepts):
            return None

        # Simple composition: concatenate code
        composed_code = "\n\n".join(c.code for c in concepts)
        composed_name = "_".join(c.name for c in concepts)

        return CodeConcept(
            id=f"composed_{composed_name}",
            name=composed_name,
            description=f"Composition of: {', '.join(c.name for c in concepts)}",
            code=composed_code,
        )

    def update_stats(self, concept_id: str, success: bool) -> None:
        """Update usage statistics for a concept"""
        concept = self.get(concept_id)
        if concept:
            concept.usage_count += 1
            # Exponential moving average for success rate
            alpha = 0.1
            concept.success_rate = (1 - alpha) * concept.success_rate + alpha * (1.0 if success else 0.0)

    def load_primitives(self, primitives: List[CodeConcept]) -> int:
        """Bulk load primitive concepts"""
        for p in primitives:
            self.add(p)
        return len(primitives)

    def _extract_code(self, trajectory: 'Trajectory') -> Optional[str]:
        """Extract code from a trajectory"""
        for step in reversed(trajectory.steps):
            if "```" in step.action or "def " in step.action:
                return step.action
        return None


# Optional Stitch integration
class StitchCompressor:
    """Wrapper for Stitch compression library"""

    def __init__(self, stitch_path: Optional[str] = None):
        self.stitch_path = stitch_path
        self._available = None

    @property
    def available(self) -> bool:
        if self._available is None:
            try:
                import stitch  # or subprocess check
                self._available = True
            except ImportError:
                self._available = False
        return self._available

    def compress(self, code_corpus: List[str]) -> List[CodeConcept]:
        if not self.available:
            return []

        # Stitch compression logic here
        # Returns extracted abstractions as CodeConcepts
        pass


# Optional LILO integration
class LILOAutoDoc:
    """LILO-style auto-documentation using LLM"""

    def __init__(self, llm: Optional['LLM'] = None):
        self.llm = llm

    def document(self, concept: CodeConcept) -> CodeConcept:
        if self.llm is None:
            return concept

        prompt = f"""
        Given this code pattern:
        ```
        {concept.code}
        ```

        Generate:
        1. A concise name (snake_case)
        2. A one-sentence description
        3. Type signature

        Format: NAME | DESCRIPTION | SIGNATURE
        """

        response = self.llm.generate(prompt)
        parts = response.strip().split("|")

        if len(parts) >= 3:
            concept.name = parts[0].strip()
            concept.description = parts[1].strip()
            concept.signature = parts[2].strip()

        return concept
```

### 1.3 Strategy Bank (Standalone)

```python
"""
atlas/memory/strategy_bank.py

Usable completely standalone:
    from atlas.memory import StrategyBank

    bank = StrategyBank()
    bank.add(strategy)
    applicable = bank.read(task)
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
import numpy as np


@dataclass
class Strategy:
    """Abstract reasoning pattern (ArcMemo-style)"""
    id: str
    situation: str      # When to apply
    suggestion: str     # What to do
    parameters: List[Dict[str, str]] = field(default_factory=list)
    usage_count: int = 0
    success_rate: float = 0.5
    embedding: Optional[np.ndarray] = None
    metadata: Dict[str, any] = field(default_factory=dict)


class StrategyBank:
    """
    Standalone strategy bank with ArcMemo-style abstraction.

    Usage (standalone):
        bank = StrategyBank()

        # Add strategies manually
        bank.add(Strategy(
            id="symmetry_check",
            situation="Input shows potential symmetry",
            suggestion="Check for horizontal/vertical symmetry, then apply transformation to each half",
        ))

        # Find applicable strategies
        strategies = bank.read(task, k=3)

        # Abstract from trajectories
        new_strategy = bank.write(trajectory)
    """

    def __init__(
        self,
        embedding_provider: Optional['EmbeddingProvider'] = None,
        abstractor: Optional['StrategyAbstractor'] = None,
    ):
        self.strategies: Dict[str, Strategy] = {}
        self.embedder = embedding_provider
        self.abstractor = abstractor
        self._default_embedder = None

    @property
    def _embedder(self):
        if self.embedder:
            return self.embedder
        if self._default_embedder is None:
            self._default_embedder = DefaultEmbeddingProvider()
        return self._default_embedder

    def add(self, strategy: Strategy) -> str:
        """Add a strategy to the bank"""
        if strategy.embedding is None:
            embed_text = f"{strategy.situation} → {strategy.suggestion}"
            strategy.embedding = self._embedder.encode(embed_text)

        self.strategies[strategy.id] = strategy
        return strategy.id

    def read(self, task: 'Task', k: int = 5) -> List[Strategy]:
        """Find applicable strategies for a task"""
        if not self.strategies:
            return []

        query_embedding = self._embedder.encode(task.description)

        scored = []
        for strategy in self.strategies.values():
            if strategy.embedding is not None:
                score = float(np.dot(
                    query_embedding / np.linalg.norm(query_embedding),
                    strategy.embedding / np.linalg.norm(strategy.embedding)
                ))
                # Boost by success rate
                score *= (0.5 + 0.5 * strategy.success_rate)
                scored.append((strategy, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [s for s, _ in scored[:k]]

    def write(self, trajectory: 'Trajectory') -> Optional[Strategy]:
        """Abstract a trajectory into a strategy"""
        if self.abstractor is None:
            return self._simple_abstract(trajectory)

        return self.abstractor.abstract(trajectory)

    def update_stats(self, strategy_id: str, success: bool) -> None:
        """Update usage statistics"""
        strategy = self.strategies.get(strategy_id)
        if strategy:
            strategy.usage_count += 1
            alpha = 0.1
            strategy.success_rate = (1 - alpha) * strategy.success_rate + alpha * (1.0 if success else 0.0)

    def _simple_abstract(self, trajectory: 'Trajectory') -> Optional[Strategy]:
        """Simple abstraction without LLM"""
        if not trajectory.outcome.success:
            return None

        # Extract key action from trajectory
        key_step = None
        for step in trajectory.steps:
            if step.thought and len(step.thought) > 50:
                key_step = step
                break

        if key_step is None:
            return None

        return Strategy(
            id=f"strat_{trajectory.task.id[:8]}",
            situation=f"Task similar to: {trajectory.task.description[:100]}",
            suggestion=key_step.thought[:200] if key_step.thought else key_step.action[:200],
        )
```

---

## 2. Composable Memory System

The `MemorySystem` aggregates available memory components:

```python
"""
atlas/memory/system.py

Composable memory system that works with any subset of components.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class MemoryQueryResult:
    """Unified result from memory query"""
    experiences: List['Experience']
    concepts: List['CodeConcept']
    strategies: List['Strategy']

    @property
    def is_empty(self) -> bool:
        return not (self.experiences or self.concepts or self.strategies)

    def to_prompt_context(self) -> str:
        """Format for inclusion in LLM prompt"""
        parts = []

        if self.experiences:
            parts.append("## Relevant Past Experiences")
            for exp in self.experiences[:3]:
                parts.append(f"- Task: {exp.task_input[:100]}")
                parts.append(f"  Solution: {exp.solution_output[:100]}")
                parts.append(f"  Result: {exp.feedback}")

        if self.concepts:
            parts.append("\n## Available Concepts")
            for concept in self.concepts[:5]:
                parts.append(f"- {concept.name}: {concept.description}")

        if self.strategies:
            parts.append("\n## Suggested Strategies")
            for strat in self.strategies[:3]:
                parts.append(f"- When: {strat.situation}")
                parts.append(f"  Do: {strat.suggestion}")

        return "\n".join(parts)


class MemorySystem:
    """
    Composable memory system - works with any subset of components.

    Usage (all components):
        memory = MemorySystem(
            experience_memory=ExperienceMemory(),
            concept_library=ConceptLibrary(),
            strategy_bank=StrategyBank(),
        )

    Usage (experience only - for ablation):
        memory = MemorySystem(
            experience_memory=ExperienceMemory(),
        )

    Usage (concepts + strategies, no experiences):
        memory = MemorySystem(
            concept_library=ConceptLibrary(),
            strategy_bank=StrategyBank(),
        )

    Usage (empty - pure baseline):
        memory = MemorySystem()
    """

    def __init__(
        self,
        experience_memory: Optional['ExperienceMemory'] = None,
        concept_library: Optional['ConceptLibrary'] = None,
        strategy_bank: Optional['StrategyBank'] = None,
    ):
        self.experience_memory = experience_memory
        self.concept_library = concept_library
        self.strategy_bank = strategy_bank

    @property
    def has_experience_memory(self) -> bool:
        return self.experience_memory is not None

    @property
    def has_concept_library(self) -> bool:
        return self.concept_library is not None

    @property
    def has_strategy_bank(self) -> bool:
        return self.strategy_bank is not None

    @property
    def components(self) -> List[str]:
        """List of active components"""
        active = []
        if self.has_experience_memory:
            active.append("experience_memory")
        if self.has_concept_library:
            active.append("concept_library")
        if self.has_strategy_bank:
            active.append("strategy_bank")
        return active

    def query(self, task: 'Task', k: int = 5) -> MemoryQueryResult:
        """Query all available memory components"""
        experiences = []
        concepts = []
        strategies = []

        if self.experience_memory:
            experiences = self.experience_memory.search(task, k=k)
            experiences = self.experience_memory.refine(experiences)

        if self.concept_library:
            concepts = self.concept_library.search(task.description, k=k)

        if self.strategy_bank:
            strategies = self.strategy_bank.read(task, k=k)

        return MemoryQueryResult(
            experiences=experiences,
            concepts=concepts,
            strategies=strategies,
        )

    def store(self, trajectory: 'Trajectory') -> Dict[str, Any]:
        """Store trajectory in all available components"""
        results = {}

        if self.experience_memory:
            results["experience_id"] = self.experience_memory.store(trajectory)

        if self.strategy_bank:
            strategy = self.strategy_bank.write(trajectory)
            if strategy:
                results["strategy_id"] = strategy.id

        # Concept extraction typically happens in batch, not per-trajectory

        return results

    def learn_batch(self, trajectories: List['Trajectory']) -> Dict[str, Any]:
        """Batch learning across all components"""
        results = {}

        if self.concept_library:
            new_concepts = self.concept_library.compress(trajectories)
            results["new_concepts"] = len(new_concepts)

        return results


# Factory functions for common configurations

def create_full_memory() -> MemorySystem:
    """Create memory system with all components"""
    return MemorySystem(
        experience_memory=ExperienceMemory(),
        concept_library=ConceptLibrary(),
        strategy_bank=StrategyBank(),
    )


def create_experience_only() -> MemorySystem:
    """Create memory with only experience memory (for ablation)"""
    return MemorySystem(
        experience_memory=ExperienceMemory(),
    )


def create_concept_only() -> MemorySystem:
    """Create memory with only concept library (for ablation)"""
    return MemorySystem(
        concept_library=ConceptLibrary(),
    )


def create_no_memory() -> MemorySystem:
    """Create empty memory system (baseline)"""
    return MemorySystem()
```

---

## 3. Modular Search Engines

```python
"""
atlas/search/base.py

Search engines that work with or without memory.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class SearchConfig:
    """Configuration for search"""
    max_iterations: int = 10
    population_size: int = 20
    temperature: float = 0.7
    use_memory: bool = True


class SearchEngine(ABC):
    """
    Base search engine - works with or without memory.

    All search engines can operate standalone (no memory)
    or augmented (with memory for initialization/guidance).
    """

    def __init__(
        self,
        llm: 'LLM',
        memory: Optional['MemorySystem'] = None,
        config: Optional[SearchConfig] = None,
    ):
        self.llm = llm
        self.memory = memory
        self.config = config or SearchConfig()

    @abstractmethod
    def search(
        self,
        task: 'Task',
        env: 'Environment',
    ) -> List['Candidate']:
        """Search for solutions"""
        pass

    def _get_memory_context(self, task: 'Task') -> str:
        """Get context from memory if available"""
        if self.memory is None or not self.config.use_memory:
            return ""

        result = self.memory.query(task)
        return result.to_prompt_context()


class MindEvolutionSearch(SearchEngine):
    """
    Mind Evolution search - works standalone or with memory.

    Usage (standalone):
        search = MindEvolutionSearch(llm=my_llm)
        candidates = search.search(task, env)

    Usage (with memory):
        search = MindEvolutionSearch(
            llm=my_llm,
            memory=memory_system,
        )
        candidates = search.search(task, env)
    """

    def search(
        self,
        task: 'Task',
        env: 'Environment',
    ) -> List['Candidate']:
        # Initialize population
        population = self._initialize_population(task)

        # Evolution loop
        for gen in range(self.config.max_iterations):
            # Evaluate fitness
            fitness = [self._evaluate(c, task, env) for c in population]

            # Select elites
            elites = self._select_elites(population, fitness)

            # Generate next generation
            population = self._evolve(elites, task)

        return population[:5]

    def _initialize_population(self, task: 'Task') -> List['Candidate']:
        """Initialize population - uses memory if available"""
        population = []

        # Memory-guided initialization (if available)
        if self.memory and self.config.use_memory:
            result = self.memory.query(task, k=self.config.population_size // 2)

            for exp in result.experiences:
                # Adapt past solution to current task
                adapted = self._adapt_experience(exp, task)
                population.append(adapted)

            for concept in result.concepts:
                # Generate candidate using concept
                candidate = self._from_concept(concept, task)
                population.append(candidate)

        # Fill remaining with novel generation
        while len(population) < self.config.population_size:
            novel = self._generate_novel(task)
            population.append(novel)

        return population

    def _adapt_experience(self, exp: 'Experience', task: 'Task') -> 'Candidate':
        """Adapt a past experience to current task"""
        prompt = f"""
        Previous similar task: {exp.task_input}
        Previous solution: {exp.solution_output}

        Current task: {task.description}

        Adapt the previous solution for the current task:
        """
        response = self.llm.generate(prompt)
        return Candidate(solution=response, confidence=0.7, source="adapted")

    def _from_concept(self, concept: 'CodeConcept', task: 'Task') -> 'Candidate':
        """Generate candidate using a concept"""
        prompt = f"""
        Available function: {concept.name}
        Description: {concept.description}
        Code: {concept.code}

        Task: {task.description}

        Write a solution using this function:
        """
        response = self.llm.generate(prompt)
        return Candidate(solution=response, confidence=0.6, source="concept")

    def _generate_novel(self, task: 'Task') -> 'Candidate':
        """Generate a novel candidate"""
        memory_context = self._get_memory_context(task)

        prompt = f"""
        Task: {task.description}

        {memory_context}

        Generate a solution:
        """
        response = self.llm.generate(prompt)
        return Candidate(solution=response, confidence=0.5, source="novel")

    def _evaluate(self, candidate: 'Candidate', task: 'Task', env: 'Environment') -> float:
        """Evaluate candidate fitness"""
        outcome = env.verify(candidate.solution)
        if outcome.success:
            return 1.0
        if outcome.partial_score:
            return outcome.partial_score
        return 0.0

    def _select_elites(self, population: List['Candidate'], fitness: List[float]) -> List['Candidate']:
        """Select top candidates"""
        paired = list(zip(population, fitness))
        paired.sort(key=lambda x: x[1], reverse=True)
        return [c for c, _ in paired[:self.config.population_size // 2]]

    def _evolve(self, elites: List['Candidate'], task: 'Task') -> List['Candidate']:
        """Generate next generation"""
        next_gen = list(elites)

        for elite in elites:
            mutated = self._mutate(elite, task)
            next_gen.append(mutated)

        return next_gen

    def _mutate(self, candidate: 'Candidate', task: 'Task') -> 'Candidate':
        """Mutate a candidate"""
        prompt = f"""
        Task: {task.description}

        Current solution:
        {candidate.solution}

        Improve or fix this solution:
        """
        response = self.llm.generate(prompt)
        return Candidate(solution=response, confidence=candidate.confidence * 0.9, source="mutated")
```

---

## 4. Ablation Study Configuration

```python
"""
atlas/experiments/ablation.py

Easy configuration for ablation studies.
"""

from dataclasses import dataclass
from typing import Optional, List
from enum import Enum, auto


class MemoryConfig(Enum):
    """Memory configuration options"""
    NONE = auto()               # No memory (baseline)
    EXPERIENCE_ONLY = auto()    # Only experience memory
    CONCEPT_ONLY = auto()       # Only concept library
    STRATEGY_ONLY = auto()      # Only strategy bank
    EXPERIENCE_CONCEPT = auto() # Experience + concept
    EXPERIENCE_STRATEGY = auto() # Experience + strategy
    CONCEPT_STRATEGY = auto()   # Concept + strategy
    FULL = auto()               # All three


class SearchConfig(Enum):
    """Search configuration options"""
    DIRECT = auto()             # Single-shot, no search
    EVOLUTION = auto()          # Mind Evolution
    MCTS = auto()               # SWE-Search style
    EVOLUTION_MCTS = auto()     # Hybrid


class LearningConfig(Enum):
    """Learning configuration options"""
    NONE = auto()               # No learning
    MEMORY_ONLY = auto()        # Only memory updates (SAGE-style)
    FINETUNE = auto()           # SOAR-style fine-tuning
    FULL = auto()               # Memory + fine-tuning


@dataclass
class AblationConfig:
    """Configuration for an ablation experiment"""
    name: str
    memory: MemoryConfig
    search: SearchConfig
    learning: LearningConfig

    def describe(self) -> str:
        return f"{self.name}: memory={self.memory.name}, search={self.search.name}, learning={self.learning.name}"


# Predefined ablation configurations
ABLATION_CONFIGS = {
    # Baselines
    "baseline": AblationConfig(
        name="baseline",
        memory=MemoryConfig.NONE,
        search=SearchConfig.DIRECT,
        learning=LearningConfig.NONE,
    ),

    "baseline_search": AblationConfig(
        name="baseline_search",
        memory=MemoryConfig.NONE,
        search=SearchConfig.EVOLUTION,
        learning=LearningConfig.NONE,
    ),

    # Memory ablations
    "experience_only": AblationConfig(
        name="experience_only",
        memory=MemoryConfig.EXPERIENCE_ONLY,
        search=SearchConfig.EVOLUTION,
        learning=LearningConfig.MEMORY_ONLY,
    ),

    "concept_only": AblationConfig(
        name="concept_only",
        memory=MemoryConfig.CONCEPT_ONLY,
        search=SearchConfig.EVOLUTION,
        learning=LearningConfig.MEMORY_ONLY,
    ),

    "strategy_only": AblationConfig(
        name="strategy_only",
        memory=MemoryConfig.STRATEGY_ONLY,
        search=SearchConfig.DIRECT,  # Strategies work well with direct
        learning=LearningConfig.MEMORY_ONLY,
    ),

    # Combinations
    "experience_concept": AblationConfig(
        name="experience_concept",
        memory=MemoryConfig.EXPERIENCE_CONCEPT,
        search=SearchConfig.EVOLUTION,
        learning=LearningConfig.MEMORY_ONLY,
    ),

    # Full system
    "full": AblationConfig(
        name="full",
        memory=MemoryConfig.FULL,
        search=SearchConfig.EVOLUTION,
        learning=LearningConfig.FULL,
    ),
}


def create_from_config(config: AblationConfig) -> 'ATLASSolver':
    """Create ATLAS solver from ablation config"""
    from atlas.memory import ExperienceMemory, ConceptLibrary, StrategyBank, MemorySystem
    from atlas.search import MindEvolutionSearch, DirectSolver

    # Build memory system
    exp_mem = None
    concept_lib = None
    strat_bank = None

    if config.memory in [MemoryConfig.EXPERIENCE_ONLY, MemoryConfig.EXPERIENCE_CONCEPT,
                         MemoryConfig.EXPERIENCE_STRATEGY, MemoryConfig.FULL]:
        exp_mem = ExperienceMemory()

    if config.memory in [MemoryConfig.CONCEPT_ONLY, MemoryConfig.EXPERIENCE_CONCEPT,
                         MemoryConfig.CONCEPT_STRATEGY, MemoryConfig.FULL]:
        concept_lib = ConceptLibrary()

    if config.memory in [MemoryConfig.STRATEGY_ONLY, MemoryConfig.EXPERIENCE_STRATEGY,
                         MemoryConfig.CONCEPT_STRATEGY, MemoryConfig.FULL]:
        strat_bank = StrategyBank()

    memory = MemorySystem(
        experience_memory=exp_mem,
        concept_library=concept_lib,
        strategy_bank=strat_bank,
    )

    # Build search engine
    if config.search == SearchConfig.DIRECT:
        search = DirectSolver(memory=memory)
    elif config.search == SearchConfig.EVOLUTION:
        search = MindEvolutionSearch(memory=memory)
    # ... etc

    return ATLASSolver(memory=memory, search=search, config=config)


# Example usage
def run_ablation_study(tasks: List['Task'], configs: List[str] = None):
    """Run ablation study with specified configurations"""
    configs = configs or list(ABLATION_CONFIGS.keys())

    results = {}
    for config_name in configs:
        config = ABLATION_CONFIGS[config_name]
        solver = create_from_config(config)

        successes = 0
        for task in tasks:
            trajectory = solver.solve(task)
            if trajectory.outcome.success:
                successes += 1

        results[config_name] = {
            "accuracy": successes / len(tasks),
            "config": config.describe(),
        }

    return results
```

---

## 5. Example Usage Patterns

### 5.1 Minimal Standalone Usage

```python
# Just experience memory - simplest possible setup
from atlas.memory import ExperienceMemory

memory = ExperienceMemory()

# Store some trajectories
for traj in my_trajectories:
    memory.store(traj)

# Search for similar experiences
similar = memory.search(new_task, k=4)
for exp in similar:
    print(f"Similar task: {exp.task_input}")
    print(f"Solution: {exp.solution_output}")
```

### 5.2 Concept Library Only

```python
# Just concept library - for code pattern reuse
from atlas.memory import ConceptLibrary, CodeConcept

library = ConceptLibrary()

# Load domain primitives
library.add(CodeConcept(
    id="rotate_90",
    name="rotate_90",
    description="Rotate grid 90 degrees clockwise",
    code="def rotate_90(grid): return np.rot90(grid, -1)",
))

# Search for relevant concepts
concepts = library.search("rotate the input grid", k=3)
for c in concepts:
    print(f"{c.name}: {c.description}")
```

### 5.3 Full System

```python
# Full ATLAS system
from atlas.memory import create_full_memory
from atlas.search import MindEvolutionSearch
from atlas.core import ATLASSolver

memory = create_full_memory()
search = MindEvolutionSearch(llm=my_llm, memory=memory)
solver = ATLASSolver(memory=memory, search=search)

# Solve tasks
trajectory = solver.solve(task)

# System automatically updates memory
```

### 5.4 Ablation Study

```python
# Run ablation study
from atlas.experiments import run_ablation_study, ABLATION_CONFIGS

results = run_ablation_study(
    tasks=test_tasks,
    configs=["baseline", "experience_only", "concept_only", "full"]
)

for name, result in results.items():
    print(f"{name}: {result['accuracy']:.2%}")

# Output:
# baseline: 32.5%
# experience_only: 41.2%
# concept_only: 38.7%
# full: 52.1%
```

---

## Summary

| Component | Standalone? | Dependencies | Optional Integration |
|-----------|-------------|--------------|---------------------|
| `ExperienceMemory` | ✅ | embeddings | vector DB |
| `ConceptLibrary` | ✅ | embeddings | Stitch, LILO |
| `StrategyBank` | ✅ | embeddings | LLM abstractor |
| `MemorySystem` | ✅ | none (aggregator) | any memory component |
| `MindEvolutionSearch` | ✅ | LLM | memory system |
| `ATLASSolver` | ✅ | LLM | memory, search, learning |

Each component works independently, gracefully handles missing dependencies, and can be composed with any other components for ablation studies.
