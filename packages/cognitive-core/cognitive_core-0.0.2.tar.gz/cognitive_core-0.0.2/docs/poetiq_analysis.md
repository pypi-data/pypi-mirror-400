# Replicating Poetiq's ARC-AGI breakthrough: A technical roadmap

Poetiq achieved **54% accuracy at $30.57 per task** on ARC-AGI-2's semi-private test set in December 2025, becoming the first to break the 50% barrier. Their approach combines a meta-system called "Mind Evolution" with frontier LLMs to create an iterative refinement loop that dramatically improves model performance without fine-tuning. This report provides implementation-level details to understand and potentially surpass their results.

## The core innovation is evolutionary search, not better prompts

Poetiq's approach builds on **Mind Evolution**, a research paper (arXiv:2501.09891) co-authored by the Poetiq team while at Google DeepMind. The key insight: instead of single-shot prompting or simple sequential revision, use an **evolutionary search strategy** that generates, recombines, and refines candidate solutions based on feedback from a programmatic evaluator.

The meta-system treats the LLM as a "database of knowledge" and focuses on extracting that knowledge through iterative querying. According to Poetiq: "It's LLMs all the way down. We used LLMs to build, improve, and power the system." The core principles are:

- **The prompt is an interface, not the intelligence** — the system engages in iterative problem-solving rather than expecting single-shot solutions
- **Self-auditing** — the system autonomously monitors progress and terminates when confident, avoiding wasteful computation
- **Model-agnostic design** — the same meta-system works across Gemini 3, GPT-5.1, Claude, Grok, and open-source models

This approach achieved fewer than **2 LLM requests per task on average**, far more efficient than competitors using hundreds or thousands of samples.

## Technical architecture: program synthesis through refinement loops

Poetiq's open-source implementation (github.com/poetiq-ai/poetiq-arc-agi-solver) uses Python 3.11+ with async execution for concurrent API calls. The architecture follows this control flow:

1. Load ARC task with input/output grid training pairs
2. Prompt LLM to generate a Python transform function
3. Execute the function against all training examples
4. If verification fails: analyze specific errors (pixel mismatches, dimension errors) and feed detailed feedback back to LLM
5. LLM refines hypothesis based on concrete failure modes
6. Repeat until all training examples pass (or compute budget exhausted)
7. Apply verified function to test input

The system represents ARC grids as **2D numpy arrays** with integer color codes (0-9). Prompts include both textual descriptions and the raw grid data. The LLM generates complete Python functions using numpy and optionally OpenCV for image processing operations.

**Key prompt structure from prompts.py:**
```
You are a world-class expert in solving Abstract Reasoning Corpus (ARC) tasks.
Your goal is to identify a *single, consistent transformation rule* that 
generalizes across *all* examples. Do not give up until you find a correct solution.
```

The prompt mandates a chain-of-thought process: examine grids → formulate hypotheses → implement as code → test rigorously → analyze failures → refine rule → iterate.

## Mind Evolution: the algorithmic foundation

The Mind Evolution algorithm from the DeepMind paper solves **99% of TravelPlanner and Natural Plan tasks** and forms the basis for Poetiq's meta-system. The core components:

**Population-based search:**
- Maintain a diverse population of candidate solutions
- Unlike Best-of-N (broad but shallow) or sequential revision (deep but narrow), Mind Evolution searches both broadly and deeply
- Easy to parallelize across multiple LLM calls

**Evolutionary operators via LLM:**
- **Generation**: Create initial candidate population
- **Crossover**: LLM combines promising aspects of two parent solutions into a child
- **Refinement**: LLM improves individual candidates based on evaluator feedback
- **Selection**: Keep top performers based on fitness (training example correctness)

**Global evaluation, not step-by-step:**
- Unlike Process Reward Models that score each reasoning step, Mind Evolution evaluates complete solutions
- Only requires an outcome evaluator, which for ARC is simply "does the code produce correct outputs on training examples?"

This approach outperforms Best-of-N and Sequential Revision by **10-30%** while using comparable inference compute, according to the paper.

## How Poetiq differs from other top competitors

| Approach | Programs/task | Method | Key innovation |
|----------|--------------|--------|----------------|
| **Poetiq** | <2 | Iterative refinement + self-audit | Meta-system discovers optimal strategies automatically |
| **Berman (79.6%)** | ~500 | Evolutionary natural language | Programs as English descriptions, not code |
| **Eric Pang (77.1%)** | ~10 | DreamCoder-style library | Knowledge transfer between tasks |
| **Greenblatt (50%)** | ~8,000 | Mass sampling + revision | AlphaCode-inspired brute force |
| **MindsAI (55.5%)** | N/A | Test-time fine-tuning | Model weight updates per task |
| **TRM (45%)** | N/A | Recursive tiny networks | 7M parameters, test-time training |

**Poetiq's distinct advantages:**
1. **Extreme efficiency** — uses orders of magnitude fewer LLM calls than evolutionary competitors
2. **Self-auditing termination** — knows when to stop, avoiding wasted compute
3. **Model agnostic** — same meta-system improves GPT, Claude, Gemini, Grok equally
4. **No fine-tuning required** — works with off-the-shelf API models
5. **Automatic strategy discovery** — meta-system learns which approaches work for which model quirks

## Training, compute, and what the system learns

Critically, **Poetiq did not train custom models**. All adaptation happened on open-source models before Gemini 3 and GPT-5.1 were released, and the system was never shown ARC-AGI-2 tasks. This demonstrates genuine transfer and generalization.

**What the meta-system learns:**
- Which questioning strategies extract the most useful information from each model family
- How to recognize when it has sufficient confidence to stop iterating
- Optimal sequencing of refinement steps
- Model-specific "quirks" in information storage and retrieval

**Compute costs across configurations:**
- **Poetiq (GPT-OSS-b)**: >40% accuracy at **<$0.01/task** (open weights, maximum efficiency)
- **Poetiq (Gemini-3-a)**: ~$0.50/task  
- **Poetiq (Gemini-3-c)**: ~$30/task, 54% accuracy (maximum performance)
- **Poetiq (Claude Opus 4.5)**: ~$60/task, similar accuracy to Gemini

The team noted that on ARC-AGI-1, performance **saturates** — additional compute provides no benefit. On ARC-AGI-2, performance continues improving with more resources.

## Limitations and failure modes

**Known bottlenecks:**
1. **Data contamination uncertainty** — public evaluation sets may be in frontier model training data, inflating scores. ARC Prize verification found Gemini using correct ARC color mappings without being told them.
2. **Public vs. semi-private drop** — most models show significant accuracy drops on held-out tasks they've never seen. Poetiq acknowledges expecting similar drops.
3. **Complex spatial reasoning** — tasks requiring novel object manipulation or intricate spatial relationships remain challenging
4. **Compositional generalization** — tasks combining multiple transformation rules are harder than single-rule tasks

**What the approach struggles with:**
- Tasks requiring genuinely novel abstractions not represented in training data
- Problems where the transformation rule is highly context-dependent
- Cases where visual pattern recognition (vs. symbolic reasoning) is essential

## Paths to surpassing Poetiq's results

Based on the research, several promising directions emerge:

**1. Combine library learning with evolutionary refinement**
Eric Pang's approach ($2.56/task at 77.1%) builds reusable abstractions that transfer between tasks. Integrating Poetiq's efficient self-auditing with a growing library of primitives could yield both efficiency and higher accuracy.

**2. Use natural language programs instead of code**
Jeremy Berman's v2 approach (85% on ARC-AGI-1) found that natural language descriptions outperform Python for complex ARC transformations. The descriptive power of English captures patterns that code struggles to express concisely.

**3. Multi-representation inputs**
Greenblatt achieved gains by providing the LLM with multiple views of the same grid: images, ASCII, connected components analysis, input-output diffs. This redundancy helps models notice patterns they'd miss with single representations.

**4. Hierarchical object-centric reasoning**
Instead of raw pixel grids, represent problems in terms of objects (rectangles, lines, bitmaps) with properties and relationships. This matches how humans naturally perceive ARC tasks.

**5. Test-time neural adaptation**
The Tiny Recursive Model (7M parameters, 45% accuracy) and CompressARC (76K parameters, 20% accuracy) show that tiny networks trained per-puzzle at test time can achieve surprising results. Combining this with LLM-based program synthesis could unlock new capabilities.

**6. GEPA-style reflective optimization**
The GEPA prompt optimizer uses natural language reflection (instead of RL) to improve prompts. Applying this to automatically discover better ARC-solving prompts could reduce the need for manual prompt engineering.

## Reproducing the baseline implementation

```bash
# Clone repository
git clone https://github.com/poetiq-ai/poetiq-arc-agi-solver
cd poetiq-arc-agi-solver

# Setup environment  
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure API keys
echo "GEMINI_API_KEY=your_key" > .env
echo "OPENAI_API_KEY=your_key" >> .env

# Run evaluation
# Edit main.py to select tasks: SELECTED_PROBLEMS = ['task_id']
python main.py
```

The default configuration runs the "Poetiq 3" setup from the blog post. Alternative configs are available in config.py.

## Key academic references and resources

**Poetiq's approach:**
- Blog: poetiq.ai/posts/arcagi_announcement/
- Verified results: poetiq.ai/posts/arcagi_verified/
- Code: github.com/poetiq-ai/poetiq-arc-agi-solver

**Mind Evolution paper (theoretical foundation):**
- arXiv:2501.09891 "Evolving Deeper LLM Thinking"
- Authors: Kuang-Huei Lee, Ian Fischer, Yueh-Hua Wu, Dave Marwood, Shumeet Baluja, Dale Schuurmans, Xinyun Chen

**Competing approaches:**
- Jeremy Berman: github.com/jerber/arc-lang-public (79.6% ARC-AGI-1)
- Eric Pang: github.com/epang080516/arc_agi (77.1% ARC-AGI-1, 26% ARC-AGI-2)  
- Ryan Greenblatt: github.com/rgreenblatt/arc_draw_more_samples_pub
- TRM: github.com/SamsungSAILMontreal/TinyRecursiveModels (45% with 7M params)
- CompressARC: github.com/iliao2345/CompressARC (20% with 76K params)

**ARC Prize resources:**
- 2025 Results: arcprize.org/blog/arc-prize-2025-results-analysis
- All winning papers and code are open-source

## Conclusion

Poetiq's breakthrough demonstrates that **refinement loops at the application layer** can dramatically improve AI reasoning without model fine-tuning. Their meta-system essentially automates the process of discovering optimal prompting and iteration strategies for each model family.

The path to surpassing 54% likely involves combining their efficient self-auditing mechanism with richer representations (natural language programs, object-centric reasoning, library learning). The fundamental insight — that evolutionary search over complete solutions with global evaluation outperforms both brute-force sampling and step-by-step reasoning — provides a strong foundation for future work.

ARC-AGI-3, due early 2026, will test interactive reasoning including exploration, planning, memory, and goal acquisition. The current approaches, including Poetiq's, are optimized for static puzzle solving and may require significant architectural changes to succeed on the new benchmark.