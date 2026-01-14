# ATLAS: Adaptive Trajectory Learning and Abstraction System

## A Unified Meta-Learning Framework for ARC-AGI and Software Engineering Tasks

---

## 1. Executive Summary

This document specifies **ATLAS** (Adaptive Trajectory Learning and Abstraction System), a domain-agnostic meta-learning framework that:

1. **Extracts learning signals from agent trajectories** produced by existing tools (Claude Code, Codex, SWE-agent, OpenHands)
2. **Builds and maintains three types of memory** (Concept Library, Experience Memory, Strategy Bank)
3. **Enables self-improvement** through hindsight learning on successful and failed trajectories
4. **Generalizes across domains** while allowing domain-specific adaptation

The core insight: **The trajectory is the curriculum.** Rather than designing tasks, we let agents attempt tasks and learn from the resulting trajectories.

---

## 2. Literature Synthesis: Key SWE Findings

### 2.1 Critical Papers Identified

| Paper | Key Contribution | Relevance |
|-------|-----------------|-----------|
| **SWE-Gym** (Pan et al., 2025) | First training environment with executable verification; 491 trajectories → +14% gains | Training environment design |
| **SAGE** (Salesforce, 2025) | Plan induction from self-experience; training-free self-improvement | Experience abstraction |
| **SWE-Search** (ICLR 2025) | MCTS + self-improvement; 23% relative improvement | Search with self-evaluation |
| **SOAR** (ICML 2025) | Self-improving evolutionary program synthesis; 52% ARC-AGI | Self-improvement loop |
| **AgentTrek** (ICLR 2025 Spotlight) | Trajectory synthesis via guided replay; $0.55/trajectory | Trajectory generation |
| **Stitch/LILO** (POPL 2023) | Library learning 3-4 orders of magnitude faster than DreamCoder | Efficient abstraction |
| **Voyager** (2023) | Ever-growing skill library in Minecraft | Compositional skill learning |

### 2.2 Key Insights for Framework Design

1. **Trajectory quality matters more than quantity**
   - SWE-Gym: 491 high-quality trajectories → +14% improvement
   - SOAR: Success + failure traces both useful for learning

2. **Self-improvement is achievable but fragile**
   - SWE-Gym found "self-improvement is not yet working" with naive approaches
   - SAGE shows training-free plan induction works
   - SOAR demonstrates iterative fine-tuning can work with proper setup

3. **Abstraction level determines transfer**
   - ArcMemo: Concept-level > instance-level at ALL compute scales
   - LILO: Auto-documentation helps LLM interpret abstractions
   - Voyager: Compositional skills compound capabilities

4. **Verification enables scaling**
   - SWE-Gym: Verifier enables inference-time scaling (10% → 13.3% with best-of-8)
   - SWE-Search: Value function + discriminator for solution quality

---

## 3. Framework Architecture

### 3.1 High-Level Design

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              ATLAS FRAMEWORK                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────────┐ │
│  │                         TRAJECTORY COLLECTOR                                │ │
│  │                                                                              │ │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │ │
│  │   │ Claude Code │  │   Codex     │  │  OpenHands  │  │  SWE-agent  │       │ │
│  │   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘       │ │
│  │          │                │                │                │               │ │
│  │          └────────────────┴────────────────┴────────────────┘               │ │
│  │                                    │                                         │ │
│  │                                    ▼                                         │ │
│  │                    ┌───────────────────────────────┐                        │ │
│  │                    │    Unified Trajectory Format   │                        │ │
│  │                    │    (Task, Steps, Outcome)      │                        │ │
│  │                    └───────────────────────────────┘                        │ │
│  └────────────────────────────────────┬───────────────────────────────────────┘ │
│                                       │                                          │
│                                       ▼                                          │
│  ┌────────────────────────────────────────────────────────────────────────────┐ │
│  │                         MEMORY SYSTEMS                                      │ │
│  │                                                                              │ │
│  │  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐            │ │
│  │  │  CONCEPT LIBRARY │ │ EXPERIENCE MEMORY│ │  STRATEGY BANK   │            │ │
│  │  │                  │ │                  │ │                  │            │ │
│  │  │ • Code patterns  │ │ • Task embeddings│ │ • Abstract plans │            │ │
│  │  │ • Compositions   │ │ • Solution traces│ │ • Situation→Action│           │ │
│  │  │ • Error→Fix maps │ │ • Failure modes  │ │ • Typed procedures│           │ │
│  │  │ • Stitch/LILO    │ │ • Evo-Memory     │ │ • ArcMemo style  │            │ │
│  │  └────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘            │ │
│  │           └────────────────────┼────────────────────┘                       │ │
│  │                                │                                             │ │
│  └────────────────────────────────┼───────────────────────────────────────────┘ │
│                                   │                                              │
│                                   ▼                                              │
│  ┌────────────────────────────────────────────────────────────────────────────┐ │
│  │                         LEARNING ENGINE                                     │ │
│  │                                                                              │ │
│  │  ┌────────────────────┐    ┌────────────────────┐    ┌──────────────────┐  │ │
│  │  │ TRAJECTORY ANALYSIS│    │  ABSTRACTION       │    │ HINDSIGHT        │  │ │
│  │  │                    │    │  EXTRACTION        │    │ LEARNING         │  │ │
│  │  │ • Success/Failure  │───▶│                    │───▶│                  │  │ │
│  │  │ • Step attribution │    │ • Pattern mining   │    │ • Fine-tune data │  │ │
│  │  │ • Error analysis   │    │ • Stitch compress  │    │ • SOAR-style     │  │ │
│  │  │                    │    │ • AutoDoc naming   │    │ • Curriculum     │  │ │
│  │  └────────────────────┘    └────────────────────┘    └──────────────────┘  │ │
│  │                                                                              │ │
│  └────────────────────────────────────────────────────────────────────────────┘ │
│                                   │                                              │
│                                   ▼                                              │
│  ┌────────────────────────────────────────────────────────────────────────────┐ │
│  │                         TASK SOLVER                                         │ │
│  │                                                                              │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │ │
│  │  │   ROUTER    │  │  SEARCH     │  │ VERIFIER    │  │  EXECUTOR   │        │ │
│  │  │             │──▶│  ENGINE    │──▶│             │──▶│             │        │ │
│  │  │ Memory query│  │ Mind Evol. │  │ ORM/Tests   │  │ Agent call  │        │ │
│  │  │ Similarity  │  │ MCTS hybrid│  │ Confidence  │  │ Tool exec   │        │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │ │
│  │                                                                              │ │
│  └────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Core Interfaces (Domain-Agnostic)

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum

# ============================================================================
# CORE DATA STRUCTURES
# ============================================================================

class TaskDomain(Enum):
    ARC_AGI = "arc_agi"
    SOFTWARE_ENGINEERING = "swe"
    # Extensible to other domains

@dataclass
class Task:
    """Domain-agnostic task representation"""
    id: str
    domain: TaskDomain
    description: str                    # Natural language description
    context: Dict[str, Any]             # Domain-specific context
    verification: 'VerificationSpec'    # How to verify success
    
@dataclass
class Step:
    """Single step in a trajectory"""
    thought: Optional[str]              # Agent's reasoning (if available)
    action: str                         # Action taken
    observation: str                    # Result/feedback
    metadata: Dict[str, Any]            # Tool calls, timing, etc.

@dataclass
class Trajectory:
    """Complete trajectory for a task attempt"""
    task: Task
    steps: List[Step]
    outcome: 'Outcome'
    agent_id: str                       # Which agent produced this
    timestamp: str
    
@dataclass
class Outcome:
    """Result of a trajectory"""
    success: bool
    partial_score: Optional[float]      # 0-1 for partial credit
    error_info: Optional[str]           # If failed, why
    verification_details: Dict[str, Any]

# ============================================================================
# MEMORY INTERFACES
# ============================================================================

class Concept(ABC):
    """Base class for learned concepts"""
    id: str
    name: str
    description: str
    usage_count: int
    success_rate: float
    
class CodeConcept(Concept):
    """Reusable code pattern"""
    code: str
    signature: str                      # Type signature
    examples: List[Tuple[str, str]]     # (input, output) examples
    
class StrategyConcept(Concept):
    """Abstract reasoning pattern"""
    situation: str                      # When to apply
    suggestion: str                     # What to do
    parameters: List[Dict[str, str]]    # Typed parameters (PS format)

class ConceptLibrary(ABC):
    """Interface for concept storage and retrieval"""
    
    @abstractmethod
    def add(self, concept: Concept) -> str:
        """Add a new concept, returns ID"""
        pass
    
    @abstractmethod
    def search(self, query: str, k: int = 5) -> List[Concept]:
        """Find relevant concepts"""
        pass
    
    @abstractmethod
    def compose(self, concept_ids: List[str]) -> Optional[Concept]:
        """Attempt to compose concepts"""
        pass
    
    @abstractmethod
    def compress(self, trajectories: List[Trajectory]) -> List[Concept]:
        """Extract new concepts from trajectories (Stitch-style)"""
        pass

class ExperienceMemory(ABC):
    """Interface for trajectory-level memory"""
    
    @abstractmethod
    def store(self, trajectory: Trajectory) -> str:
        """Store a trajectory, returns ID"""
        pass
    
    @abstractmethod
    def search(self, task: Task, k: int = 5) -> List[Trajectory]:
        """Find similar past experiences"""
        pass
    
    @abstractmethod
    def prune(self, criteria: Dict[str, Any]) -> int:
        """Remove low-value experiences, returns count removed"""
        pass

class StrategyBank(ABC):
    """Interface for abstract strategy storage"""
    
    @abstractmethod
    def write(self, trajectory: Trajectory) -> Optional[StrategyConcept]:
        """Abstract a trajectory into a strategy"""
        pass
    
    @abstractmethod
    def read(self, task: Task, k: int = 5) -> List[StrategyConcept]:
        """Find applicable strategies"""
        pass

# ============================================================================
# LEARNING ENGINE INTERFACES
# ============================================================================

class TrajectoryAnalyzer(ABC):
    """Analyze trajectories to extract learning signals"""
    
    @abstractmethod
    def analyze(self, trajectory: Trajectory) -> 'AnalysisResult':
        """Full analysis of a trajectory"""
        pass
    
    @abstractmethod
    def attribute_outcome(self, trajectory: Trajectory) -> List[Tuple[int, float]]:
        """Credit assignment: which steps contributed to outcome"""
        pass
    
    @abstractmethod
    def extract_error_patterns(self, trajectories: List[Trajectory]) -> List[Dict]:
        """Find common error patterns across failed trajectories"""
        pass

@dataclass
class AnalysisResult:
    """Result of trajectory analysis"""
    success: bool
    key_steps: List[int]                # Indices of critical steps
    learned_patterns: List[Concept]
    error_patterns: List[Dict]
    abstracted_strategy: Optional[StrategyConcept]
    training_examples: List[Dict]       # For fine-tuning

class AbstractionExtractor(ABC):
    """Extract reusable abstractions from trajectories"""
    
    @abstractmethod
    def extract_code_patterns(self, trajectories: List[Trajectory]) -> List[CodeConcept]:
        """Find reusable code patterns (Stitch/LILO style)"""
        pass
    
    @abstractmethod
    def extract_strategies(self, trajectories: List[Trajectory]) -> List[StrategyConcept]:
        """Find reusable reasoning patterns (ArcMemo style)"""
        pass
    
    @abstractmethod
    def auto_document(self, concept: Concept) -> Concept:
        """Generate human-readable documentation (LILO AutoDoc)"""
        pass

class HindsightLearner(ABC):
    """Learn from trajectories to improve future performance"""
    
    @abstractmethod
    def prepare_training_data(self, trajectories: List[Trajectory]) -> Dict:
        """Convert trajectories to training format"""
        pass
    
    @abstractmethod
    def should_finetune(self) -> bool:
        """Check if enough data accumulated for fine-tuning"""
        pass
    
    @abstractmethod
    def finetune(self, training_data: Dict) -> 'FinetuneResult':
        """Execute fine-tuning (SOAR-style)"""
        pass

# ============================================================================
# TASK SOLVER INTERFACES
# ============================================================================

class TaskRouter(ABC):
    """Route tasks based on memory and similarity"""
    
    @abstractmethod
    def route(self, task: Task) -> 'RoutingDecision':
        """Decide how to approach a task"""
        pass

@dataclass
class RoutingDecision:
    """How to approach a task"""
    strategy: str                       # "direct", "search", "adapt"
    relevant_concepts: List[Concept]
    similar_experiences: List[Trajectory]
    suggested_strategies: List[StrategyConcept]
    estimated_difficulty: float
    search_budget: int                  # Max iterations/samples

class SearchEngine(ABC):
    """Search for solutions (evolutionary, MCTS, or hybrid)"""
    
    @abstractmethod
    def search(self, task: Task, routing: RoutingDecision) -> List['Candidate']:
        """Search for candidate solutions"""
        pass
    
    @abstractmethod
    def refine(self, candidate: 'Candidate', feedback: str) -> 'Candidate':
        """Refine a candidate based on feedback"""
        pass

@dataclass
class Candidate:
    """A candidate solution"""
    solution: Any                       # Domain-specific solution
    confidence: float
    reasoning: str
    source: str                         # "generated", "adapted", "retrieved"

class Verifier(ABC):
    """Verify candidate solutions"""
    
    @abstractmethod
    def verify(self, task: Task, candidate: Candidate) -> Outcome:
        """Verify a candidate solution"""
        pass
    
    @abstractmethod
    def rank(self, task: Task, candidates: List[Candidate]) -> List[Tuple[Candidate, float]]:
        """Rank candidates by estimated quality"""
        pass
```

### 3.3 Domain Adapters

```python
# ============================================================================
# ARC-AGI DOMAIN ADAPTER
# ============================================================================

class ARCTask(Task):
    """ARC-AGI specific task"""
    training_examples: List[Tuple[np.ndarray, np.ndarray]]
    test_input: np.ndarray
    expected_output: Optional[np.ndarray]  # None during evaluation

class ARCVerifier(Verifier):
    """ARC-AGI verification: exact grid match"""
    
    def verify(self, task: ARCTask, candidate: Candidate) -> Outcome:
        # Execute the candidate code
        try:
            transform_fn = self._compile(candidate.solution)
            
            # Verify on training examples first
            for inp, out in task.training_examples:
                result = transform_fn(inp)
                if not np.array_equal(result, out):
                    return Outcome(
                        success=False,
                        partial_score=self._partial_score(result, out),
                        error_info=f"Failed on training example",
                        verification_details={"expected": out, "got": result}
                    )
            
            # Apply to test input
            test_result = transform_fn(task.test_input)
            
            if task.expected_output is not None:
                success = np.array_equal(test_result, task.expected_output)
            else:
                success = None  # Unknown during real evaluation
                
            return Outcome(
                success=success,
                partial_score=1.0 if success else None,
                verification_details={"output": test_result}
            )
            
        except Exception as e:
            return Outcome(
                success=False,
                error_info=str(e),
                verification_details={"exception": type(e).__name__}
            )

class ARCConceptLibrary(ConceptLibrary):
    """ARC-specific concept library with grid primitives"""
    
    def __init__(self):
        self.primitives = self._load_base_primitives()
        self.learned = {}
        
    def _load_base_primitives(self) -> Dict[str, CodeConcept]:
        """Load fundamental ARC operations"""
        return {
            "get_objects": CodeConcept(
                id="get_objects",
                name="get_objects",
                description="Extract connected components from grid",
                code="def get_objects(grid): ...",
                signature="(np.ndarray) -> List[Object]",
                examples=[],
                usage_count=0,
                success_rate=0.0
            ),
            "flood_fill": CodeConcept(...),
            "rotate_90": CodeConcept(...),
            "mirror_horizontal": CodeConcept(...),
            "get_background_color": CodeConcept(...),
            # ... more primitives
        }
    
    def compress(self, trajectories: List[Trajectory]) -> List[CodeConcept]:
        """Use Stitch-style compression to find new abstractions"""
        # Extract successful code from trajectories
        successful_code = [
            t.steps[-1].action  # Assuming final step is the solution
            for t in trajectories
            if t.outcome.success
        ]
        
        # Run Stitch compression
        abstractions = self._run_stitch(successful_code)
        
        # Auto-document with LLM
        documented = [self._auto_document(a) for a in abstractions]
        
        return documented

# ============================================================================
# SOFTWARE ENGINEERING DOMAIN ADAPTER  
# ============================================================================

class SWETask(Task):
    """Software Engineering specific task"""
    repository: str
    issue_description: str
    test_commands: List[str]
    relevant_files: List[str]
    docker_image: Optional[str]

class SWEVerifier(Verifier):
    """SWE verification: run tests"""
    
    def verify(self, task: SWETask, candidate: Candidate) -> Outcome:
        # Apply the patch
        patch = candidate.solution
        
        # Run in sandboxed environment
        with self._create_sandbox(task.docker_image) as sandbox:
            # Apply patch
            apply_result = sandbox.run(f"git apply --check", input=patch)
            if apply_result.returncode != 0:
                return Outcome(
                    success=False,
                    error_info="Patch does not apply cleanly",
                    verification_details={"stderr": apply_result.stderr}
                )
            
            sandbox.run(f"git apply", input=patch)
            
            # Run tests
            test_results = []
            for cmd in task.test_commands:
                result = sandbox.run(cmd, timeout=300)
                test_results.append({
                    "command": cmd,
                    "passed": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                })
            
            all_passed = all(t["passed"] for t in test_results)
            
            return Outcome(
                success=all_passed,
                partial_score=sum(t["passed"] for t in test_results) / len(test_results),
                verification_details={"test_results": test_results}
            )

class SWETrajectoryCollector:
    """Collect trajectories from existing SWE agents"""
    
    def __init__(self, agents: Dict[str, Any]):
        self.agents = agents  # {"claude_code": ..., "openhands": ..., etc}
    
    def collect_from_agent(
        self, 
        agent_id: str, 
        task: SWETask,
        max_steps: int = 50
    ) -> Trajectory:
        """Run an agent and collect its trajectory"""
        agent = self.agents[agent_id]
        
        steps = []
        for step_result in agent.run(task, max_steps=max_steps):
            steps.append(Step(
                thought=step_result.get("thought"),
                action=step_result["action"],
                observation=step_result["observation"],
                metadata={
                    "tool": step_result.get("tool"),
                    "duration": step_result.get("duration"),
                }
            ))
        
        # Verify outcome
        final_patch = self._extract_patch(steps)
        outcome = self.verifier.verify(task, Candidate(solution=final_patch, confidence=1.0, reasoning="", source="agent"))
        
        return Trajectory(
            task=task,
            steps=steps,
            outcome=outcome,
            agent_id=agent_id,
            timestamp=datetime.now().isoformat()
        )
```

---

## 4. Learning Pipeline

### 4.1 Trajectory Processing Pipeline

```python
class ATLASLearningPipeline:
    """Main learning pipeline for ATLAS"""
    
    def __init__(
        self,
        concept_library: ConceptLibrary,
        experience_memory: ExperienceMemory,
        strategy_bank: StrategyBank,
        analyzer: TrajectoryAnalyzer,
        abstractor: AbstractionExtractor,
        hindsight_learner: HindsightLearner,
    ):
        self.concept_library = concept_library
        self.experience_memory = experience_memory
        self.strategy_bank = strategy_bank
        self.analyzer = analyzer
        self.abstractor = abstractor
        self.hindsight_learner = hindsight_learner
        
        # Buffers
        self.trajectory_buffer: List[Trajectory] = []
        self.pending_finetune_data: List[Dict] = []
    
    def process_trajectory(self, trajectory: Trajectory) -> Dict[str, Any]:
        """Process a single trajectory through the full pipeline"""
        results = {}
        
        # 1. Store in experience memory
        exp_id = self.experience_memory.store(trajectory)
        results["experience_id"] = exp_id
        
        # 2. Analyze trajectory
        analysis = self.analyzer.analyze(trajectory)
        results["analysis"] = analysis
        
        # 3. Extract and store strategy (if successful or informative failure)
        if analysis.abstracted_strategy:
            self.strategy_bank.write(trajectory)
            results["strategy_extracted"] = True
        
        # 4. Add to trajectory buffer for batch processing
        self.trajectory_buffer.append(trajectory)
        
        # 5. Collect training examples for hindsight learning
        self.pending_finetune_data.extend(analysis.training_examples)
        
        return results
    
    def run_batch_learning(self, min_trajectories: int = 50) -> Dict[str, Any]:
        """Run batch learning on accumulated trajectories"""
        if len(self.trajectory_buffer) < min_trajectories:
            return {"status": "insufficient_data", "count": len(self.trajectory_buffer)}
        
        results = {}
        
        # 1. Extract new concepts using Stitch compression
        new_concepts = self.abstractor.extract_code_patterns(self.trajectory_buffer)
        for concept in new_concepts:
            documented = self.abstractor.auto_document(concept)
            self.concept_library.add(documented)
        results["new_concepts"] = len(new_concepts)
        
        # 2. Extract new strategies
        new_strategies = self.abstractor.extract_strategies(self.trajectory_buffer)
        results["new_strategies"] = len(new_strategies)
        
        # 3. Check if we should fine-tune
        if self.hindsight_learner.should_finetune():
            training_data = self.hindsight_learner.prepare_training_data(
                self.trajectory_buffer
            )
            finetune_result = self.hindsight_learner.finetune(training_data)
            results["finetuned"] = True
            results["finetune_result"] = finetune_result
        
        # 4. Prune low-value experiences
        pruned = self.experience_memory.prune({
            "min_success_rate": 0.1,
            "max_age_days": 30,
            "keep_diverse": True
        })
        results["pruned_experiences"] = pruned
        
        # 5. Clear buffer
        self.trajectory_buffer = []
        
        return results
```

### 4.2 SOAR-Style Hindsight Learning Implementation

```python
class SOARHindsightLearner(HindsightLearner):
    """SOAR-style self-improvement through hindsight learning"""
    
    def __init__(
        self,
        base_model: str,
        min_trajectories_for_finetune: int = 100,
        finetune_interval_hours: int = 24,
    ):
        self.base_model = base_model
        self.min_trajectories = min_trajectories_for_finetune
        self.finetune_interval = timedelta(hours=finetune_interval_hours)
        self.last_finetune = datetime.now()
        self.accumulated_data = []
        
    def prepare_training_data(self, trajectories: List[Trajectory]) -> Dict:
        """
        Convert trajectories to training format.
        Key insight from SOAR: separate sampling and refinement data.
        """
        sampling_data = []      # Learning to generate good initial solutions
        refinement_data = []    # Learning to refine based on feedback
        
        for traj in trajectories:
            task_context = self._format_task(traj.task)
            
            if traj.outcome.success:
                # For successful trajectories: learn the solution directly
                sampling_data.append({
                    "input": task_context,
                    "output": self._extract_solution(traj),
                    "type": "success"
                })
                
                # Also learn from intermediate steps that led to success
                for i, step in enumerate(traj.steps):
                    if self._is_key_step(traj, i):
                        refinement_data.append({
                            "input": task_context + self._format_history(traj.steps[:i]),
                            "output": step.action,
                            "type": "key_step"
                        })
            else:
                # For failed trajectories: learn what NOT to do, or error recovery
                if traj.outcome.error_info:
                    # If there was a clear error, learn to avoid it
                    refinement_data.append({
                        "input": task_context + self._format_history(traj.steps),
                        "output": f"[ERROR] {traj.outcome.error_info}. Should have: ...",
                        "type": "error_recovery"
                    })
        
        return {
            "sampling": sampling_data,
            "refinement": refinement_data,
            "metadata": {
                "total_trajectories": len(trajectories),
                "successful": sum(1 for t in trajectories if t.outcome.success),
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def finetune(self, training_data: Dict) -> 'FinetuneResult':
        """
        Execute fine-tuning following SOAR methodology:
        1. Fine-tune on sampling data (improves initial generation)
        2. Fine-tune on refinement data (improves error recovery)
        """
        # Combine with appropriate weighting
        combined_data = []
        
        # Weight successful examples higher
        for example in training_data["sampling"]:
            combined_data.append({
                **example,
                "weight": 2.0 if example["type"] == "success" else 1.0
            })
        
        for example in training_data["refinement"]:
            combined_data.append({
                **example,
                "weight": 1.5 if example["type"] == "key_step" else 1.0
            })
        
        # Execute fine-tuning (implementation depends on infrastructure)
        result = self._execute_finetune(combined_data)
        
        self.last_finetune = datetime.now()
        
        return result
```

### 4.3 Stitch-Style Concept Compression

```python
class StitchAbstractionExtractor(AbstractionExtractor):
    """
    Stitch-style compression for extracting reusable concepts.
    Key insight: 3-4 orders of magnitude faster than DreamCoder.
    """
    
    def extract_code_patterns(self, trajectories: List[Trajectory]) -> List[CodeConcept]:
        """Extract common code patterns using corpus-guided top-down synthesis"""
        
        # 1. Extract all code snippets from successful trajectories
        code_corpus = []
        for traj in trajectories:
            if traj.outcome.success:
                code_corpus.extend(self._extract_code_snippets(traj))
        
        if not code_corpus:
            return []
        
        # 2. Parse into AST representation
        ast_corpus = [self._parse_to_ast(code) for code in code_corpus]
        
        # 3. Find common subtrees (Stitch algorithm)
        common_patterns = self._find_common_subtrees(ast_corpus)
        
        # 4. Score patterns by compression benefit
        scored_patterns = []
        for pattern in common_patterns:
            score = self._compression_score(pattern, ast_corpus)
            if score > self.min_compression_threshold:
                scored_patterns.append((pattern, score))
        
        # 5. Convert to CodeConcepts
        concepts = []
        for pattern, score in sorted(scored_patterns, key=lambda x: -x[1])[:self.max_concepts]:
            concept = self._pattern_to_concept(pattern)
            concepts.append(concept)
        
        return concepts
    
    def auto_document(self, concept: Concept) -> Concept:
        """
        Generate human-readable documentation using LLM.
        Key insight from LILO: AutoDoc helps the synthesizer interpret abstractions.
        """
        prompt = f"""
        Given this code pattern extracted from successful solutions:
        
        ```python
        {concept.code}
        ```
        
        And these example usages:
        {self._format_examples(concept.examples)}
        
        Generate:
        1. A concise, descriptive name (snake_case)
        2. A one-sentence description
        3. Type signature
        4. When to use this pattern
        
        Format:
        NAME: ...
        DESCRIPTION: ...
        SIGNATURE: ...
        USE_WHEN: ...
        """
        
        response = self.llm.generate(prompt)
        parsed = self._parse_autodoc_response(response)
        
        concept.name = parsed["name"]
        concept.description = parsed["description"]
        concept.signature = parsed["signature"]
        
        return concept
```

---

## 5. Training Curriculum Design

### 5.1 Playground Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ATLAS TRAINING PLAYGROUND                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    PHASE 1: WARM-UP (Weeks 1-2)                      │    │
│  │                                                                       │    │
│  │  ARC-AGI                          SWE                                │    │
│  │  ├── ARC-AGI-1 Training Set       ├── HumanEval                     │    │
│  │  │   (400 easy-medium tasks)      │   (164 function synthesis)      │    │
│  │  ├── ConceptARC                   ├── MBPP                          │    │
│  │  │   (labeled by concept)         │   (974 basic problems)          │    │
│  │  └── RE-ARC synthetic             └── CodeContests (easy)           │    │
│  │                                                                       │    │
│  │  Goal: Build base library, understand task formats                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                   │                                          │
│                                   ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    PHASE 2: CORE TRAINING (Weeks 3-6)                │    │
│  │                                                                       │    │
│  │  ARC-AGI                          SWE                                │    │
│  │  ├── ARC-AGI-1 Full               ├── SWE-Gym (2,438 tasks)         │    │
│  │  │   (800 tasks)                  │   with executable verification  │    │
│  │  ├── BARC synthetic               ├── SWE-bench Lite               │    │
│  │  │   (100K+ augmented)            │   (300 real issues)             │    │
│  │  └── 1D-ARC                       └── DevBench                      │    │
│  │      (simplified subset)              (end-to-end tasks)            │    │
│  │                                                                       │    │
│  │  Goal: Main capability building, self-improvement loops              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                   │                                          │
│                                   ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    PHASE 3: CHALLENGE (Weeks 7-8)                    │    │
│  │                                                                       │    │
│  │  ARC-AGI                          SWE                                │    │
│  │  ├── ARC-AGI-2                    ├── SWE-bench Verified            │    │
│  │  │   (harder tasks)               │   (500 curated)                  │    │
│  │  ├── Semi-private eval set        ├── SWE-rebench                   │    │
│  │  │   (if available)               │   (monthly fresh issues)        │    │
│  │  └── Novel synthetic tasks        └── Multi-SWE-bench              │    │
│  │                                       (multi-language)              │    │
│  │                                                                       │    │
│  │  Goal: Test generalization, identify gaps                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                   │                                          │
│                                   ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    PHASE 4: ADAPTATION (Ongoing)                     │    │
│  │                                                                       │    │
│  │  Domain-Specific Fine-Tuning                                         │    │
│  │  ├── Specific repository patterns (for SWE)                         │    │
│  │  ├── Specific task families (for ARC)                               │    │
│  │  └── User-provided examples                                          │    │
│  │                                                                       │    │
│  │  Goal: Specialize for target deployment                              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Benchmark Details

```python
class TrainingCurriculum:
    """Curriculum definition for ATLAS training"""
    
    # =========================================================================
    # ARC-AGI BENCHMARKS
    # =========================================================================
    
    ARC_BENCHMARKS = {
        "phase1": {
            "arc_agi_1_training": {
                "description": "Original ARC-AGI training set",
                "size": 400,
                "difficulty": "easy-medium",
                "source": "https://github.com/fchollet/ARC-AGI",
                "format": "json",
            },
            "conceptarc": {
                "description": "ARC tasks labeled by concept (rotation, color, etc.)",
                "size": 480,
                "difficulty": "easy-medium",
                "source": "https://github.com/victorvikram/ConceptARC",
                "format": "json",
            },
            "re_arc": {
                "description": "Synthetic ARC tasks from DSL",
                "size": 10000,
                "difficulty": "varied",
                "source": "https://github.com/michaelhodel/re-arc",
                "format": "json",
            },
        },
        "phase2": {
            "arc_agi_1_full": {
                "description": "Full ARC-AGI-1 dataset",
                "size": 800,
                "difficulty": "full range",
                "source": "https://github.com/fchollet/ARC-AGI",
            },
            "barc": {
                "description": "Billion-scale ARC synthetic",
                "size": 100000,
                "difficulty": "varied",
                "source": "https://github.com/xu3kev/BARC",
            },
        },
        "phase3": {
            "arc_agi_2": {
                "description": "Harder ARC-AGI-2 tasks",
                "size": 400,
                "difficulty": "hard",
                "source": "https://arcprize.org/arc-agi-2",
            },
        },
    }
    
    # =========================================================================
    # SOFTWARE ENGINEERING BENCHMARKS
    # =========================================================================
    
    SWE_BENCHMARKS = {
        "phase1": {
            "humaneval": {
                "description": "Function synthesis from docstrings",
                "size": 164,
                "difficulty": "easy",
                "source": "https://github.com/openai/human-eval",
                "verification": "unit_tests",
            },
            "mbpp": {
                "description": "Mostly Basic Python Problems",
                "size": 974,
                "difficulty": "easy",
                "source": "https://github.com/google-research/mbpp",
                "verification": "unit_tests",
            },
            "codecontests_easy": {
                "description": "Easy competitive programming",
                "size": 500,
                "difficulty": "easy-medium",
                "source": "https://github.com/deepmind/code_contests",
                "verification": "test_cases",
            },
        },
        "phase2": {
            "swe_gym": {
                "description": "Real GitHub issues with executable environments",
                "size": 2438,
                "difficulty": "medium-hard",
                "source": "https://github.com/SWE-Gym/SWE-Gym",
                "verification": "docker_tests",
                "notes": "Most important training environment for SWE",
            },
            "swe_bench_lite": {
                "description": "Curated subset of SWE-bench",
                "size": 300,
                "difficulty": "medium",
                "source": "https://github.com/princeton-nlp/SWE-bench",
                "verification": "docker_tests",
            },
            "devbench": {
                "description": "End-to-end development tasks",
                "size": 200,
                "difficulty": "medium-hard",
                "source": "Various",
                "verification": "functional_tests",
            },
        },
        "phase3": {
            "swe_bench_verified": {
                "description": "Verified subset with quality checks",
                "size": 500,
                "difficulty": "hard",
                "source": "https://github.com/princeton-nlp/SWE-bench",
                "verification": "docker_tests",
                "notes": "Primary evaluation benchmark",
            },
            "swe_rebench": {
                "description": "Monthly fresh issues",
                "size": "varies",
                "difficulty": "hard",
                "source": "https://github.com/swe-rebench",
                "verification": "docker_tests",
                "notes": "Prevents overfitting to static benchmarks",
            },
        },
    }
    
    # =========================================================================
    # CURRICULUM SCHEDULING
    # =========================================================================
    
    @staticmethod
    def get_phase_config(phase: int) -> Dict:
        """Get training configuration for a phase"""
        configs = {
            1: {
                "duration_weeks": 2,
                "trajectory_target": 1000,
                "learning_rate": "high",
                "focus": "library_building",
                "finetune_frequency": "never",
                "memory_prune": False,
            },
            2: {
                "duration_weeks": 4,
                "trajectory_target": 10000,
                "learning_rate": "medium",
                "focus": "self_improvement",
                "finetune_frequency": "weekly",
                "memory_prune": True,
            },
            3: {
                "duration_weeks": 2,
                "trajectory_target": 2000,
                "learning_rate": "low",
                "focus": "generalization_test",
                "finetune_frequency": "none",
                "memory_prune": False,
            },
            4: {
                "duration_weeks": "ongoing",
                "trajectory_target": "adaptive",
                "learning_rate": "very_low",
                "focus": "specialization",
                "finetune_frequency": "on_demand",
                "memory_prune": True,
            },
        }
        return configs[phase]
```

### 5.3 Evaluation Protocol

```python
class EvaluationProtocol:
    """Standardized evaluation across domains"""
    
    # Primary metrics
    METRICS = {
        "arc_agi": {
            "primary": "accuracy",           # % tasks solved
            "secondary": [
                "accuracy_by_difficulty",    # Breakdown by task difficulty
                "llm_calls_per_task",        # Efficiency
                "cost_per_task",             # $ cost
                "solve_time",                # Wall clock time
            ],
        },
        "swe": {
            "primary": "resolve_rate",       # % issues resolved
            "secondary": [
                "pass_at_k",                 # With k attempts
                "best_at_k",                 # With verifier selection
                "partial_score",             # % tests passing
                "stuck_in_loop_rate",        # % trajectories that loop
                "empty_patch_rate",          # % no code changes
            ],
        },
    }
    
    # Evaluation checkpoints
    CHECKPOINTS = {
        "phase1_exit": {
            "arc": {"accuracy": 0.30, "on": "arc_agi_1_training"},
            "swe": {"resolve_rate": 0.40, "on": "humaneval"},
        },
        "phase2_exit": {
            "arc": {"accuracy": 0.50, "on": "arc_agi_1_full"},
            "swe": {"resolve_rate": 0.20, "on": "swe_bench_lite"},
        },
        "phase3_target": {
            "arc": {"accuracy": 0.40, "on": "arc_agi_2"},
            "swe": {"resolve_rate": 0.30, "on": "swe_bench_verified"},
        },
    }
    
    @staticmethod
    def evaluate(
        system: 'ATLASSystem',
        benchmark: str,
        domain: str,
        n_samples: int = None,
    ) -> Dict[str, float]:
        """Run evaluation on a benchmark"""
        tasks = load_benchmark(benchmark)
        if n_samples:
            tasks = random.sample(tasks, min(n_samples, len(tasks)))
        
        results = []
        for task in tqdm(tasks, desc=f"Evaluating {benchmark}"):
            trajectory = system.solve(task, record=True)
            results.append({
                "task_id": task.id,
                "success": trajectory.outcome.success,
                "partial_score": trajectory.outcome.partial_score,
                "steps": len(trajectory.steps),
                "time": trajectory.metadata.get("solve_time"),
            })
        
        metrics = EvaluationProtocol._compute_metrics(results, domain)
        return metrics
```

---

## 6. Implementation Roadmap

### 6.1 Phase 0: Infrastructure (Week 0)

```
□ Set up trajectory collection from Claude Code / Codex
□ Set up trajectory collection from OpenHands / SWE-agent
□ Implement unified trajectory format
□ Set up vector database for experience memory
□ Set up benchmark environments (Docker for SWE, Python for ARC)
```

### 6.2 Phase 1: Core Memory Systems (Weeks 1-2)

```
□ Implement ExperienceMemory with embedding-based retrieval
□ Implement basic ConceptLibrary with manual primitives
□ Implement StrategyBank with ArcMemo-style abstraction
□ Test memory systems independently on small benchmarks
```

### 6.3 Phase 2: Learning Pipeline (Weeks 3-4)

```
□ Implement TrajectoryAnalyzer for both domains
□ Implement Stitch-style compression for concept extraction
□ Implement SOAR-style hindsight learning
□ Set up curriculum Phase 1 benchmarks
□ Run initial training loop
```

### 6.4 Phase 3: Search Engine (Weeks 5-6)

```
□ Implement TaskRouter with memory integration
□ Implement Mind Evolution-style search
□ Implement verifier integration (ORM for SWE, grid-match for ARC)
□ Add MCTS hybrid option for exploration
```

### 6.5 Phase 4: Self-Improvement Loop (Weeks 7-8)

```
□ Implement periodic fine-tuning pipeline
□ Implement memory pruning and consolidation
□ Run full curriculum Phases 2-3
□ Evaluate on held-out benchmarks
```

### 6.6 Phase 5: Optimization (Weeks 9+)

```
□ Implement GEPA-style prompt optimization
□ Multi-agent routing experiments
□ Scaling experiments
□ Ablation studies
```

---

## 7. Key Design Decisions

### 7.1 Why Extract Learning from Existing Agents?

1. **Leverage existing tool integration** - Claude Code, Codex, OpenHands already handle complex tool orchestration
2. **Focus on meta-learning** - ATLAS adds the learning layer, not another agent implementation
3. **Trajectory diversity** - Different agents make different mistakes, providing richer learning signal
4. **Reduce development scope** - Build on proven agent infrastructure

### 7.2 Why Three Memory Types?

From the literature:

1. **Concept Library** (DreamCoder/Stitch/Pang)
   - Provides efficiency: 10x fewer LLM calls with good library
   - Enables composition: complex solutions from simple primitives

2. **Experience Memory** (Evo-Memory/ReMem)
   - Provides task-level retrieval: find similar past problems
   - Enables adaptation: transfer solutions with minor modifications

3. **Strategy Bank** (ArcMemo)
   - Provides abstraction: concept-level > instance-level at all scales
   - Enables reasoning: guide search with abstract principles

### 7.3 Why SOAR-Style Self-Improvement?

From SOAR paper findings:
- Fine-tuning on own traces overcomes performance plateaus
- Separate sampling and refinement capabilities improve differently
- Cross-model diversity helps (ensemble of sizes)
- 52% ARC-AGI with open-source models

### 7.4 Generalization vs. Specialization

The framework is designed to be:
- **General in architecture**: Same pipeline for both domains
- **Specific in adapters**: Domain-specific verification, context, primitives
- **Adaptive in learning**: Learns domain-specific patterns from trajectories

---

## 8. Expected Results

Based on literature baselines:

| Configuration | ARC-AGI-1 | ARC-AGI-2 | SWE-Bench Verified |
|--------------|-----------|-----------|-------------------|
| Baseline (no learning) | 30-40% | 10-15% | 15-20% |
| + Experience Memory | 40-50% | 15-20% | 20-25% |
| + Concept Library | 50-60% | 18-25% | 25-30% |
| + Strategy Bank | 55-65% | 22-30% | 28-32% |
| + Self-Improvement | 60-70% | 28-35% | 32-38% |
| + Full Optimization | 70-80% | 35-45% | 38-45% |

---

## 9. References

### Core Papers
1. Mind Evolution (arXiv:2501.09891)
2. SOAR (arXiv:2507.14172)
3. ArcMemo (arXiv:2509.04439)
4. Evo-Memory (arXiv:2511.20857)
5. SWE-Gym (arXiv:2412.21139)
6. SAGE (Salesforce, 2025)
7. SWE-Search (ICLR 2025)
8. Stitch (POPL 2023)
9. LILO (ICLR 2024)
10. Voyager (arXiv:2305.16291)
11. DreamCoder (PLDI 2021)
12. AgentTrek (ICLR 2025 Spotlight)

### Code Resources
1. `github.com/SWE-Gym/SWE-Gym` - Training environment
2. `github.com/OpenHands/OpenHands` - Agent scaffold
3. `github.com/epang080516/arc_agi` - Efficient ARC solver
4. `github.com/matt-seb-ho/arc_memo` - Concept memory
5. `github.com/mlb2251/stitch` - Fast library learning
6. `github.com/gabegrand/lilo` - Neurosymbolic library learning
7. `github.com/lucidrains/mind-evolution` - Evolutionary search
8. `github.com/julien31/Soar-qwen-7b` - Fine-tuned SOAR models

---

*Document Version: 1.0*
*Last Updated: December 2025*