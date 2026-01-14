# Library Learning and Abstraction Extraction Research

## 1. Stitch (POPL 2023)

### Paper Details
- **Title**: "Top-Down Synthesis for Library Learning"
- **Authors**: Matthew Bowers, Theo X. Olausson, Lionel Wong, Gabriel Grand, Joshua B. Tenenbaum, Kevin Ellis, Armando Solar-Lezama
- **Venue**: POPL 2023
- **ArXiv**: https://arxiv.org/abs/2211.16605

### Core Algorithm

**Stitch** uses a corpus-guided top-down synthesis approach that is fundamentally different from DreamCoder's bottom-up approach:

1. **Compression-Guided Extraction**: Instead of enumerating candidate abstractions, Stitch analyzes the existing corpus of programs to find reusable patterns.

2. **Anti-unification**: The key technique is anti-unification (generalization) of program fragments:
   - Finds common structure between program pairs
   - Generalizes differences into parameters
   - Creates lambda abstractions for reusable patterns

3. **Top-Down Strategy**:
   - Analyzes the entire corpus at once
   - Identifies high-value abstractions based on compression potential
   - Extracts abstractions that maximize reuse across programs

### How Abstractions Are Discovered

1. **Pattern Matching**: Stitch identifies repeated patterns across the program corpus
2. **Generalization**: Uses anti-unification to create parameterized versions of common patterns
3. **Compression-Based Selection**: Ranks candidate abstractions by how much they compress the corpus
4. **Iterative Refinement**: Can extract multiple layers of abstractions (abstractions using other abstractions)

### Compression Measurement

- **Metric**: Total size of the corpus when expressed using the discovered library
- **Calculation**: Sum of:
  - Size of library definitions (abstraction bodies)
  - Size of programs rewritten using the library
- **Goal**: Minimize total description length (MDL principle)

### Integration with Neural Networks

Stitch itself is **symbolic** and doesn't directly integrate neural networks. However:
- Can be used as a library learning component in neurosymbolic systems
- Output libraries can be used to train neural program synthesizers
- Compatible with neural guidance for program search

### Performance Comparisons

**Speed Improvements**:
- **3-4 orders of magnitude faster** than DreamCoder on equivalent tasks
- Can process larger corpora (100s-1000s of programs)
- Scales to more complex domains

**Quality**:
- Discovers comparable or better abstractions than DreamCoder
- More consistent across different domains
- Better at finding hierarchical abstractions

**Benchmarks**:
- List processing tasks
- Regular expression synthesis
- Logo graphics programs
- Text editing programs

### Code Repository

- **GitHub**: https://github.com/mlb2251/stitch
- **Language**: Rust (for performance)
- **Key Features**:
  - Fast anti-unification implementation
  - Support for multiple DSLs
  - Visualization tools for discovered libraries

---

## 2. LILO (ICLR 2024)

### Paper Details
- **Title**: "LILO: Learning Interpretable Libraries by Compressing and Documenting Code"
- **Authors**: Gabriel Grand, Lionel Wong, Matthew Bowers, Theo X. Olausson, Muxin Liu, Joshua B. Tenenbaum, Jacob Andreas
- **Venue**: ICLR 2024
- **ArXiv**: https://arxiv.org/abs/2310.19791

### Core Algorithm

**LILO** combines library learning with LLM-based documentation in a neurosymbolic framework:

1. **Compression Phase** (Stitch):
   - Uses Stitch to extract symbolic abstractions from program corpus
   - Identifies reusable patterns that compress the corpus

2. **Documentation Phase** (AutoDoc):
   - Uses LLMs to generate natural language documentation for abstractions
   - Creates interpretable names and docstrings
   - Explains what each abstraction does and when to use it

3. **Synthesis Phase**:
   - Uses documented library to guide LLM-based program synthesis
   - LLMs can better utilize abstractions when they have natural language descriptions

### How Abstractions Are Discovered

1. **Symbolic Extraction**: Uses Stitch's anti-unification approach
2. **Semantic Clustering**: Groups similar abstractions
3. **AutoDoc Enhancement**:
   - LLM analyzes abstraction bodies and usage examples
   - Generates human-readable names (e.g., `map`, `filter`, `fold`)
   - Creates docstrings explaining functionality
   - Provides usage examples

### AutoDoc Approach

**Input**: Symbolic abstraction + usage examples from corpus

**Process**:
1. Extract the abstraction's definition
2. Find all call sites in the corpus
3. Prompt LLM with:
   - Abstraction body
   - Example usages
   - Request for name and documentation
4. Generate structured output:
   - Function name
   - Parameter descriptions
   - Natural language explanation
   - Usage guidelines

**Output**: Documented library function that LLMs can understand and use

### Compression Measurement

- **Symbolic Compression**: Same as Stitch (MDL principle)
- **Functional Compression**: Measures how much abstractions improve synthesis success rate
- **Combined Metric**: Balances code compression with synthesis utility

### Integration with Neural Networks

**Tight Integration**:
- **Library Learning**: Symbolic (Stitch)
- **Documentation**: Neural (LLM-based)
- **Synthesis**: Neural (LLM generates code using documented library)

**Neurosymbolic Loop**:
1. Neural synthesis generates initial programs
2. Symbolic compression extracts abstractions
3. Neural documentation makes abstractions interpretable
4. Neural synthesis uses documented library (better performance)
5. Repeat with improved programs

### Performance Comparisons

**Synthesis Improvements**:
- **2-3x better success rate** on program synthesis tasks when using documented libraries
- LLMs can use abstractions more effectively with natural language documentation
- Reduces token usage in synthesis (more concise programs)

**Benchmarks**:
- LOGO graphics generation
- List manipulation tasks
- String processing
- Compositional generalization tasks

**vs. DreamCoder**:
- Faster library learning (inherits Stitch's speed)
- Better LLM integration
- More interpretable abstractions

**vs. Pure LLM Synthesis**:
- Higher success rate on complex tasks
- More consistent abstraction reuse
- Better compositional generalization

### Code Repository

- **GitHub**: https://github.com/gabegrand/lilo
- **Language**: Python (with Rust bindings to Stitch)
- **Key Features**:
  - Stitch integration
  - LLM-based documentation generation
  - Synthesis benchmarks
  - Evaluation tools

---

## 3. DreamCoder (PLDI 2021)

### Paper Details
- **Title**: "DreamCoder: Growing generalizable, interpretable knowledge with wake-sleep Bayesian program learning"
- **Authors**: Kevin Ellis, Catherine Wong, Maxwell Nye, Mathias Sable-Meyer, Luc Cary, Lucas Morales, Luke Hewitt, Armando Solar-Lezama, Joshua B. Tenenbaum
- **Venue**: PLDI 2021
- **ArXiv**: https://arxiv.org/abs/2006.08381

### Core Algorithm: Wake-Sleep Cycle

**DreamCoder** uses an alternating wake-sleep algorithm inspired by cognitive science:

#### Wake Phase (Learning from Data)
1. **Program Synthesis**:
   - Given tasks, synthesize programs that solve them
   - Uses neural-guided search with recognition model
   - Explores program space using current library

2. **Task Solution**:
   - Recognition network proposes likely program structures
   - Enumerative search fills in details
   - Finds programs that solve training tasks

#### Sleep Phase (Dreaming/Library Learning)
1. **Abstraction Extraction**:
   - Analyzes programs from wake phase
   - Identifies common subexpressions
   - Proposes new library functions

2. **Library Refactoring**:
   - Evaluates candidate abstractions by compression
   - Adds valuable abstractions to library
   - Rewrites existing programs using new library

3. **Dreaming**:
   - Generates synthetic tasks using the library
   - Trains recognition network on synthetic data
   - Improves neural guidance for next wake phase

#### Recognition Model Training
- Neural network learns to predict useful program structures
- Trained on both real and synthetic tasks
- Guides search in wake phase toward likely programs

### How Abstractions Are Discovered

1. **Bottom-Up Enumeration**:
   - Enumerates candidate abstractions from program corpus
   - Considers all possible subexpressions as potential abstractions

2. **Compression-Based Selection**:
   - Evaluates each candidate by compression metric
   - Keeps abstractions that reduce total description length

3. **Refactoring**:
   - Rewrites all programs in corpus using new abstractions
   - Can discover hierarchical abstractions over multiple iterations

4. **Versioning**:
   - Maintains multiple versions of library
   - Can backtrack if abstractions don't generalize well

### Compression Measurement

**Minimum Description Length (MDL)**:
- **Library Cost**: Sum of sizes of all abstraction definitions
- **Program Cost**: Sum of sizes of all programs using the library
- **Total Cost**: Library Cost + Program Cost

**Optimization**:
- Find library L that minimizes: |L| + Σ|P_i(L)|
- Where |L| is library size and |P_i(L)| is program i's size using library L

**Bayesian Formulation**:
- Prior favors smaller libraries (Occam's razor)
- Likelihood favors libraries that compress programs well
- Posterior balances both considerations

### Integration with Neural Networks

**Recognition Network**:
- **Architecture**: Neural network (typically LSTM or transformer)
- **Input**: Task specification (input/output examples)
- **Output**: Distribution over program sketches/structures
- **Purpose**: Guide search toward likely program structures

**Training**:
- Supervised learning on solved tasks
- Self-supervised learning on synthetic tasks (dreaming)
- Online learning during wake-sleep cycles

**Neurosymbolic Integration**:
- Neural network proposes (top-down guidance)
- Symbolic search verifies (bottom-up enumeration)
- Library learning improves both neural and symbolic components

### Performance Comparisons

**Capabilities**:
- Can learn libraries across diverse domains:
  - List processing
  - Regular expressions
  - Logo graphics
  - Text editing
  - Physics learning
  - Compositional reasoning

**Limitations**:
- **Speed**: Slow on large corpora (100+ programs)
- **Scalability**: Bottom-up enumeration is expensive
- **Complexity**: Full wake-sleep cycle is computationally intensive

**vs. Hand-Coded Libraries**:
- Discovers domain-appropriate abstractions automatically
- Sometimes finds better abstractions than human designers
- Adapts to specific task distributions

**Benchmarks**:
- Outperforms neural-only approaches on compositional tasks
- Better sample efficiency than pure enumerative search
- Demonstrates cross-domain transfer learning

### Code Repository

- **GitHub**: https://github.com/ellisk42/ec
- **Language**: Python (with OCaml for some synthesis)
- **Key Features**:
  - Wake-sleep algorithm implementation
  - Recognition network training
  - Multiple domain DSLs
  - Extensive benchmarks
  - Visualization tools

---

## Comparison Summary

| Aspect | DreamCoder | Stitch | LILO |
|--------|------------|--------|------|
| **Speed** | Slow (baseline) | 3-4 orders faster | Fast (uses Stitch) |
| **Approach** | Bottom-up enumeration | Top-down anti-unification | Hybrid neurosymbolic |
| **Neural Integration** | Recognition network | None (symbolic only) | LLM documentation + synthesis |
| **Interpretability** | Symbolic abstractions | Symbolic abstractions | Natural language documented |
| **Scalability** | 10s-100s programs | 100s-1000s programs | 100s-1000s programs |
| **Key Innovation** | Wake-sleep learning | Fast corpus compression | LLM-interpretable libraries |
| **Use Case** | Cognitive modeling | Fast library extraction | LLM-based synthesis |

## Key Insights

### Evolution of Techniques
1. **DreamCoder (2021)**: Established wake-sleep paradigm, showed library learning works
2. **Stitch (2023)**: Made library learning practical with speed improvements
3. **LILO (2024)**: Made libraries interpretable to LLMs, enabling better synthesis

### Common Principles
- **Compression**: All use MDL principle for abstraction selection
- **Iteration**: All support iterative refinement of libraries
- **Compositionality**: All discover hierarchical abstractions

### Complementary Strengths
- **DreamCoder**: Best for cognitive modeling and understanding learning
- **Stitch**: Best for fast, large-scale library extraction
- **LILO**: Best for practical LLM-based synthesis with learned abstractions

### Future Directions
- Combining DreamCoder's recognition networks with Stitch's speed
- Extending AutoDoc to other modalities (visual, interactive)
- Scaling to even larger corpora and more complex domains
- Transfer learning across domains using shared libraries
