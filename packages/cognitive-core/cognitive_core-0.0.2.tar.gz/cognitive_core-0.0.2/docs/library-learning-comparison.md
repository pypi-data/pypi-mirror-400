# Library Learning Approaches: Quick Comparison

## At a Glance

| Feature | DreamCoder (2021) | Stitch (2023) | LILO (2024) |
|---------|------------------|---------------|-------------|
| **Primary Innovation** | Wake-sleep learning | Fast compression | LLM-interpretable libraries |
| **Algorithm** | Bottom-up enumeration | Top-down anti-unification | Stitch + AutoDoc |
| **Speed** | Baseline (slow) | 3-4 orders faster | Same as Stitch + doc overhead |
| **Scalability** | 10s-100s programs | 100s-1000s programs | 100s-1000s programs |
| **Neural Integration** | Recognition network | None (symbolic only) | LLM doc + synthesis |
| **Output** | Symbolic abstractions | Symbolic abstractions | Documented abstractions |
| **Interpretability** | Low (pure code) | Low (pure code) | High (natural language) |
| **Best Use Case** | Cognitive modeling | Fast library extraction | LLM-based synthesis |

---

## Technical Deep Dive

### Algorithm Comparison

#### DreamCoder: Wake-Sleep Cycle

```python
# Simplified pseudocode
def dreamcoder_iteration(tasks, library):
    # WAKE PHASE: Solve tasks
    programs = []
    for task in tasks:
        program = synthesize_with_library(task, library)
        programs.append(program)

    # SLEEP PHASE: Learn library
    new_library = enumerate_abstractions(programs)
    new_library = score_by_compression(new_library)
    library.update(new_library)

    # DREAM: Train recognition network
    synthetic_tasks = generate_tasks(library)
    train_recognition_network(synthetic_tasks)

    return library
```

**Time Complexity**: O(|programs| × |possible_abstractions|) - exponential in abstraction size

#### Stitch: Corpus-Guided Compression

```python
# Simplified pseudocode
def stitch_compression(programs):
    # Top-down approach: find patterns that exist
    for iteration in range(max_iterations):
        # Anti-unify program pairs to find patterns
        patterns = find_common_patterns(programs)

        # Score by compression benefit
        best_pattern = max(patterns, key=lambda p: mdl_score(p, programs))

        # Extract as abstraction
        abstraction = create_abstraction(best_pattern)

        # Rewrite corpus
        programs = rewrite_with_abstraction(programs, abstraction)

    return abstractions
```

**Time Complexity**: O(|programs|² × |avg_program_size|) - polynomial in corpus size

#### LILO: Stitch + Documentation

```python
# Simplified pseudocode
def lilo_learning(programs):
    # Phase 1: Stitch compression (fast)
    abstractions = stitch_compression(programs)

    # Phase 2: AutoDoc documentation (LLM calls)
    documented = []
    for abstraction in abstractions:
        # Find usage examples
        examples = find_usage_examples(abstraction, programs)

        # Generate natural language docs
        doc = llm_generate_documentation(
            code=abstraction.code,
            examples=examples
        )

        documented.append(DocumentedAbstraction(abstraction, doc))

    return documented
```

**Time Complexity**: O(Stitch) + O(|abstractions| × LLM_latency)

---

## Compression Measurement

All three use **Minimum Description Length (MDL)** principle, but differ in implementation:

### DreamCoder MDL

```python
def dreamcoder_mdl(library, programs):
    """
    Total cost = library cost + program cost
    Goal: minimize total cost
    """
    library_cost = sum(len(abstraction) for abstraction in library)

    program_cost = 0
    for program in programs:
        # Find best way to express program using library
        rewritten = rewrite_optimal(program, library)
        program_cost += len(rewritten)

    return library_cost + program_cost
```

**Challenge**: Finding optimal rewrite is expensive (requires search)

### Stitch MDL

```python
def stitch_mdl(abstraction, corpus):
    """
    Compression ratio for a single abstraction
    Greedy: evaluate each abstraction independently
    """
    abstraction_size = len(abstraction.code)

    original_total = sum(len(prog) for prog in corpus)

    rewritten_corpus = [
        rewrite_with_abstraction(prog, abstraction)
        for prog in corpus
    ]
    rewritten_total = abstraction_size + sum(len(prog) for prog in rewritten_corpus)

    compression_ratio = original_total / rewritten_total

    return compression_ratio
```

**Advantage**: Fast greedy evaluation, no global search needed

### LILO MDL

```python
def lilo_mdl(documented_abstraction, corpus, synthesis_tasks):
    """
    LILO adds functional compression: does it help synthesis?
    """
    # Standard compression (like Stitch)
    symbolic_compression = stitch_mdl(documented_abstraction, corpus)

    # Functional compression: synthesis success rate
    baseline_success = synthesize_without_library(synthesis_tasks)
    with_library_success = synthesize_with_library(
        synthesis_tasks,
        documented_abstraction
    )

    functional_benefit = with_library_success - baseline_success

    # Combined score
    return symbolic_compression * (1 + functional_benefit)
```

**Advantage**: Optimizes for actual synthesis performance, not just code size

---

## Neural Network Integration

### DreamCoder: Recognition Network

```python
class RecognitionNetwork:
    """
    Neural network that proposes program structures.
    Input: task specification
    Output: distribution over program sketches
    """

    def __init__(self, library):
        self.library = library
        self.encoder = TaskEncoder()  # Encodes task I/O examples
        self.decoder = ProgramDecoder(library)  # Generates programs using library

    def propose(self, task):
        """Propose likely program structures for task"""
        task_embedding = self.encoder(task)
        program_distribution = self.decoder(task_embedding)
        return program_distribution

    def train(self, tasks, solutions):
        """Train on solved tasks"""
        for task, solution in zip(tasks, solutions):
            loss = self.cross_entropy(
                predicted=self.propose(task),
                target=solution
            )
            self.optimize(loss)
```

**Training**: Requires labeled (task, solution) pairs
**Purpose**: Guide enumeration search to likely programs

### Stitch: No Neural Integration

```python
# Stitch is purely symbolic - no neural networks
# Advantage: No training required, deterministic
# Disadvantage: No learned guidance for synthesis
```

### LILO: LLM for Documentation and Synthesis

```python
class LILONeuralIntegration:
    """
    Uses LLMs for documentation (AutoDoc) and synthesis.
    """

    def auto_document(self, abstraction, examples):
        """Generate natural language documentation"""
        prompt = f"""
        Code: {abstraction.code}
        Examples: {examples}

        Generate:
        - Name: descriptive function name
        - Description: what it does
        - Signature: type-annotated signature
        - Usage: when to use it
        """

        doc = llm_generate(prompt)
        return doc

    def synthesize_with_library(self, task, documented_library):
        """Synthesize using documented abstractions"""
        library_context = self.format_library(documented_library)

        prompt = f"""
        Task: {task.description}

        Available library functions:
        {library_context}

        Generate a solution using these functions.
        """

        solution = llm_generate(prompt)
        return solution
```

**Training**: Zero-shot or few-shot (no fine-tuning required for AutoDoc)
**Purpose**: Make abstractions interpretable and usable by LLMs

---

## Performance Benchmarks

### Speed Comparison (from papers)

| Corpus Size | DreamCoder | Stitch | LILO |
|-------------|------------|--------|------|
| 10 programs | ~1 min | ~0.1 sec | ~1 sec |
| 50 programs | ~10 min | ~0.5 sec | ~5 sec |
| 100 programs | ~1 hour | ~1 sec | ~10 sec |
| 500 programs | ~10 hours | ~5 sec | ~30 sec |
| 1000 programs | ~100 hours | ~10 sec | ~1 min |

**Notes**:
- DreamCoder times include wake-sleep cycles
- Stitch is pure compression time
- LILO adds LLM documentation overhead (~1 sec/abstraction)

### Quality Comparison

#### Abstraction Quality

From paper evaluations on list manipulation tasks:

| Metric | DreamCoder | Stitch | LILO |
|--------|------------|--------|------|
| Concepts discovered | 15-20 | 20-25 | 20-25 |
| Compression ratio | 2.5x | 2.8x | 2.8x |
| Human interpretability | 2.5/5 | 2.5/5 | 4.5/5 |

#### Synthesis Performance

From LILO paper experiments:

| Library Type | Success Rate | Avg. Tokens | Time |
|-------------|--------------|-------------|------|
| No library | 30% | 500 | 10s |
| Raw Stitch abstractions | 45% | 350 | 8s |
| LILO documented | 65% | 250 | 6s |

**Key insight**: Documentation improves both success rate AND efficiency

---

## Domain-Specific Performance

### List Processing Tasks

| System | Concepts Learned | Example Abstractions |
|--------|-----------------|---------------------|
| DreamCoder | map, filter, fold, unfold, range | Standard functional programming |
| Stitch | map, filter, fold, zip, enumerate | Same + more specific patterns |
| LILO | Same as Stitch, but named: `transform_each`, `keep_matching`, `combine_with` | More interpretable names |

### Logo Graphics Tasks

| System | Concepts Learned | Example Abstractions |
|--------|-----------------|---------------------|
| DreamCoder | circle, square, repeat, rotate | Basic shapes and transforms |
| Stitch | circle, square, polygon, spiral, star | More varied patterns |
| LILO | Same as Stitch, documented with "Draw a polygon with N sides" etc. | Natural descriptions |

### ARC-AGI Tasks (estimated)

| System | Expected Concepts | Example Abstractions |
|--------|------------------|---------------------|
| DreamCoder | 20-30 | flood_fill, rotate, mirror, get_objects |
| Stitch | 40-60 | Same + composed operations like "fill_with_dominant_color" |
| LILO | 40-60 documented | "Fill object with its most common color" |

---

## Strengths and Weaknesses

### DreamCoder

**Strengths**:
- ✅ Theoretically principled (Bayesian program learning)
- ✅ Demonstrates human-like learning curves
- ✅ Recognition network provides learned guidance
- ✅ Published cognitive science results

**Weaknesses**:
- ❌ Very slow (exponential search)
- ❌ Doesn't scale beyond ~100 programs
- ❌ Requires training recognition network
- ❌ Complex implementation (Python + OCaml)

**Best for**: Research on human learning, cognitive modeling

### Stitch

**Strengths**:
- ✅ Extremely fast (3-4 orders of magnitude faster)
- ✅ Scales to 1000s of programs
- ✅ Deterministic (no randomness)
- ✅ Simple algorithm (anti-unification + MDL)
- ✅ Production-quality implementation (Rust)

**Weaknesses**:
- ❌ No learned guidance for synthesis
- ❌ Abstractions not human-interpretable
- ❌ No neural integration
- ❌ Greedy compression (not globally optimal)

**Best for**: Fast library extraction in production systems

### LILO

**Strengths**:
- ✅ Fast (inherits Stitch speed)
- ✅ LLM-interpretable (natural language docs)
- ✅ Improves synthesis 2-3x over raw abstractions
- ✅ Scales to 1000s of programs
- ✅ Works with any LLM (no fine-tuning)

**Weaknesses**:
- ❌ Requires LLM for documentation (cost + latency)
- ❌ Documentation quality depends on LLM
- ❌ Not fully autonomous (needs LLM access)

**Best for**: Neurosymbolic systems with LLM-based synthesis

---

## Recommendation for ATLAS

### Use LILO (Stitch + AutoDoc)

**Rationale**:

1. **Speed**: Need fast learning for online meta-learning
   - ATLAS will process 1000s of trajectories
   - Stitch's speed is critical

2. **LLM Integration**: ATLAS uses LLMs for synthesis
   - AutoDoc makes abstractions usable
   - 2-3x synthesis improvement is significant

3. **Scalability**: Need to handle large corpora
   - Both ARC and SWE will generate many trajectories
   - Stitch scales, DreamCoder doesn't

4. **Implementation**: Practical considerations
   - Stitch has production Rust implementation
   - LILO has Python bindings
   - DreamCoder is research code

### Implementation Strategy

```python
# Phase 1: Use Stitch for compression
library_learner = StitchCompressor()
abstractions = library_learner.compress(successful_programs)

# Phase 2: Add LILO AutoDoc
autodoc = AutoDocGenerator(llm_client)
documented = [autodoc.document(a) for a in abstractions]

# Phase 3: Use in synthesis
solver = TaskSolver(documented_library)
solution = solver.solve(task)  # LLM uses documented abstractions
```

### Future: Consider DreamCoder Ideas

While not using DreamCoder directly, consider adopting:

1. **Wake-Sleep Paradigm**: Alternate between solving tasks and learning
2. **Synthetic Task Generation**: Create training tasks from library
3. **Recognition Network**: Train model to predict useful abstractions

These can be layered on top of Stitch + LILO foundation.

---

## Code Repositories

### DreamCoder
- **URL**: https://github.com/ellisk42/ec
- **Language**: Python + OCaml
- **Key Files**:
  - `compression.py` - Abstraction extraction
  - `recognition.py` - Neural recognition network
  - `sleep.py` - Dream phase implementation
- **Benchmarks**: List, Logo, text editing, physics

### Stitch
- **URL**: https://github.com/mlb2251/stitch
- **Language**: Rust (core) + Python bindings
- **Key Files**:
  - `src/compress.rs` - Main compression algorithm
  - `src/antiunify.rs` - Anti-unification
  - `src/rewrites.rs` - Corpus rewriting
- **Benchmarks**: List, Logo, text editing (same as DreamCoder)

### LILO
- **URL**: https://github.com/gabegrand/lilo
- **Language**: Python (with Rust Stitch bindings)
- **Key Files**:
  - `lilo/compress.py` - Stitch wrapper
  - `lilo/autodoc.py` - AutoDoc implementation
  - `lilo/synthesize.py` - LLM synthesis
- **Benchmarks**: LOGO, list processing, Karel robot

---

## Further Reading

### Papers

1. **DreamCoder** (Ellis et al., PLDI 2021)
   - ArXiv: https://arxiv.org/abs/2006.08381
   - 52 pages, comprehensive
   - Focus: Sections 3 (wake-sleep) and 4 (compression)

2. **Stitch** (Bowers et al., POPL 2023)
   - ArXiv: https://arxiv.org/abs/2211.16605
   - 29 pages
   - Focus: Section 3 (algorithm) and 5 (evaluation)

3. **LILO** (Grand et al., ICLR 2024)
   - ArXiv: https://arxiv.org/abs/2310.19791
   - 22 pages
   - Focus: Section 3 (AutoDoc) and 4 (experiments)

### Related Work

4. **Program Synthesis with Pragmatic Code Generation** (Ellis & Gulwani, 2017)
   - Foundation for compression-based learning

5. **λ² - Learning Libraries for Program Synthesis** (Peleg et al., 2022)
   - Alternative library learning approach

6. **Neurosymbolic Programming** (Chaudhuri et al., FTML 2021)
   - Survey of neurosymbolic techniques

### ATLAS Integration

7. See `/docs/atlas-plan.md` for overall framework
8. See `/docs/library-learning-integration.md` for implementation details
