# ARC-AGI Implementation Resources: A Comprehensive Reading List

This document contains all the technical resources you need to design and implement the key components for surpassing Poetiq's ARC-AGI results. Resources are organized by component, with priority rankings.

---

## 1. Core Algorithm: Mind Evolution (Evolutionary Search)

The foundation of Poetiq's approach. This is your most important starting point.

### Primary Resources

| Resource | Type | URL | Priority |
|----------|------|-----|----------|
| **Mind Evolution Paper** | Academic Paper | https://arxiv.org/abs/2501.09891 | ⭐⭐⭐ CRITICAL |
| **lucidrains Implementation** | Code | https://github.com/lucidrains/mind-evolution | ⭐⭐⭐ CRITICAL |
| **Poetiq Open-Source Solver** | Code | https://github.com/poetiq-ai/poetiq-arc-agi-solver | ⭐⭐⭐ CRITICAL |

### Key Concepts from Mind Evolution

The paper introduces an evolutionary search strategy with these core components:

1. **Population-based search** — Maintain diverse candidate solutions
2. **LLM-driven operators**:
   - Generation: Create initial candidates
   - Crossover: Combine promising aspects of parent solutions
   - Refinement: Improve candidates based on evaluator feedback
   - Selection: Keep top performers
3. **Global evaluation** — Score complete solutions, not intermediate steps
4. **No formalization required** — Only needs an outcome evaluator

The algorithm solves **99% of TravelPlanner and Natural Plan tasks** and outperforms Best-of-N and Sequential Revision by 10-30%.

---

## 2. Evolutionary Test-Time Compute (Jeremy Berman's Approach)

The original approach that inspired many current methods.

### Primary Resources

| Resource | Type | URL | Priority |
|----------|------|-----|----------|
| **Original Blog Post (v1)** | Technical Write-up | https://jeremyberman.substack.com/p/how-i-got-a-record-536-on-arc-agi | ⭐⭐⭐ CRITICAL |
| **Natural Language v2 Post** | Technical Write-up | https://jeremyberman.substack.com/p/how-i-got-the-highest-score-on-arc-agi-again | ⭐⭐⭐ CRITICAL |
| **Detailed Prompts (Params)** | Prompts/Code | https://params.com/@jeremy-berman/arc-agi | ⭐⭐ HIGH |
| **Twitter/X Updates** | Updates | https://x.com/jerber888 | ⭐ MEDIUM |

### Key Insights

**v1 (Python Functions)**:
- Generate hundreds of Python transform functions
- Test against training examples
- Use "fittest" candidates to create new prompts
- Iterative refinement cycle

**v2 (Natural Language)**:
- Replaced Python with English descriptions
- Natural language is more expressive than code for complex ARC transformations
- Thinking models handle internal revision, so prioritize breadth over depth
- Achieved 79.6% on ARC-AGI-1, 29.4% on ARC-AGI-2

---

## 3. Library Learning (Eric Pang's DreamCoder-Inspired Approach)

Enables knowledge transfer between tasks — a key weakness in other approaches.

### Primary Resources

| Resource | Type | URL | Priority |
|----------|------|-----|----------|
| **Eric Pang's GitHub** | Code | https://github.com/epang080516/arc_agi | ⭐⭐⭐ CRITICAL |
| **Technical Write-up** | Blog Post | https://ctpang.substack.com/p/arc-agi-2-sota-efficient-evolutionary | ⭐⭐⭐ CRITICAL |
| **Original DreamCoder Paper** | Academic Paper | https://arxiv.org/abs/2006.08381 | ⭐⭐ HIGH |
| **DreamCoder Code** | Code | https://github.com/ellisk42/ec | ⭐⭐ HIGH |
| **DreamCoder for ARC** | Code | https://github.com/mxbi/dreamcoder-arc | ⭐ MEDIUM |

### Key Innovations

- Only **~10 LLM calls per task** (vs. Berman's 500, Greenblatt's 8,000)
- **$2.56/task** at 77.1% accuracy on ARC-AGI-1
- Library grows with each solved task
- Transfers learned concepts to new problems

### DreamCoder Wake-Sleep Algorithm

1. **Wake Phase**: Recognition model proposes candidate programs from library
2. **Sleep (Abstraction)**: Add successful programs to library
3. **Sleep (Dreaming)**: Train recognition model on fantasies and replays

---

## 4. Prompt Optimization with GEPA

For automatically discovering optimal prompting strategies.

### Primary Resources

| Resource | Type | URL | Priority |
|----------|------|-----|----------|
| **GEPA Paper** | Academic Paper | https://arxiv.org/abs/2507.19457 | ⭐⭐⭐ CRITICAL |
| **GEPA GitHub** | Code | https://github.com/gepa-ai/gepa | ⭐⭐⭐ CRITICAL |
| **DSPy GEPA Docs** | Documentation | https://dspy.ai/api/optimizers/GEPA/overview/ | ⭐⭐⭐ CRITICAL |
| **DSPy Framework** | Code | https://github.com/stanfordnlp/dspy | ⭐⭐ HIGH |
| **GEPA Tutorials** | Tutorials | https://dspy.ai/tutorials/gepa_ai_program/ | ⭐⭐ HIGH |
| **HuggingFace Cookbook** | Tutorial | https://huggingface.co/learn/cookbook/dspy_gepa | ⭐⭐ HIGH |

### Why GEPA Matters

- Uses **natural language reflection** instead of RL
- **35x fewer rollouts** than reinforcement learning
- Preserves execution traces for diagnosis
- Pareto-based multi-objective optimization
- Perfect for discovering ARC-solving strategies automatically

### Key GEPA Concepts

```python
# GEPA returns both score and textual feedback
metric(example, prediction) -> dspy.Prediction(score=..., feedback=...)
```

The textual feedback provides visibility into *why* a score was achieved, enabling targeted improvements.

---

## 5. Mass Sampling / AlphaCode-Style Approach (Ryan Greenblatt)

The brute-force baseline that established the paradigm.

### Primary Resources

| Resource | Type | URL | Priority |
|----------|------|-----|----------|
| **Original Blog Post** | Technical Write-up | https://blog.redwoodresearch.org/p/getting-50-sota-on-arc-agi-with-gpt | ⭐⭐ HIGH |
| **Code Repository** | Code | https://github.com/rgreenblatt/arc_draw_more_samples_pub | ⭐⭐ HIGH |
| **MLST Podcast Interview** | Video/Audio | https://open.spotify.com/episode/2lLjVGxDIQJ8WBgKrgGLb6 | ⭐ MEDIUM |

### Key Techniques

- Generate ~8,000 Python programs per task
- Multiple text representations (ASCII, nested list, connected components, diffs)
- Few-shot prompts with meticulous step-by-step reasoning
- Revision step after seeing program outputs
- Voting among promising candidates

---

## 6. ARC Prize Official Resources

Essential context and benchmarks.

### Primary Resources

| Resource | Type | URL | Priority |
|----------|------|-----|----------|
| **ARC Prize 2025 Results** | Analysis | https://arcprize.org/blog/arc-prize-2025-results-analysis | ⭐⭐⭐ CRITICAL |
| **ARC-AGI Dataset** | Data | https://github.com/fchollet/ARC-AGI | ⭐⭐⭐ CRITICAL |
| **Research Compilation** | Links | https://github.com/open-thought/arc-agi-2/blob/main/docs/research.md | ⭐⭐ HIGH |
| **2024 Progress Post** | Analysis | https://arcprize.org/blog/2024-progress-arc-agi-pub | ⭐⭐ HIGH |
| **Deep Learning + Program Synthesis** | Talk | https://arcprize.org/blog/beat-arc-agi-deep-learning-and-program-synthesis | ⭐⭐ HIGH |
| **Public Leaderboard** | Data | https://arcprize.org/blog/introducing-arc-agi-public-leaderboard | ⭐ MEDIUM |

---

## 7. Advanced Techniques & Additional Approaches

### Test-Time Training / Tiny Recursive Models

| Resource | Type | URL | Priority |
|----------|------|-----|----------|
| **TRM Paper** (7M params, 45% accuracy) | Paper | Search "Tiny Recursive Models ARC-AGI" | ⭐⭐ HIGH |
| **CompressARC** (76K params, 20% accuracy) | Paper | Search "CompressARC" | ⭐⭐ HIGH |

### Comprehensive Research Review

| Resource | Type | URL | Priority |
|----------|------|-----|----------|
| **ARC-AGI 2025 Research Review** | Analysis | https://lewish.io/posts/arc-agi-2025-research-review | ⭐⭐ HIGH |
| **State of the Art Summary** | Analysis | https://ironbar.github.io/arc24/03_State_of_the_art/ | ⭐⭐ HIGH |
| **Data Augmentation Paper** | Paper | https://arxiv.org/html/2505.07859v1 | ⭐ MEDIUM |

---

## 8. Implementation Roadmap

Based on the research, here's a suggested order for building your system:

### Phase 1: Baseline (Week 1-2)
1. Clone and run Poetiq's open-source solver
2. Read Ryan Greenblatt's blog post and code
3. Understand the generate → execute → verify → refine loop

### Phase 2: Evolutionary Search (Week 3-4)
4. Read Mind Evolution paper thoroughly
5. Implement basic evolutionary operators using lucidrains' code as reference
6. Add population-based search with crossover and mutation

### Phase 3: Self-Auditing & Termination (Week 5-6)
7. Implement confidence estimation for when to stop
8. Study GEPA for prompt optimization
9. Build feedback loops that learn from failures

### Phase 4: Library Learning (Week 7-8)
10. Study Eric Pang's DreamCoder-inspired approach
11. Implement a growing library of successful programs
12. Enable concept transfer between tasks

### Phase 5: Optimization (Week 9+)
13. Use GEPA to automatically optimize prompts
14. Experiment with natural language programs (Berman v2)
15. Multi-model routing for different task types

---

## 9. Key Papers to Download

| Paper | arXiv ID | Focus |
|-------|----------|-------|
| Mind Evolution | 2501.09891 | Evolutionary LLM reasoning |
| GEPA | 2507.19457 | Prompt optimization |
| DreamCoder | 2006.08381 | Program synthesis + library learning |
| On the Measure of Intelligence | 1911.01547 | Original ARC paper (Chollet) |

---

## 10. Community & Updates

| Resource | URL |
|----------|-----|
| ARC Prize Discord | https://discord.gg/arcprize |
| Poetiq Contact | poetiq@poetiq.ai |
| Jeremy Berman Twitter | https://x.com/jerber888 |
| Eric Pang Substack | https://ctpang.substack.com |

---

## Summary: What's Missing from Poetiq's Open-Source Release

To surpass Poetiq, you need to build these components yourself:

1. **Meta-learning loop** — The system that discovers optimal strategies (Mind Evolution provides the foundation)
2. **Self-auditing termination** — Knowing when a solution is good enough to stop
3. **Strategy discovery** — Automatically selecting which approach to use
4. **Model routing** — Deciding which LLM for which subtask
5. **Accumulated experience** — Learning from each solved puzzle

The resources in this document provide everything you need to build these components. Start with Mind Evolution + Poetiq's baseline, then layer in GEPA for optimization and DreamCoder concepts for library learning.

Good luck! 🚀
