# ATLAS Research Synthesis: Key Findings and Implementation Priorities

## Executive Summary

After comprehensive research into the papers referenced in the ATLAS plan, this document synthesizes the key findings and provides actionable implementation priorities. The research validates the ATLAS architecture while revealing specific implementation insights.

**Document Version**: 2.0 (Updated with Evo-Memory, SAGE, and Poetiq findings)

---

## Critical Research Updates

### Papers Verified vs. Gaps Identified

| Paper | Status | Notes |
|-------|--------|-------|
| **Evo-Memory** (arXiv:2511.20857) | ✅ **Verified** | Google DeepMind, Nov 2025. ReMem framework for test-time learning |
| **SAGE** (Salesforce 2025) | ⚠️ **Limited Info** | Training-free plan induction - paper details unclear |
| **Poetiq/Mind Evolution** | ✅ **Well Documented** | 54% ARC-AGI-2 SOTA, meta-system approach |
| **Stitch/LILO** | ✅ **Complete** | Library learning, 1000x faster than DreamCoder |
| **ArcMemo** | ✅ **Key Finding** | Concept-level > instance-level at all scales |
| **SWE-Gym/SOAR** | ✅ **Complete** | Self-improvement loop, trajectory curation critical |

---

## 1. Core Finding: The Three Pillars of Meta-Learning

The research confirms three essential capabilities that must work together:

### Pillar 1: Memory Systems (What to Remember)

| System | Paper | Key Insight | ATLAS Mapping |
|--------|-------|-------------|---------------|
| **Concept Library** | Stitch/LILO | Compression-based abstraction extraction is 1000x faster than enumeration | `ConceptLibrary.compress()` |
| **Experience Memory** | Evo-Memory/ReMem | Test-time learning with search-synthesize-evolve loop; 2x step efficiency | `ExperienceMemory.search()` |
| **Strategy Bank** | ArcMemo | Concept-level > instance-level at ALL compute scales | `StrategyBank.read()` |

**Critical Insight from ArcMemo**: Abstract strategies (e.g., "look for symmetry then apply to each half") outperform concrete examples at every budget level. This validates ATLAS's three-tier memory design.

### Pillar 2: Search Methods (How to Solve)

| Method | Paper | Best For | Cost | Improvement |
|--------|-------|----------|------|-------------|
| **Mind Evolution** | arXiv:2501.09891 | ARC-AGI, hard single tasks | $2-8/task | +10-12pp |
| **SWE-Search** | ICLR 2025 | Software engineering, sequential edits | $4-12/task | +23% relative |
| **AgentTrek** | ICLR 2025 | Training data synthesis | $0.55/traj | 45x cheaper than human demos |

**Critical Insight**: Different search methods excel for different domains. ATLAS should route to appropriate search based on task type.

### Pillar 3: Self-Improvement (How to Learn)

| Approach | Paper | Method | Result |
|----------|-------|--------|--------|
| **SOAR** | ICML 2025 | Fine-tune on own trajectories | 52% ARC-AGI |
| **SAGE** | Salesforce 2025 | Training-free plan induction | Works without weight updates |
| **AgentTrek** | ICLR 2025 | Synthesize 3x training data | $1.1k for 2000 trajectories |

**Critical Insight from SWE-Gym**: "Self-improvement is not yet working with naive approaches." Success requires: (1) high-quality trajectories, (2) proper data curation, (3) separate sampling vs refinement capabilities.

---

## 2. Paper-by-Paper Key Takeaways

### Library Learning (Stitch/LILO/DreamCoder)

**Evolution of Techniques**:
1. **DreamCoder (2021)**: Established wake-sleep paradigm, proved library learning works
2. **Stitch (2023)**: Made it practical with 3-4 orders of magnitude speedup
3. **LILO (2024)**: Made libraries interpretable to LLMs with AutoDoc

**Implementation Priority**: Use Stitch for compression, LILO for documentation

```
Speed comparison:
- DreamCoder: 1 hour for 100 programs
- Stitch: 1 second for 100 programs
- LILO: 5 seconds for 100 programs (includes LLM documentation)
```

**Key Algorithm - Anti-Unification**:
- Find common patterns between program pairs
- Generalize differences into parameters
- Score by compression (MDL principle)
- Iteratively extract best abstractions

### Search Methods (Mind Evolution/SWE-Search)

**Mind Evolution for ARC-AGI**:
- Population-based evolutionary search (20-50 candidates)
- LLM acts as mutation and crossover operator
- 5-10 generations per task
- Best for tasks with clear fitness functions (grid matching)

**SWE-Search for Software Engineering**:
- MCTS + self-evaluation discriminator
- Tree search in continuous edit space
- 50-200 node expansions per task
- Best for sequential decision tasks

**Key Insight**: Initialize search from memory for 2x faster convergence

### Memory Systems (ArcMemo/Evo-Memory/Voyager)

**ArcMemo's Key Finding**:
```
At ANY compute budget:
  Concept-level memory > Instance-level memory

This holds whether you have:
- 10 LLM calls
- 100 LLM calls
- 1000 LLM calls
```

**Evo-Memory/ReMem (arXiv:2511.20857) - NEW FINDINGS**:

Google DeepMind's framework for test-time learning with self-evolving memory:

**ReMem Architecture - Three Modules**:
1. **Think**: Produces internal reasoning traces to decompose tasks
2. **Act**: Executes operations in environment or outputs responses
3. **Refine**: Meta-reasoning over memory - exploiting useful experiences, pruning noise, reorganizing

**Key Algorithm - Search-Synthesize-Evolve Loop**:
```
(x_t, M_t) →[search] R_t →[synthesis] ŷ_t →[evolve] M_{t+1}
```

**Memory Storage**:
- Experiences stored as (input, predicted_output, feedback) tuples
- Indexed using BAAI/bge-base-en-v1.5 embeddings
- Top-k retrieval (k=4 default) via cosine similarity
- Update rule: `M_{t+1} = U(M_t, m_t)` where U varies by method

**Results (Claude 3.7 Sonnet)**:
| Benchmark | ReMem Success/Progress |
|-----------|----------------------|
| AlfWorld | 0.92 / 0.96 |
| BabyAI | 0.73 / 0.83 |
| PDDL | 0.83 / 0.95 |
| ScienceWorld | 0.62 / 0.89 |

**Step Efficiency Gains**:
- AlfWorld: 22.6 steps → 11.5 steps (2x improvement)
- ScienceWorld: 20.5 steps → 14.0 steps

**Critical**: All experiments use **frozen LLMs** - no fine-tuning, only embeddings & memory change.

**Voyager's Skill Library**:
- Skills as executable code (JavaScript functions)
- Semantic indexing via embeddings
- Compositional reuse (skills call skills)
- Self-verification loop

**Design Pattern for ATLAS**:
```python
class Experience:
    input: str              # Task description
    output: str             # Predicted solution
    feedback: str           # Environment feedback
    embedding: Vector       # BAAI/bge-base-en-v1.5

class ExperienceMemory:
    def search(self, query: str, k: int = 4) -> List[Experience]:
        """Top-k retrieval via cosine similarity"""
        query_emb = self.encoder.encode(query)
        return self.index.search(query_emb, k)

    def refine(self, task: Task, memory: List[Experience]) -> List[Experience]:
        """ReMem-style: exploit useful, prune noise, reorganize"""
        pass
```

### Self-Improvement (SOAR/SAGE/SWE-Gym)

**SOAR's Self-Improvement Loop**:
1. Generate trajectories on tasks
2. Separate into sampling data (initial solutions) and refinement data (iterative fixes)
3. Weight successful examples higher
4. Fine-tune periodically
5. Repeat

**SAGE's Training-Free Alternative** (Salesforce 2025):

*Note: Limited paper details available. Inferred mechanism:*

- Induce plans from successful experiences (not concrete trajectories)
- Store as abstract procedures with situation → action templates
- Retrieve and adapt at inference time via embedding similarity
- No weight updates needed - all improvement through memory + retrieval

**SAGE vs SOAR Comparison**:
| Aspect | SOAR | SAGE |
|--------|------|------|
| Method | Fine-tune weights | Plan retrieval + in-context |
| Cost | High (GPU training) | Low (embedding + retrieval) |
| Speed | Slow (retraining) | Fast (add new plan) |
| Forgetting | Risk of catastrophic | No forgetting (additive) |
| Interpretability | Low (weights) | High (explicit plans) |

**When to Use Which**:
- SAGE: Rapid iteration, no GPU, interpretable improvements
- SOAR: Maximum performance when fine-tuning is feasible

**SWE-Gym's Warning**:
> "Self-improvement is not yet working with naive approaches"

**What Makes It Work**:
- High-quality trajectory curation (491 trajectories → +14% gain)
- Verifier for inference-time scaling (10% → 13.3% with best-of-8)
- Proper training setup with separated capabilities

---

## 2.5 Poetiq's ARC-AGI-2 SOTA (54%) - Deep Dive

Poetiq achieved **54% accuracy at $30.57 per task** on ARC-AGI-2, breaking the 50% barrier. Key findings:

### The Meta-System Architecture

**Core Philosophy**:
- "The prompt is an interface, not the intelligence" - design for iterative refinement
- "LLM as knowledge database" - extract through iterative querying
- "It's LLMs all the way down" - LLMs build, improve, and power the system

**What Makes Poetiq Different**:
| Approach | LLM Calls/Task | Key Innovation |
|----------|----------------|----------------|
| **Poetiq** | **<2** | Meta-system + self-audit |
| Berman | ~500 | Natural language programs |
| Eric Pang | ~10 | Library learning |
| Greenblatt | ~8,000 | Mass sampling |

### Self-Auditing: The Efficiency Secret

The meta-system learns:
1. **When to stop** - confidence estimation from multiple signals
2. **Which strategies work** - per model family (GPT, Claude, Gemini)
3. **Optimal sequencing** - of refinement steps
4. **Model quirks** - specific adaptations per LLM

**Evidence of Adaptation**:
| Configuration | Cost/Task | Accuracy |
|--------------|-----------|----------|
| GPT-OSS-b | <$0.01 | >40% |
| Gemini-3-a | ~$0.50 | ~45-50% |
| Gemini-3-c | ~$30 | 54% |
| Claude Opus 4.5 | ~$60 | ~54% |

### What's NOT Open-Sourced (The Secret Sauce)

Poetiq open-sourced the baseline but NOT:
1. **Strategy discovery mechanism** - how it finds optimal approaches
2. **Self-auditing/confidence estimation** - knowing when to stop
3. **Model-specific adaptations** - per-LLM optimizations
4. **Multi-model routing** - which model for which subtask
5. **Accumulated experience library** - learned patterns

### Path to >60% on ARC-AGI-2

Based on competitor analysis:
| Addition | Expected Gain |
|----------|---------------|
| Library Learning (Pang) | +10-15pp |
| Natural Language Programs (Berman) | +5-10pp |
| Multi-Representation (Greenblatt) | +3-5pp |
| Object-Centric Reasoning | +5-8pp |

**Combined potential**: 54% + 25-40pp = **75-90% on ARC-AGI-2**

### Key Takeaways for ATLAS

1. **Meta-system over base models** - automatic strategy discovery
2. **Self-auditing for efficiency** - avoid wasted compute
3. **Concrete feedback enables targeted refinement** - specific errors, not just "failed"
4. **Model-agnostic design** - same system works across all frontier LLMs

---

## 3. Validated Architecture Decisions

The research validates these ATLAS design choices:

### ✅ Three Memory Types
- **Concept Library**: Stitch + LILO provide fast, interpretable abstractions
- **Experience Memory**: Evo-Memory/ReMem validates search-synthesize-evolve loop with 2x efficiency gains
- **Strategy Bank**: ArcMemo confirms concept-level > instance-level

### ✅ Trajectory-Based Learning
- SWE-Gym: 491 quality trajectories → significant gains
- AgentTrek: Can synthesize 3x more from successful runs
- SOAR: Both success and failure traces valuable

### ✅ Verification Enables Scaling
- SWE-Gym: Verifier enables best-of-k scaling
- SWE-Search: Discriminator model for ranking candidates
- Mind Evolution: Fitness function drives selection

### ✅ Domain Adapters
- ARC needs: grid primitives, visual patterns, symmetry detection
- SWE needs: code editing, test execution, patch application
- Same learning pipeline, different verification

---

## 4. Implementation Priorities

### Phase 0: Infrastructure (Week 0)

```
Priority 1: Trajectory Collection
├── Unified trajectory format (Task, Steps, Outcome)
├── Integration with Claude Code / OpenHands
└── Basic storage (SQLite/JSON for start)

Priority 2: Verification Systems
├── ARC: Grid matching + partial scoring
├── SWE: Docker test execution
└── Confidence estimation
```

### Phase 1: Core Memory + Basic Search (Weeks 1-4)

```
Memory Systems:
├── Experience Memory
│   ├── Vector database (Chroma/Pinecone)
│   ├── Embedding model for tasks
│   └── k-NN retrieval
├── Concept Library (Stitch + LILO)
│   ├── Stitch compression engine
│   ├── AutoDoc documentation
│   └── Primitive loading per domain
└── Strategy Bank
    ├── ArcMemo-style abstraction
    └── Situation → Suggestion format

Search:
├── Mind Evolution for ARC
│   ├── Population initialization from memory
│   ├── LLM mutation/crossover
│   └── Fitness-based selection
└── Basic SWE-Search
    ├── Greedy search with discriminator
    └── Test-based verification
```

**Expected Results After Phase 1**:
- ARC-AGI-1: 40-45% (baseline: 30%)
- SWE-bench Lite: 22-25% (baseline: 18%)

### Phase 2: Advanced Search + Self-Improvement (Weeks 5-8)

```
Advanced Search:
├── Full MCTS for SWE-Search
├── Memory-guided UCB selection
├── Discriminator training
└── Early stopping heuristics

Self-Improvement (SOAR-style):
├── Trajectory analysis
│   ├── Success/failure classification
│   ├── Step attribution
│   └── Error pattern extraction
├── Training data preparation
│   ├── Sampling examples
│   └── Refinement examples
├── AgentTrek synthesis
│   ├── Guided replay
│   ├── Self-critique
│   └── Alternative generation
└── Periodic fine-tuning
```

**Expected Results After Phase 2**:
- ARC-AGI-1: 55-60%
- SWE-bench Lite: 28-32%

### Phase 3: Optimization + Scaling (Weeks 9+)

```
Optimization:
├── GEPA-style prompt optimization
├── Model routing (different models for different subtasks)
├── Parallel execution
└── Caching and memoization

Scaling:
├── Memory pruning and consolidation
├── Curriculum learning
├── Multi-agent coordination
└── Fresh benchmark evaluation (SWE-rebench)
```

**Target Results**:
- ARC-AGI-1: 65-75%
- ARC-AGI-2: 30-40%
- SWE-bench Verified: 32-40%

---

## 5. Critical Implementation Details

### Stitch Integration

```python
# Core algorithm: Anti-unification + MDL scoring
class StitchCompressor:
    def compress(self, programs: List[str]) -> List[Abstraction]:
        # 1. Parse to AST
        ast_programs = [parse(p) for p in programs]

        # 2. Find common patterns via anti-unification
        candidates = self._find_common_patterns(ast_programs)

        # 3. Score by compression
        scored = [(c, self._mdl_score(c, ast_programs)) for c in candidates]

        # 4. Iteratively extract best, rewrite corpus
        abstractions = []
        for _ in range(max_abstractions):
            best = max(scored, key=lambda x: x[1])
            abstractions.append(best[0])
            ast_programs = self._rewrite(ast_programs, best[0])

        return abstractions
```

### Mind Evolution Integration

```python
# Key: Initialize population from memory
class MindEvolutionSearch:
    def search(self, task: Task, memory: Memory) -> List[Candidate]:
        # 50% from memory, 50% novel
        population = []

        # Memory-guided initialization
        for concept in memory.search(task, k=10):
            adapted = self._adapt_concept(concept, task)
            population.append(adapted)

        # Novel generation
        for _ in range(10):
            novel = self._generate_novel(task)
            population.append(novel)

        # Evolution loop
        for gen in range(5):
            fitness = [self._evaluate(c, task) for c in population]
            elites = self._select_top(population, fitness, k=10)
            mutated = [self._mutate(e) for e in elites[:5]]
            crossed = [self._crossover(elites[i], elites[j]) for i,j in pairs]
            population = elites + mutated + crossed

        return population[:5]
```

### SOAR-Style Training Data

```python
# Key: Separate sampling and refinement capabilities
class TrainingDataPreparer:
    def prepare(self, trajectories: List[Trajectory]) -> Dict:
        sampling_data = []    # Learn to generate good initial solutions
        refinement_data = []  # Learn to refine based on feedback

        for traj in trajectories:
            if traj.outcome.success:
                # Learn the successful solution
                sampling_data.append({
                    "input": format_task(traj.task),
                    "output": extract_solution(traj),
                    "weight": 2.0  # Weight successful higher
                })

                # Learn key intermediate steps
                for i, step in enumerate(traj.steps):
                    if is_key_step(traj, i):
                        refinement_data.append({
                            "input": format_with_history(traj, i),
                            "output": step.action,
                            "weight": 1.5
                        })
            else:
                # Learn from failures (error recovery)
                if traj.outcome.error_info:
                    refinement_data.append({
                        "input": format_with_history(traj, len(traj.steps)),
                        "output": f"[ERROR] {traj.outcome.error_info}",
                        "weight": 1.0
                    })

        return {"sampling": sampling_data, "refinement": refinement_data}
```

---

## 6. Cost-Benefit Analysis

### Per-Task Costs

| Configuration | ARC Cost | SWE Cost | Notes |
|--------------|----------|----------|-------|
| Baseline (no memory) | $1/task | $2/task | Single-shot |
| + Memory retrieval | $1.20/task | $2.50/task | +20% for embedding |
| + Mind Evolution/SWE-Search | $5/task | $8/task | 100-200 LLM calls |
| + Full optimization | $3/task | $6/task | With caching |

### Training Costs

| Phase | Cost | Trajectories | Expected Gain |
|-------|------|--------------|---------------|
| Initial collection | $500 | 500 | Baseline |
| AgentTrek synthesis | $1,100 | 2,000 | +10-15pp |
| Fine-tuning (3 rounds) | $2,000 | - | +5-10pp |
| **Total** | **$3,600** | **2,000** | **+15-25pp** |

### ROI Analysis

```
Without ATLAS:
- ARC: 30% at $1/task → $3.33/success
- SWE: 18% at $2/task → $11.11/success

With ATLAS (after training):
- ARC: 60% at $5/task → $8.33/success (but 2x more problems solved)
- SWE: 35% at $8/task → $22.86/success (but 2x more problems solved)

Value proposition:
- Solve 2x more problems
- Training cost amortized over all future tasks
- Memory accumulates value over time
```

---

## 7. Research Gaps and Open Questions

### Identified Gaps

1. **Hybrid Search**: No paper combines evolutionary + MCTS effectively
2. **Online Memory Updates**: All papers use batch learning, not online updates during search
3. **Cross-Domain Transfer**: Memory systems are domain-specific; transfer unclear
4. **Failure Mode Analysis**: Limited systematic study of when these methods fail

### Recommended Experiments

1. **Memory Initialization Ablation**: How much does memory help vs. cold start?
2. **Search Budget Allocation**: Adaptive budget based on task difficulty
3. **Abstraction Quality**: Which abstractions actually help synthesis?
4. **Self-Improvement Dynamics**: When does fine-tuning help vs. hurt?

---

## 8. Key Takeaways for Implementation

### Do First

1. **Implement Stitch compression** - 1000x speedup for library learning
2. **Build Experience Memory with embeddings** - Foundation for all retrieval
3. **Add Mind Evolution for ARC** - Clear fitness function, proven gains
4. **Set up trajectory collection** - All learning depends on this

### Do Carefully

1. **Self-improvement loop** - "Not yet working with naive approaches" (SWE-Gym)
2. **Memory pruning** - Keep diverse + high-quality, not just recent
3. **Domain adaptation** - Different primitives for ARC vs. SWE

### Avoid

1. **DreamCoder's wake-sleep** - Too slow, use Stitch instead
2. **Instance-level memory only** - Concept-level always better (ArcMemo)
3. **Single search method** - Route to appropriate method by task type
4. **Massive sampling without verification** - Quality over quantity

---

## 9. Success Metrics

### 8-Week Checkpoint

- [ ] ARC-AGI-1 accuracy > 50%
- [ ] SWE-bench Lite resolve rate > 25%
- [ ] Library grows with each batch (>10 concepts/100 trajectories)
- [ ] Experience Memory retrieval improves performance
- [ ] Self-improvement loop functional (even if gains small)

### 16-Week Target

- [ ] ARC-AGI-2 accuracy > 30%
- [ ] SWE-bench Verified resolve rate > 28%
- [ ] Cost per task < $5 with optimizations
- [ ] Demonstrable improvement each epoch
- [ ] Generalizes to new task distributions

---

## References

### Core Papers (Highest Priority)

1. **Stitch** (POPL 2023) - Library learning speedup
2. **LILO** (ICLR 2024) - LLM-interpretable libraries
3. **ArcMemo** (arXiv:2509.04439) - Concept > instance memory
4. **Mind Evolution** (arXiv:2501.09891) - Evolutionary LLM search
5. **SWE-Gym** (arXiv:2412.21139) - Training environment + verification
6. **SOAR** (ICML 2025) - Self-improvement loop
7. **Evo-Memory/ReMem** (arXiv:2511.20857) - Test-time learning with self-evolving memory

### Supporting Papers

8. **SWE-Search** (ICLR 2025) - MCTS for code
9. **AgentTrek** (ICLR 2025) - Trajectory synthesis
10. **Voyager** (arXiv:2305.16291) - Skill libraries
11. **DreamCoder** (PLDI 2021) - Wake-sleep paradigm
12. **SAGE** (Salesforce 2025) - Training-free plan induction (limited details)

### Poetiq Resources

- Blog: [poetiq.ai/posts/arcagi_announcement/](https://poetiq.ai/posts/arcagi_announcement/)
- Code: [github.com/poetiq-ai/poetiq-arc-agi-solver](https://github.com/poetiq-ai/poetiq-arc-agi-solver)
- Mind Evolution Paper: arXiv:2501.09891

### Code Repositories

- `github.com/mlb2251/stitch` - Stitch (Rust)
- `github.com/gabegrand/lilo` - LILO (Python)
- `github.com/lucidrains/mind-evolution` - Mind Evolution
- `github.com/SWE-Gym/SWE-Gym` - Training environment
- `github.com/epang080516/arc_agi` - Eric Pang's library learning (77.1% ARC-AGI-1)

---

*Document Version: 2.0*
*Last Updated: December 2025*
*Synthesis of research for ATLAS framework implementation*

---

## Appendix: Research Coverage Summary

| Pillar | Papers Researched | Coverage | Key Gap |
|--------|-------------------|----------|---------|
| **Memory Systems** | ArcMemo, Evo-Memory/ReMem, Voyager | ✅ Complete | - |
| **Search Methods** | Mind Evolution, SWE-Search, AgentTrek | ✅ Complete | - |
| **Self-Improvement** | SOAR, SWE-Gym, AgentTrek | ✅ Complete | SAGE details limited |
| **SOTA Approaches** | Poetiq, Berman, Pang, Greenblatt | ✅ Complete | - |
| **Library Learning** | Stitch, LILO, DreamCoder | ✅ Complete | - |

**Sources**:
- [Evo-Memory Paper](https://arxiv.org/abs/2511.20857)
- [MarkTechPost Coverage](https://www.marktechpost.com/2025/12/02/google-deepmind-researchers-introduce-evo-memory-benchmark-and-remem-framework-for-experience-reuse-in-llm-agents/)
- [ARC Prize 2025 Results](https://arcprize.org/blog/arc-prize-2025-results-analysis)
