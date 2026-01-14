# Cognitive Core Architecture: High-Level Design

## Overview

This document defines the high-level architecture for Cognitive Core (Adaptive Trajectory Learning and Abstraction System). It organizes the system around **three pillars** (Memory, Search, Learning) and **three primitives** (Trajectories, Environments, Agents).

---

## 1. Core Primitives

These are the fundamental building blocks that all other components operate on.

### 1.1 Trajectory

The **atomic unit of learning**. Everything in Cognitive Core flows through trajectories.

```
┌─────────────────────────────────────────────────────────────────┐
│                         TRAJECTORY                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Task                                                     │    │
│  │ ├── id: str                                             │    │
│  │ ├── domain: TaskDomain (arc_agi | swe | ...)           │    │
│  │ ├── description: str                                    │    │
│  │ ├── context: Dict[str, Any]  # domain-specific          │    │
│  │ └── verification: VerificationSpec                      │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Steps: List[Step]                                        │    │
│  │                                                          │    │
│  │   Step 0: thought → action → observation → metadata     │    │
│  │   Step 1: thought → action → observation → metadata     │    │
│  │   ...                                                    │    │
│  │   Step N: thought → action → observation → metadata     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Outcome                                                  │    │
│  │ ├── success: bool                                       │    │
│  │ ├── partial_score: Optional[float]  # 0.0 - 1.0        │    │
│  │ ├── error_info: Optional[str]                          │    │
│  │ └── verification_details: Dict[str, Any]               │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Metadata:                                                       │
│  ├── agent_id: str        # which agent produced this           │
│  ├── timestamp: datetime                                         │
│  └── embeddings: Dict[str, Vector]  # precomputed embeddings    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Key Design Decisions**:
- Trajectories are **immutable** after creation
- Every trajectory has an **outcome** (even partial/failed ones)
- Steps capture **thought-action-observation** triples (like ReAct)
- Metadata enables **attribution** back to producing agent

### 1.2 Environment

The **execution context** where tasks are solved and trajectories are generated.

```
┌─────────────────────────────────────────────────────────────────┐
│                        ENVIRONMENT                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Interface:                                                      │
│  ├── reset(task: Task) → Observation                            │
│  ├── step(action: Action) → (Observation, Reward, Done, Info)   │
│  ├── verify(solution: Any) → Outcome                            │
│  └── render() → str | Image                                     │
│                                                                  │
│  Properties:                                                     │
│  ├── deterministic: bool       # same action → same result      │
│  ├── has_intermediate_reward: bool                              │
│  ├── max_steps: int                                             │
│  └── action_space: ActionSpace                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Domain Implementations:

┌─────────────────────────┐  ┌─────────────────────────┐
│    ARC Environment      │  │    SWE Environment      │
├─────────────────────────┤  ├─────────────────────────┤
│ • Grid manipulation     │  │ • Docker sandbox        │
│ • Training examples     │  │ • File system access    │
│ • Exact match verify    │  │ • Test execution        │
│ • Deterministic         │  │ • Patch application     │
└─────────────────────────┘  └─────────────────────────┘
```

**Key Design Decisions**:
- Follows **Gymnasium-like** interface for familiarity
- **Verification is built-in** (not external)
- Environments are **sandboxed** and **reproducible**
- Support for **partial scoring** in verification

### 1.3 Agent

The **actor** that produces trajectories by interacting with environments.

```
┌─────────────────────────────────────────────────────────────────┐
│                           AGENT                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Interface:                                                      │
│  ├── solve(task: Task, env: Environment) → Trajectory           │
│  ├── step(observation: Observation) → Action                    │
│  └── reset()                                                    │
│                                                                  │
│  Components:                                                     │
│  ├── llm: LLM                  # base language model             │
│  ├── memory: MemorySystem      # access to Cognitive Core memory          │
│  ├── tools: List[Tool]         # available actions               │
│  └── prompt_template: Template                                   │
│                                                                  │
│  Configuration:                                                  │
│  ├── max_steps: int                                              │
│  ├── temperature: float                                          │
│  └── use_memory: bool                                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Agent Types:

┌─────────────────────────┐  ┌─────────────────────────┐
│    External Agents      │  │    Cognitive Core Agent          │
├─────────────────────────┤  ├─────────────────────────┤
│ • Claude Code           │  │ • Memory-augmented      │
│ • OpenHands             │  │ • Library-aware         │
│ • SWE-agent             │  │ • Strategy-guided       │
│ • Codex                 │  │ • Searchable            │
│                         │  │                         │
│ Output: Raw Trajectories│  │ Output: Rich Trajector. │
└─────────────────────────┘  └─────────────────────────┘
```

**Key Design Decisions**:
- Agents are **pluggable** (external agents wrapped to unified interface)
- Cognitive Core agents are **memory-augmented** versions of base agents
- All agents **produce trajectories** as output
- Agent **attribution** is preserved for analysis

---

## 2. The Three Pillars

### 2.1 Pillar 1: Memory Systems

Memory is **what to remember** - the accumulated knowledge from past trajectories.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           MEMORY SYSTEMS                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                     CONCEPT LIBRARY                              │    │
│  │                     (What can I reuse?)                          │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │                                                                   │    │
│  │  Purpose: Reusable code patterns and compositions                │    │
│  │                                                                   │    │
│  │  Storage:                                                         │    │
│  │  ├── primitives: Dict[str, CodeConcept]  # base operations       │    │
│  │  ├── learned: Dict[str, CodeConcept]     # extracted patterns    │    │
│  │  └── compositions: Dict[str, CodeConcept] # combined patterns    │    │
│  │                                                                   │    │
│  │  Interface:                                                       │    │
│  │  ├── add(concept: CodeConcept) → str                             │    │
│  │  ├── search(query: str, k: int) → List[CodeConcept]             │    │
│  │  ├── compose(ids: List[str]) → Optional[CodeConcept]            │    │
│  │  └── compress(trajectories: List[Trajectory]) → List[CodeConcept]│   │
│  │                                                                   │    │
│  │  Key Insight: Stitch + LILO for fast, interpretable extraction   │    │
│  │                                                                   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    EXPERIENCE MEMORY                             │    │
│  │                    (What have I seen before?)                    │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │                                                                   │    │
│  │  Purpose: Task-level retrieval of similar past experiences       │    │
│  │                                                                   │    │
│  │  Storage:                                                         │    │
│  │  ├── experiences: VectorIndex[Experience]                        │    │
│  │  └── embeddings: Model  # BAAI/bge-base-en-v1.5                  │    │
│  │                                                                   │    │
│  │  Experience:                                                      │    │
│  │  ├── input: str             # task description                   │    │
│  │  ├── output: str            # solution attempt                   │    │
│  │  ├── feedback: str          # outcome/error                      │    │
│  │  └── embedding: Vector                                           │    │
│  │                                                                   │    │
│  │  Interface:                                                       │    │
│  │  ├── store(trajectory: Trajectory) → str                        │    │
│  │  ├── search(task: Task, k: int) → List[Experience]              │    │
│  │  ├── refine(experiences: List[Experience]) → List[Experience]   │    │
│  │  └── prune(criteria: Dict) → int                                │    │
│  │                                                                   │    │
│  │  Key Insight: ReMem's search-synthesize-evolve loop              │    │
│  │                                                                   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                     STRATEGY BANK                                │    │
│  │                     (How should I approach this?)                │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │                                                                   │    │
│  │  Purpose: Abstract reasoning patterns (concept-level > instance) │    │
│  │                                                                   │    │
│  │  Storage:                                                         │    │
│  │  ├── strategies: VectorIndex[Strategy]                           │    │
│  │  └── situation_embeddings: Model                                 │    │
│  │                                                                   │    │
│  │  Strategy:                                                        │    │
│  │  ├── situation: str         # when to apply                      │    │
│  │  ├── suggestion: str        # what to do                         │    │
│  │  ├── parameters: List[TypedParam]                                │    │
│  │  └── success_rate: float                                         │    │
│  │                                                                   │    │
│  │  Interface:                                                       │    │
│  │  ├── write(trajectory: Trajectory) → Optional[Strategy]         │    │
│  │  ├── read(task: Task, k: int) → List[Strategy]                  │    │
│  │  └── update_stats(strategy_id: str, success: bool)              │    │
│  │                                                                   │    │
│  │  Key Insight: ArcMemo - concept-level beats instance-level       │    │
│  │               at ALL compute scales                               │    │
│  │                                                                   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Memory Hierarchy**:
```
Strategy Bank    →  "For symmetry tasks, reflect then duplicate"  (most abstract)
        ↓
Experience Memory →  "Task #123 was similar, here's what worked"   (task-level)
        ↓
Concept Library  →  "Use rotate_90() followed by flood_fill()"    (most concrete)
```

### 2.2 Pillar 2: Search Methods

Search is **how to solve** - the algorithms for finding solutions.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           SEARCH METHODS                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                        TASK ROUTER                               │    │
│  │                        (Which search to use?)                    │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │                                                                   │    │
│  │  Input: Task + Memory query results                              │    │
│  │                                                                   │    │
│  │  Output: RoutingDecision                                         │    │
│  │  ├── strategy: "direct" | "evolutionary" | "mcts" | "adapt"     │    │
│  │  ├── relevant_concepts: List[Concept]                            │    │
│  │  ├── similar_experiences: List[Experience]                       │    │
│  │  ├── suggested_strategies: List[Strategy]                        │    │
│  │  ├── estimated_difficulty: float                                 │    │
│  │  └── search_budget: int                                          │    │
│  │                                                                   │    │
│  │  Logic:                                                           │    │
│  │  ├── High similarity + success → "adapt" (modify existing)      │    │
│  │  ├── Clear strategy available → "direct" (apply strategy)       │    │
│  │  ├── ARC domain → "evolutionary" (Mind Evolution)               │    │
│  │  └── SWE domain → "mcts" (SWE-Search)                           │    │
│  │                                                                   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              │                                           │
│                              ▼                                           │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌───────────────┐  │
│  │   MIND EVOLUTION     │  │     SWE-SEARCH       │  │    DIRECT     │  │
│  │   (Population-based) │  │   (Tree-based MCTS)  │  │   (Single)    │  │
│  ├──────────────────────┤  ├──────────────────────┤  ├───────────────┤  │
│  │                      │  │                      │  │               │  │
│  │ Best for: ARC-AGI    │  │ Best for: SWE        │  │ Best for:     │  │
│  │ Clear fitness fn     │  │ Sequential edits     │  │ High conf.    │  │
│  │                      │  │                      │  │ memory match  │  │
│  │ Algorithm:           │  │ Algorithm:           │  │               │  │
│  │ 1. Init population   │  │ 1. Root = task       │  │ Algorithm:    │  │
│  │    (50% memory)      │  │ 2. Select (UCB)      │  │ 1. Retrieve   │  │
│  │ 2. Evaluate fitness  │  │ 3. Expand (LLM)      │  │ 2. Adapt      │  │
│  │ 3. Select elites     │  │ 4. Simulate          │  │ 3. Verify     │  │
│  │ 4. Mutate/crossover  │  │ 5. Backpropagate     │  │               │  │
│  │ 5. Repeat 5-10 gen   │  │ 6. Repeat 50-200x    │  │ Cost: ~1 call │  │
│  │                      │  │                      │  │               │  │
│  │ Cost: ~100 LLM calls │  │ Cost: ~200 LLM calls │  │               │  │
│  │                      │  │                      │  │               │  │
│  └──────────────────────┘  └──────────────────────┘  └───────────────┘  │
│                              │                                           │
│                              ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                        VERIFIER                                  │    │
│  │                        (Is this solution correct?)               │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │                                                                   │    │
│  │  Interface:                                                       │    │
│  │  ├── verify(task, candidate) → Outcome                           │    │
│  │  └── rank(task, candidates) → List[(Candidate, score)]          │    │
│  │                                                                   │    │
│  │  ARC: Exact grid match + training example consistency            │    │
│  │  SWE: Test execution + discriminator model                       │    │
│  │                                                                   │    │
│  │  Key: Verification enables inference-time scaling (best-of-k)    │    │
│  │                                                                   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Pillar 3: Learning Engine

Learning is **how to improve** - extracting knowledge from trajectories.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          LEARNING ENGINE                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Input: Trajectories (both successful and failed)                        │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    TRAJECTORY ANALYZER                           │    │
│  │                    (What happened? Why?)                         │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │                                                                   │    │
│  │  analyze(trajectory) → AnalysisResult:                           │    │
│  │  ├── success_classification: bool                                │    │
│  │  ├── key_steps: List[int]           # indices of critical steps │    │
│  │  ├── error_patterns: List[Pattern]  # if failed                 │    │
│  │  ├── step_attribution: List[float]  # credit per step           │    │
│  │  └── abstractable: bool             # worth extracting?         │    │
│  │                                                                   │    │
│  │  Methods:                                                         │    │
│  │  ├── attribute_outcome() → credit assignment                     │    │
│  │  ├── extract_error_patterns() → common failure modes            │    │
│  │  └── should_abstract() → is this trajectory valuable?           │    │
│  │                                                                   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              │                                           │
│                              ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                  ABSTRACTION EXTRACTOR                           │    │
│  │                  (What patterns emerge?)                         │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │                                                                   │    │
│  │  Code Patterns (Stitch-style):                                    │    │
│  │  ├── Parse successful code to AST                                │    │
│  │  ├── Find common subtrees via anti-unification                  │    │
│  │  ├── Score by MDL (compression benefit)                          │    │
│  │  └── Extract top-k as CodeConcepts                               │    │
│  │                                                                   │    │
│  │  Strategies (ArcMemo-style):                                      │    │
│  │  ├── Abstract from task → solution patterns                      │    │
│  │  ├── Generalize situation descriptions                           │    │
│  │  ├── Extract typed parameters                                    │    │
│  │  └── Store as Strategy with success stats                        │    │
│  │                                                                   │    │
│  │  AutoDoc (LILO-style):                                            │    │
│  │  ├── LLM generates names for abstractions                        │    │
│  │  ├── Creates docstrings explaining purpose                       │    │
│  │  └── Adds usage examples                                         │    │
│  │                                                                   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              │                                           │
│                              ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                   HINDSIGHT LEARNER                              │    │
│  │                   (How to improve the model?)                    │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │                                                                   │    │
│  │  SOAR-style self-improvement:                                     │    │
│  │                                                                   │    │
│  │  prepare_training_data(trajectories) →                           │    │
│  │  ├── sampling_data: List[Example]      # initial solution gen    │    │
│  │  └── refinement_data: List[Example]    # error recovery          │    │
│  │                                                                   │    │
│  │  Weighting:                                                       │    │
│  │  ├── Successful trajectories: 2.0x weight                        │    │
│  │  ├── Key intermediate steps: 1.5x weight                         │    │
│  │  └── Error recovery: 1.0x weight                                 │    │
│  │                                                                   │    │
│  │  should_finetune() → bool                                         │    │
│  │  ├── Enough trajectories accumulated? (min 100)                  │    │
│  │  ├── Time since last finetune? (min 24h)                         │    │
│  │  └── Quality threshold met?                                      │    │
│  │                                                                   │    │
│  │  finetune(data) → FinetuneResult                                  │    │
│  │  ├── Execute fine-tuning (API or local)                          │    │
│  │  └── Track metrics and version                                   │    │
│  │                                                                   │    │
│  │  SAGE-style alternative (training-free):                          │    │
│  │  ├── Store plans as retrievable documents                        │    │
│  │  ├── In-context learning with retrieved plans                    │    │
│  │  └── No weight updates, only memory growth                       │    │
│  │                                                                   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  Output: Updated Memory Systems + Optional Fine-tuned Model             │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. System Integration

### 3.1 Full Data Flow

```
                              ┌─────────────────────────────────────┐
                              │             TASK INPUT               │
                              │                                      │
                              │   • ARC-AGI puzzle                  │
                              │   • GitHub issue                    │
                              │   • General coding task             │
                              └──────────────┬──────────────────────┘
                                             │
                                             ▼
                    ┌────────────────────────────────────────────────────┐
                    │                    MEMORY QUERY                     │
                    │                                                     │
                    │   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐  │
                    │   │  Concept    │ │ Experience  │ │  Strategy   │  │
                    │   │  Library    │ │   Memory    │ │    Bank     │  │
                    │   └──────┬──────┘ └──────┬──────┘ └──────┬──────┘  │
                    │          │               │               │         │
                    │          └───────────────┼───────────────┘         │
                    │                          │                          │
                    └──────────────────────────┼──────────────────────────┘
                                               │
                                               ▼
                              ┌─────────────────────────────────────┐
                              │            TASK ROUTER               │
                              │                                      │
                              │   Decide: direct | evolutionary |   │
                              │           mcts | adapt              │
                              └──────────────┬──────────────────────┘
                                             │
                        ┌────────────────────┼────────────────────┐
                        │                    │                    │
                        ▼                    ▼                    ▼
               ┌────────────────┐   ┌────────────────┐   ┌────────────────┐
               │ MIND EVOLUTION │   │  SWE-SEARCH    │   │    DIRECT      │
               │                │   │                │   │                │
               │  Population    │   │   MCTS Tree    │   │   Retrieval    │
               │  Generations   │   │   Expansions   │   │   Adaptation   │
               └───────┬────────┘   └───────┬────────┘   └───────┬────────┘
                       │                    │                    │
                       └────────────────────┼────────────────────┘
                                            │
                                            ▼
                              ┌─────────────────────────────────────┐
                              │            VERIFIER                  │
                              │                                      │
                              │   Rank candidates, select best      │
                              └──────────────┬──────────────────────┘
                                             │
                        ┌────────────────────┴────────────────────┐
                        │                                         │
                        ▼                                         ▼
               ┌────────────────┐                       ┌────────────────┐
               │    SUCCESS     │                       │    FAILURE     │
               │                │                       │                │
               │  • Solution    │                       │  • Error info  │
               │  • Trajectory  │                       │  • Trajectory  │
               └───────┬────────┘                       └───────┬────────┘
                       │                                        │
                       └────────────────┬───────────────────────┘
                                        │
                                        ▼
                              ┌─────────────────────────────────────┐
                              │          LEARNING ENGINE            │
                              │                                     │
                              │   • Analyze trajectory              │
                              │   • Extract patterns (Stitch)       │
                              │   • Abstract strategies (ArcMemo)   │
                              │   • Prepare training data (SOAR)    │
                              └──────────────┬──────────────────────┘
                                             │
                                             ▼
                              ┌─────────────────────────────────────┐
                              │          MEMORY UPDATE              │
                              │                                     │
                              │   • Add to Experience Memory        │
                              │   • Update Concept Library          │
                              │   • Enrich Strategy Bank            │
                              │   • Accumulate training data        │
                              └─────────────────────────────────────┘
                                             │
                                             │ (periodic)
                                             ▼
                              ┌─────────────────────────────────────┐
                              │          FINE-TUNING                │
                              │          (Optional, SOAR-style)     │
                              │                                     │
                              │   When: 100+ trajectories, 24h+     │
                              └─────────────────────────────────────┘
```

### 3.2 Module Dependencies

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          MODULE STRUCTURE                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  cognitive_core/                                                                  │
│  ├── core/                      # Primitives                            │
│  │   ├── trajectory.py          # Trajectory, Step, Outcome             │
│  │   ├── task.py                # Task, TaskDomain                      │
│  │   └── interfaces.py          # ABC definitions                       │
│  │                                                                       │
│  ├── memory/                    # Pillar 1: Memory Systems              │
│  │   ├── concept_library.py     # CodeConcept, ConceptLibrary           │
│  │   ├── experience_memory.py   # Experience, ExperienceMemory          │
│  │   ├── strategy_bank.py       # Strategy, StrategyBank                │
│  │   └── embeddings.py          # Embedding model wrapper               │
│  │                                                                       │
│  ├── search/                    # Pillar 2: Search Methods              │
│  │   ├── router.py              # TaskRouter, RoutingDecision           │
│  │   ├── mind_evolution.py      # MindEvolutionSearch                   │
│  │   ├── swe_search.py          # SWESearch (MCTS)                      │
│  │   ├── direct.py              # DirectSolver                          │
│  │   └── verifier.py            # Verifier interface + impls            │
│  │                                                                       │
│  ├── learning/                  # Pillar 3: Learning Engine             │
│  │   ├── analyzer.py            # TrajectoryAnalyzer                    │
│  │   ├── abstractor.py          # AbstractionExtractor (Stitch+LILO)    │
│  │   ├── hindsight.py           # HindsightLearner (SOAR/SAGE)          │
│  │   └── pipeline.py            # Cognitive CoreLearningPipeline                 │
│  │                                                                       │
│  ├── environments/              # Task Environments                      │
│  │   ├── __init__.py            # Factory and re-exports                │
│  │   ├── base.py                # PassthroughEnvironment                │
│  │   ├── arc/                   # ARC-AGI environment package           │
│  │   │   ├── __init__.py        # Re-exports all ARC components         │
│  │   │   ├── environment.py     # ARCEnvironment class                  │
│  │   │   ├── types.py           # Grid type alias, ARCTask dataclass    │
│  │   │   ├── loader.py          # Dataset loading utilities             │
│  │   │   └── utils.py           # Format/parse/verify utilities         │
│  │   └── swe.py                 # SWE environment (Docker)              │
│  │                                                                       │
│  ├── agents/                    # Agent Wrappers                         │
│  │   ├── base.py                # Agent ABC                             │
│  │   ├── cognitive_core_agent.py         # Memory-augmented agent                │
│  │   └── external/              # Wrappers for external agents          │
│  │       ├── claude_code.py                                             │
│  │       ├── openhands.py                                               │
│  │       └── swe_agent.py                                               │
│  │                                                                       │
│  ├── domains/                   # Domain-Specific Adapters              │
│  │   ├── arc/                                                           │
│  │   │   ├── primitives.py      # ARC grid operations                   │
│  │   │   ├── verifier.py        # Grid matching                         │
│  │   │   └── concept_library.py # ARC-specific library                  │
│  │   └── swe/                                                           │
│  │       ├── primitives.py      # Code editing operations               │
│  │       ├── verifier.py        # Test execution                        │
│  │       └── concept_library.py # SWE-specific library                  │
│  │                                                                       │
│  └── integration/               # External Integrations                  │
│      ├── stitch.py              # Stitch compression                    │
│      ├── lilo.py                # LILO AutoDoc                          │
│      └── llm.py                 # LLM API wrappers                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Key Interfaces (Type Definitions)

### 4.1 Core Types

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple, TypeVar, Generic
from enum import Enum
from datetime import datetime
import numpy as np


# =============================================================================
# ENUMS
# =============================================================================

class TaskDomain(Enum):
    ARC_AGI = "arc_agi"
    SOFTWARE_ENGINEERING = "swe"
    # Extensible


class SearchStrategy(Enum):
    DIRECT = "direct"
    EVOLUTIONARY = "evolutionary"
    MCTS = "mcts"
    ADAPT = "adapt"


# =============================================================================
# CORE DATA STRUCTURES
# =============================================================================

@dataclass
class Task:
    """Domain-agnostic task representation"""
    id: str
    domain: TaskDomain
    description: str
    context: Dict[str, Any]
    verification: 'VerificationSpec'

    # Optional: precomputed embeddings for efficiency
    embedding: Optional[np.ndarray] = None


@dataclass
class Step:
    """Single step in a trajectory"""
    thought: Optional[str]
    action: str
    observation: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Computed during analysis
    attribution_score: Optional[float] = None


@dataclass
class Outcome:
    """Result of a trajectory"""
    success: bool
    partial_score: Optional[float] = None  # 0.0 - 1.0
    error_info: Optional[str] = None
    verification_details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Trajectory:
    """Complete trajectory for a task attempt"""
    task: Task
    steps: List[Step]
    outcome: Outcome
    agent_id: str
    timestamp: datetime

    # Metadata
    llm_calls: int = 0
    total_tokens: int = 0
    wall_time_seconds: float = 0.0


# =============================================================================
# MEMORY TYPES
# =============================================================================

@dataclass
class CodeConcept:
    """Reusable code pattern"""
    id: str
    name: str
    description: str
    code: str
    signature: str
    examples: List[Tuple[str, str]]  # (input, output)

    # Stats
    usage_count: int = 0
    success_rate: float = 0.0

    # Embeddings
    embedding: Optional[np.ndarray] = None


@dataclass
class Experience:
    """Stored experience for retrieval"""
    id: str
    task_input: str
    solution_output: str
    feedback: str
    success: bool

    # Embedding for retrieval
    embedding: np.ndarray

    # Source tracking
    trajectory_id: str
    timestamp: datetime


@dataclass
class Strategy:
    """Abstract reasoning pattern"""
    id: str
    situation: str      # When to apply
    suggestion: str     # What to do
    parameters: List[Dict[str, str]]  # Typed parameters

    # Stats
    usage_count: int = 0
    success_rate: float = 0.0

    # Embedding
    embedding: Optional[np.ndarray] = None


# =============================================================================
# SEARCH TYPES
# =============================================================================

@dataclass
class RoutingDecision:
    """Output of task router"""
    strategy: SearchStrategy
    relevant_concepts: List[CodeConcept]
    similar_experiences: List[Experience]
    suggested_strategies: List[Strategy]
    estimated_difficulty: float
    search_budget: int


@dataclass
class Candidate:
    """A candidate solution"""
    solution: Any
    confidence: float
    reasoning: str
    source: str  # "generated", "adapted", "retrieved"

    # For evolutionary search
    fitness: Optional[float] = None
    parent_ids: List[str] = field(default_factory=list)


# =============================================================================
# ANALYSIS TYPES
# =============================================================================

@dataclass
class AnalysisResult:
    """Result of trajectory analysis"""
    success: bool
    key_steps: List[int]
    step_attribution: List[float]
    learned_patterns: List[CodeConcept]
    error_patterns: List[Dict[str, Any]]
    abstracted_strategy: Optional[Strategy]
    training_examples: List[Dict[str, Any]]
```

### 4.2 Abstract Base Classes

```python
# =============================================================================
# MEMORY INTERFACES
# =============================================================================

class ConceptLibrary(ABC):
    """Interface for concept storage and retrieval"""

    @abstractmethod
    def add(self, concept: CodeConcept) -> str:
        """Add a new concept, returns ID"""
        pass

    @abstractmethod
    def search(self, query: str, k: int = 5) -> List[CodeConcept]:
        """Find relevant concepts by semantic similarity"""
        pass

    @abstractmethod
    def get(self, concept_id: str) -> Optional[CodeConcept]:
        """Get concept by ID"""
        pass

    @abstractmethod
    def compose(self, concept_ids: List[str]) -> Optional[CodeConcept]:
        """Attempt to compose multiple concepts into one"""
        pass

    @abstractmethod
    def compress(self, trajectories: List[Trajectory]) -> List[CodeConcept]:
        """Extract new concepts from trajectories (Stitch-style)"""
        pass


class ExperienceMemory(ABC):
    """Interface for trajectory-level memory"""

    @abstractmethod
    def store(self, trajectory: Trajectory) -> str:
        """Store a trajectory as experience, returns ID"""
        pass

    @abstractmethod
    def search(self, task: Task, k: int = 5) -> List[Experience]:
        """Find similar past experiences"""
        pass

    @abstractmethod
    def refine(self, experiences: List[Experience]) -> List[Experience]:
        """ReMem-style refinement: exploit useful, prune noise"""
        pass

    @abstractmethod
    def prune(self, criteria: Dict[str, Any]) -> int:
        """Remove low-value experiences, returns count removed"""
        pass


class StrategyBank(ABC):
    """Interface for abstract strategy storage"""

    @abstractmethod
    def write(self, trajectory: Trajectory) -> Optional[Strategy]:
        """Abstract a trajectory into a strategy"""
        pass

    @abstractmethod
    def read(self, task: Task, k: int = 5) -> List[Strategy]:
        """Find applicable strategies"""
        pass

    @abstractmethod
    def update_stats(self, strategy_id: str, success: bool) -> None:
        """Update success statistics for a strategy"""
        pass


# =============================================================================
# SEARCH INTERFACES
# =============================================================================

class TaskRouter(ABC):
    """Route tasks to appropriate search strategy"""

    @abstractmethod
    def route(
        self,
        task: Task,
        concept_library: ConceptLibrary,
        experience_memory: ExperienceMemory,
        strategy_bank: StrategyBank
    ) -> RoutingDecision:
        """Decide how to approach a task"""
        pass


class SearchEngine(ABC):
    """Search for solutions"""

    @abstractmethod
    def search(
        self,
        task: Task,
        routing: RoutingDecision,
        env: 'Environment'
    ) -> List[Candidate]:
        """Search for candidate solutions"""
        pass

    @abstractmethod
    def refine(
        self,
        candidate: Candidate,
        feedback: str,
        task: Task
    ) -> Candidate:
        """Refine a candidate based on feedback"""
        pass


class Verifier(ABC):
    """Verify candidate solutions"""

    @abstractmethod
    def verify(self, task: Task, candidate: Candidate) -> Outcome:
        """Verify a candidate solution"""
        pass

    @abstractmethod
    def rank(
        self,
        task: Task,
        candidates: List[Candidate]
    ) -> List[Tuple[Candidate, float]]:
        """Rank candidates by estimated quality"""
        pass


# =============================================================================
# LEARNING INTERFACES
# =============================================================================

class TrajectoryAnalyzer(ABC):
    """Analyze trajectories to extract learning signals"""

    @abstractmethod
    def analyze(self, trajectory: Trajectory) -> AnalysisResult:
        """Full analysis of a trajectory"""
        pass

    @abstractmethod
    def attribute_outcome(
        self,
        trajectory: Trajectory
    ) -> List[Tuple[int, float]]:
        """Credit assignment: which steps contributed to outcome"""
        pass


class AbstractionExtractor(ABC):
    """Extract reusable abstractions from trajectories"""

    @abstractmethod
    def extract_code_patterns(
        self,
        trajectories: List[Trajectory]
    ) -> List[CodeConcept]:
        """Find reusable code patterns (Stitch-style)"""
        pass

    @abstractmethod
    def extract_strategies(
        self,
        trajectories: List[Trajectory]
    ) -> List[Strategy]:
        """Find reusable reasoning patterns (ArcMemo-style)"""
        pass

    @abstractmethod
    def auto_document(self, concept: CodeConcept) -> CodeConcept:
        """Generate human-readable documentation (LILO AutoDoc)"""
        pass


class HindsightLearner(ABC):
    """Learn from trajectories to improve future performance"""

    @abstractmethod
    def prepare_training_data(
        self,
        trajectories: List[Trajectory]
    ) -> Dict[str, Any]:
        """Convert trajectories to training format"""
        pass

    @abstractmethod
    def should_finetune(self) -> bool:
        """Check if enough data accumulated for fine-tuning"""
        pass

    @abstractmethod
    def finetune(self, training_data: Dict[str, Any]) -> 'FinetuneResult':
        """Execute fine-tuning (SOAR-style)"""
        pass


# =============================================================================
# ENVIRONMENT INTERFACE
# =============================================================================

class Environment(ABC):
    """Execution environment for tasks"""

    @abstractmethod
    def reset(self, task: Task) -> str:
        """Reset environment with a new task, returns initial observation"""
        pass

    @abstractmethod
    def step(self, action: str) -> Tuple[str, float, bool, Dict]:
        """Execute action, returns (observation, reward, done, info)"""
        pass

    @abstractmethod
    def verify(self, solution: Any) -> Outcome:
        """Verify a solution"""
        pass

    @property
    @abstractmethod
    def max_steps(self) -> int:
        """Maximum steps before timeout"""
        pass


# =============================================================================
# AGENT INTERFACE
# =============================================================================

class Agent(ABC):
    """Agent that produces trajectories"""

    @abstractmethod
    def solve(self, task: Task, env: Environment) -> Trajectory:
        """Attempt to solve a task, returns trajectory"""
        pass

    @abstractmethod
    def step(self, observation: str) -> str:
        """Given observation, return action"""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset agent state"""
        pass
```

---

## 5. Implementation Directions

### 5.1 Phase 0: Foundation (Weeks 1-2)

**Goal**: Establish core primitives and basic infrastructure

```
Priority 1: Core Data Structures
├── Implement Trajectory, Step, Outcome dataclasses
├── Implement Task with domain support
└── Basic serialization (JSON/pickle)

Priority 2: Environment Interfaces
├── Define Environment ABC
├── Implement basic ARC environment (grid matching)
└── Implement basic SWE environment (test execution)

Priority 3: Trajectory Collection
├── Unified format for external agent outputs
├── Simple storage (SQLite or JSON files)
└── Basic CLI for running and collecting
```

### 5.2 Phase 1: Memory Systems (Weeks 3-4)

**Goal**: Implement the three memory types

```
Priority 1: Experience Memory
├── Vector database setup (ChromaDB or similar)
├── Embedding model integration (BAAI/bge-base-en-v1.5)
├── Search and store operations
└── Basic pruning

Priority 2: Concept Library
├── Primitive loading per domain
├── Stitch integration for compression
├── LILO AutoDoc for documentation
└── Search by semantic similarity

Priority 3: Strategy Bank
├── Strategy abstraction from trajectories
├── Situation embedding and matching
└── Success rate tracking
```

### 5.3 Phase 2: Search Methods (Weeks 5-6)

**Goal**: Implement search engines

```
Priority 1: Task Router
├── Memory query aggregation
├── Routing logic based on domain + similarity
└── Budget estimation

Priority 2: Mind Evolution (ARC)
├── Population initialization from memory
├── LLM mutation/crossover operators
├── Fitness evaluation with verifier
└── Elite selection and iteration

Priority 3: SWE-Search (SWE)
├── Basic MCTS tree structure
├── UCB selection with memory guidance
├── Test-based verification
└── Discriminator model (optional)
```

### 5.4 Phase 3: Learning Engine (Weeks 7-8)

**Goal**: Implement learning from trajectories

```
Priority 1: Trajectory Analyzer
├── Success/failure classification
├── Step attribution (which steps mattered)
└── Error pattern detection

Priority 2: Abstraction Extractor
├── Stitch compression integration
├── Strategy abstraction (ArcMemo-style)
└── AutoDoc for new concepts

Priority 3: Hindsight Learner
├── Training data preparation (SOAR format)
├── Fine-tuning trigger logic
└── Model versioning
```

### 5.5 Phase 4: Integration & Optimization (Weeks 9+)

**Goal**: Full system integration and performance

```
Priority 1: Full Pipeline
├── End-to-end task solving
├── Automatic memory updates
└── Periodic batch learning

Priority 2: Optimization
├── Caching and memoization
├── Parallel search execution
└── Memory pruning and consolidation

Priority 3: Evaluation
├── Benchmark integration (ARC-AGI, SWE-bench)
├── Ablation experiments
└── Cost tracking
```

---

## 6. Open Questions & Decisions Needed

### Architecture Decisions

1. **Vector Database**: ChromaDB vs. Pinecone vs. Qdrant?
   - Recommendation: Start with ChromaDB (local, simple), migrate if needed

2. **Embedding Model**: Which model for semantic similarity?
   - Recommendation: BAAI/bge-base-en-v1.5 (validated in ReMem paper)

3. **LLM Provider**: OpenAI, Anthropic, or local models?
   - Recommendation: Abstract via interface, start with Claude/GPT-4

4. **Fine-tuning Infrastructure**: API fine-tuning vs. local training?
   - Recommendation: Start with API (OpenAI/Anthropic), local for SOAR-style

### Technical Decisions

1. **Stitch Integration**: Use Rust library directly or Python port?
   - Recommendation: Use PyO3 bindings if available, else subprocess

2. **SWE Sandbox**: Docker vs. other isolation?
   - Recommendation: Docker for consistency with SWE-Gym

3. **Storage**: SQLite vs. PostgreSQL vs. file-based?
   - Recommendation: SQLite for start, PostgreSQL for production

### Research Questions

1. **Memory Update Frequency**: Batch vs. online updates?
2. **Cross-Domain Transfer**: Share memory across ARC and SWE?
3. **Hybrid Search**: When to combine evolutionary + MCTS?

---

*Document Version: 1.0*
*Last Updated: December 2025*
