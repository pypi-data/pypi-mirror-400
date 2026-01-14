---
id: s-w56w
title: Learning Engine (Pillar 3)
priority: 1
created_at: '2025-12-07 08:21:08'
parent_id: s-5o87
tags:
  - abstraction
  - fine-tuning
  - learning
  - pillar-3
  - trajectory-analysis
relationships:
  - from_id: s-w56w
    from_uuid: ce205fa1-4233-4fbc-b56f-d1455e27962c
    from_type: spec
    to_id: s-5o87
    to_uuid: 315749e5-c7a0-41c9-8fd2-8124b1d9c2f7
    to_type: spec
    relationship_type: implements
    created_at: '2025-12-07 08:22:01'
    metadata: null
---
# Learning Engine (Pillar 3)

Parent: [[s-5o87|ATLAS System Architecture]]

## Overview

Learning is **how to improve** - extracting knowledge from trajectories to update memory and optionally fine-tune models.

## Data Flow

```
Trajectories (success + failure)
        ↓
Trajectory Analyzer → AnalysisResult
        ↓
Abstraction Extractor → CodeConcepts, Strategies
        ↓
Memory Update
        ↓
Hindsight Learner → Training Data → (optional) Fine-tune
```

## Trajectory Analyzer

**Purpose**: Extract learning signals from trajectories

### Interface

```python
class TrajectoryAnalyzer(ABC):
    @abstractmethod
    def analyze(self, trajectory: Trajectory) -> AnalysisResult:
        """Full analysis of a trajectory"""
        pass
    
    @abstractmethod
    def attribute_outcome(
        self,
        trajectory: Trajectory,
    ) -> List[Tuple[int, float]]:
        """Credit assignment: (step_index, contribution_score)"""
        pass
```

### Analysis Result

```python
@dataclass
class AnalysisResult:
    success: bool
    key_steps: List[int]              # Indices of critical steps
    step_attribution: List[float]     # Credit per step
    error_patterns: List[Dict]        # Detected failure modes
    abstractable: bool                # Worth extracting patterns?
    training_examples: List[Dict]     # For hindsight learning
```

### Credit Assignment

Identify which steps contributed to outcome:
- Success: which steps led to solution?
- Failure: which step caused the error?

Methods:
1. **Simple**: Last successful action gets credit
2. **LLM-based**: Ask LLM to identify key steps
3. **Counterfactual**: Would removing this step change outcome?

## Abstraction Extractor

**Purpose**: Extract reusable patterns from trajectories

### Interface

```python
class AbstractionExtractor(ABC):
    @abstractmethod
    def extract_code_patterns(
        self,
        trajectories: List[Trajectory],
    ) -> List[CodeConcept]:
        """Stitch-style compression"""
        pass
    
    @abstractmethod
    def extract_strategies(
        self,
        trajectories: List[Trajectory],
    ) -> List[Strategy]:
        """ArcMemo-style abstraction"""
        pass
    
    @abstractmethod
    def auto_document(self, concept: CodeConcept) -> CodeConcept:
        """LILO-style documentation generation"""
        pass
```

### Code Pattern Extraction (Stitch)

1. Parse successful code to AST
2. Find common subtrees via anti-unification
3. Score by MDL (compression benefit)
4. Extract top-k as CodeConcepts

```python
def extract_code_patterns(self, trajectories):
    # Extract code from successful trajectories
    code_corpus = [extract_code(t) for t in trajectories if t.outcome.success]
    
    # Run Stitch compression
    abstractions = self.stitch.compress(code_corpus)
    
    # Convert to CodeConcepts
    return [self._to_concept(a) for a in abstractions]
```

### Strategy Extraction (ArcMemo)

1. Identify successful trajectory
2. Abstract task description → situation
3. Abstract solution approach → suggestion
4. Extract typed parameters

```python
def extract_strategies(self, trajectories):
    strategies = []
    for traj in trajectories:
        if traj.outcome.success and self._is_abstractable(traj):
            strategy = Strategy(
                situation=self._abstract_situation(traj.task),
                suggestion=self._abstract_approach(traj),
                parameters=self._extract_params(traj),
            )
            strategies.append(strategy)
    return strategies
```

### AutoDoc (LILO)

Generate human-readable documentation for concepts:

```python
def auto_document(self, concept: CodeConcept) -> CodeConcept:
    prompt = f"""
    Given this code pattern:
    {concept.code}
    
    And these examples:
    {concept.examples}
    
    Generate:
    1. Concise name (snake_case)
    2. One-sentence description
    3. Type signature
    """
    response = self.llm.generate(prompt)
    concept.name, concept.description, concept.signature = parse(response)
    return concept
```

## Hindsight Learner

**Purpose**: Learn from trajectories to improve model

### Interface

```python
class HindsightLearner(ABC):
    @abstractmethod
    def prepare_training_data(
        self,
        trajectories: List[Trajectory],
    ) -> Dict[str, Any]:
        """Convert trajectories to training format"""
        pass
    
    @abstractmethod
    def should_finetune(self) -> bool:
        """Check if enough data for fine-tuning"""
        pass
    
    @abstractmethod
    def finetune(self, training_data: Dict) -> FinetuneResult:
        """Execute fine-tuning"""
        pass
```

### SOAR-Style Training Data

Separate sampling and refinement capabilities:

```python
def prepare_training_data(self, trajectories):
    sampling_data = []      # Learn to generate good initial solutions
    refinement_data = []    # Learn to refine based on feedback
    
    for traj in trajectories:
        if traj.outcome.success:
            # Learn successful solutions (2x weight)
            sampling_data.append({
                "input": format_task(traj.task),
                "output": extract_solution(traj),
                "weight": 2.0,
            })
            
            # Learn key intermediate steps (1.5x weight)
            for i, step in enumerate(traj.steps):
                if is_key_step(traj, i):
                    refinement_data.append({
                        "input": format_with_history(traj, i),
                        "output": step.action,
                        "weight": 1.5,
                    })
        else:
            # Learn from failures (1x weight)
            if traj.outcome.error_info:
                refinement_data.append({
                    "input": format_with_history(traj, len(traj.steps)),
                    "output": f"[ERROR] {traj.outcome.error_info}",
                    "weight": 1.0,
                })
    
    return {"sampling": sampling_data, "refinement": refinement_data}
```

### Fine-tuning Triggers

```python
def should_finetune(self) -> bool:
    return (
        len(self.accumulated_trajectories) >= 100 and
        time_since_last_finetune() >= timedelta(hours=24) and
        quality_threshold_met()
    )
```

### SAGE Alternative (Training-Free)

If fine-tuning not desired, use memory-only improvement:
- Store plans as retrievable documents
- In-context learning with retrieved plans
- No weight updates, only memory growth

## Learning Pipeline

Orchestrates the full learning process:

```python
class LearningPipeline:
    def __init__(
        self,
        memory: MemorySystem,
        analyzer: TrajectoryAnalyzer,
        extractor: AbstractionExtractor,
        hindsight: Optional[HindsightLearner] = None,
    ):
        pass
    
    def process_trajectory(self, trajectory: Trajectory):
        """Process single trajectory"""
        # 1. Store in experience memory
        self.memory.experience_memory.store(trajectory)
        
        # 2. Analyze
        analysis = self.analyzer.analyze(trajectory)
        
        # 3. Extract strategy if abstractable
        if analysis.abstractable:
            strategy = self.extractor.extract_strategy(trajectory)
            if strategy:
                self.memory.strategy_bank.write(strategy)
        
        # 4. Accumulate for batch processing
        self.trajectory_buffer.append(trajectory)
    
    def run_batch_learning(self, min_trajectories: int = 50):
        """Periodic batch learning"""
        if len(self.trajectory_buffer) < min_trajectories:
            return
        
        # Extract code patterns
        concepts = self.extractor.extract_code_patterns(self.trajectory_buffer)
        for c in concepts:
            self.memory.concept_library.add(c)
        
        # Maybe fine-tune
        if self.hindsight and self.hindsight.should_finetune():
            data = self.hindsight.prepare_training_data(self.trajectory_buffer)
            self.hindsight.finetune(data)
        
        self.trajectory_buffer = []
```

## File Location

```
atlas/learning/
├── __init__.py
├── analyzer.py      # TrajectoryAnalyzer, AnalysisResult
├── extractor.py     # AbstractionExtractor
├── hindsight.py     # HindsightLearner, SOAR/SAGE implementations
└── pipeline.py      # LearningPipeline
```
