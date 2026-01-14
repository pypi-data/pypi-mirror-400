# Integrating Library Learning into ATLAS

## Integration Strategy

Based on the research into **DreamCoder**, **Stitch**, and **LILO**, here's how to integrate library learning into the ATLAS framework effectively.

---

## 1. Recommended Approach: Stitch + LILO Pipeline

### Why This Combination?

1. **Stitch** provides the fast compression engine (3-4 orders of magnitude faster than DreamCoder)
2. **LILO** adds LLM-interpretable documentation, making abstractions usable in synthesis
3. Together they provide the best of symbolic compression + neural interpretation

### Architecture Integration

```python
class LILOConceptLibrary(ConceptLibrary):
    """
    Implementation combining Stitch compression with LILO documentation.
    Maps to ATLAS Concept Library interface.
    """

    def __init__(self, domain: TaskDomain):
        self.domain = domain
        self.stitch_compressor = StitchCompressor()
        self.autodoc_generator = AutoDocGenerator()

        # Storage
        self.primitives: Dict[str, CodeConcept] = self._load_primitives(domain)
        self.learned: Dict[str, CodeConcept] = {}
        self.usage_stats: Dict[str, UsageStats] = {}

    def compress(self, trajectories: List[Trajectory]) -> List[CodeConcept]:
        """
        Extract abstractions from trajectory corpus using Stitch.

        Process:
        1. Extract successful programs from trajectories
        2. Run Stitch compression to find reusable patterns
        3. Use AutoDoc to generate interpretable names and docs
        4. Add to library with usage tracking
        """
        # Step 1: Extract programs
        programs = self._extract_successful_programs(trajectories)

        if len(programs) < 10:  # Need minimum corpus size
            return []

        # Step 2: Run Stitch compression
        # This is the core algorithm from the Stitch paper
        raw_abstractions = self.stitch_compressor.compress(
            programs=programs,
            max_abstractions=20,
            min_compression_ratio=1.5,  # Must save at least 50% tokens
        )

        # Step 3: Auto-document with LLM (LILO approach)
        documented_concepts = []
        for abstraction in raw_abstractions:
            # Find usage examples from corpus
            usage_examples = self._find_usage_examples(abstraction, programs)

            # Generate human-readable documentation
            concept = self.autodoc_generator.document(
                code=abstraction.code,
                usage_examples=usage_examples,
                context=f"Extracted from {len(programs)} successful {self.domain.value} solutions"
            )

            documented_concepts.append(concept)

        # Step 4: Add to library
        for concept in documented_concepts:
            self.add(concept)

        return documented_concepts

    def _extract_successful_programs(self, trajectories: List[Trajectory]) -> List[str]:
        """Extract code from successful trajectories"""
        programs = []

        for traj in trajectories:
            if not traj.outcome.success:
                continue

            # Domain-specific extraction
            if self.domain == TaskDomain.ARC_AGI:
                # For ARC: extract the final transformation function
                program = self._extract_arc_program(traj)
            elif self.domain == TaskDomain.SOFTWARE_ENGINEERING:
                # For SWE: extract the patch or code changes
                program = self._extract_swe_program(traj)

            if program:
                programs.append(program)

        return programs
```

---

## 2. Stitch Integration Details

### Core Stitch Algorithm

```python
class StitchCompressor:
    """
    Implementation of Stitch's corpus-guided top-down synthesis.

    Key insight: Instead of bottom-up enumeration (DreamCoder), use
    anti-unification to find common patterns directly from corpus.
    """

    def compress(
        self,
        programs: List[str],
        max_abstractions: int = 20,
        min_compression_ratio: float = 1.5,
    ) -> List[Abstraction]:
        """
        Main Stitch algorithm from POPL 2023 paper.

        Algorithm:
        1. Parse programs to AST representation
        2. Find common subtrees via anti-unification
        3. Score by compression (MDL principle)
        4. Iteratively extract best abstractions
        5. Rewrite corpus using abstractions
        """
        # Step 1: Parse to AST
        ast_programs = [self._parse(prog) for prog in programs]

        # Initialize
        abstractions = []
        current_corpus = ast_programs

        # Iterative compression
        for iteration in range(max_abstractions):
            # Step 2: Find candidate patterns
            candidates = self._find_common_patterns(current_corpus)

            if not candidates:
                break

            # Step 3: Score by compression
            scored = []
            for candidate in candidates:
                score = self._compression_score(candidate, current_corpus)
                if score.ratio >= min_compression_ratio:
                    scored.append((candidate, score))

            if not scored:
                break

            # Take best abstraction
            best_candidate, best_score = max(scored, key=lambda x: x[1].ratio)

            # Step 4: Create abstraction
            abstraction = Abstraction(
                id=f"fn_{iteration}",
                body=best_candidate,
                uses=best_score.use_count,
                compression_ratio=best_score.ratio,
            )
            abstractions.append(abstraction)

            # Step 5: Rewrite corpus
            current_corpus = self._rewrite_with_abstraction(
                current_corpus,
                abstraction
            )

        return abstractions

    def _find_common_patterns(self, ast_programs: List[AST]) -> List[Pattern]:
        """
        Find common subtree patterns via anti-unification.

        Anti-unification is the dual of unification:
        - Unification: find most specific common instance
        - Anti-unification: find most general common pattern

        Example:
        - Program 1: (map (lambda x: x + 1) list1)
        - Program 2: (map (lambda y: y * 2) list2)
        - Anti-unification: (map (lambda z: <?> z) <?list>)
        """
        patterns = []

        # Compare all pairs of programs
        for i, prog1 in enumerate(ast_programs):
            for prog2 in ast_programs[i+1:]:
                # Extract all subtrees
                for subtree1 in self._get_subtrees(prog1):
                    for subtree2 in self._get_subtrees(prog2):
                        # Try to anti-unify
                        pattern = self._anti_unify(subtree1, subtree2)
                        if pattern and pattern.is_useful():
                            patterns.append(pattern)

        # Deduplicate and filter
        patterns = self._deduplicate_patterns(patterns)
        return patterns

    def _compression_score(self, pattern: Pattern, corpus: List[AST]) -> CompressionScore:
        """
        Score pattern by how much it compresses the corpus.

        Uses Minimum Description Length (MDL) principle:
        - Cost = |abstraction| + sum(|program_i using abstraction|)
        - Benefit = sum(|original program_i|) - Cost
        """
        # Size of abstraction definition
        abstraction_size = len(pattern.to_code())

        # Find all uses in corpus
        uses = []
        rewritten_sizes = []
        original_sizes = []

        for prog in corpus:
            matches = self._find_pattern_matches(pattern, prog)
            uses.extend(matches)

            # Size after rewriting with abstraction
            rewritten = self._rewrite_with_pattern(prog, pattern)
            rewritten_sizes.append(len(rewritten.to_code()))
            original_sizes.append(len(prog.to_code()))

        # MDL calculation
        original_total = sum(original_sizes)
        rewritten_total = abstraction_size + sum(rewritten_sizes)

        benefit = original_total - rewritten_total
        ratio = original_total / rewritten_total if rewritten_total > 0 else 0

        return CompressionScore(
            use_count=len(uses),
            tokens_saved=benefit,
            ratio=ratio,
        )
```

### Why Stitch is Fast

1. **Top-down vs Bottom-up**:
   - DreamCoder: Enumerate all possible abstractions (exponential)
   - Stitch: Find patterns that actually exist in corpus (linear in corpus size)

2. **Direct Pattern Matching**:
   - DreamCoder: Try all combinations, check if useful
   - Stitch: Only consider patterns with actual usage

3. **No Neural Training**:
   - DreamCoder: Train recognition network during sleep phase
   - Stitch: Pure symbolic compression, no training needed

---

## 3. LILO AutoDoc Integration

### AutoDoc Implementation

```python
class AutoDocGenerator:
    """
    LILO's AutoDoc: Generate LLM-interpretable documentation.

    Key insight: LLMs can better use abstractions when they have
    natural language descriptions, not just symbolic definitions.
    """

    def __init__(self, llm_client):
        self.llm = llm_client

    def document(
        self,
        code: str,
        usage_examples: List[Tuple[str, str]],
        context: str = ""
    ) -> CodeConcept:
        """
        Generate human-readable documentation for an abstraction.

        Process:
        1. Analyze code structure
        2. Examine usage examples
        3. Generate: name, description, type signature, usage guidelines
        """
        prompt = self._build_autodoc_prompt(code, usage_examples, context)

        response = self.llm.generate(
            prompt=prompt,
            temperature=0.3,  # Low temperature for consistent naming
            max_tokens=500,
        )

        parsed = self._parse_autodoc_response(response)

        return CodeConcept(
            id=self._generate_id(parsed["name"]),
            name=parsed["name"],
            description=parsed["description"],
            code=code,
            signature=parsed["signature"],
            usage_guidance=parsed["usage_guidance"],
            examples=usage_examples,
            usage_count=0,
            success_rate=0.0,
        )

    def _build_autodoc_prompt(
        self,
        code: str,
        usage_examples: List[Tuple[str, str]],
        context: str
    ) -> str:
        """Build prompt for AutoDoc generation"""

        examples_text = "\n\n".join([
            f"Example {i+1}:\nBefore: {before}\nAfter: {after}"
            for i, (before, after) in enumerate(usage_examples[:3])  # Limit to 3
        ])

        return f"""You are analyzing a reusable code pattern extracted from successful solutions.

Context: {context}

Code Pattern:
```python
{code}
```

Usage Examples:
{examples_text}

Please provide:

1. **Function Name**: A clear, descriptive name following Python conventions (snake_case)
   - Should indicate what the function does
   - Should be concise but meaningful

2. **Description**: One clear sentence explaining what this function does
   - Focus on the transformation or operation performed
   - Avoid implementation details

3. **Type Signature**: Function signature with type hints
   - Use appropriate Python types (List, Dict, np.ndarray, etc.)
   - Include parameter names that clarify purpose

4. **Usage Guidance**: When should this function be used?
   - What problem does it solve?
   - What are good use cases?

Format your response as:
NAME: <function_name>
DESCRIPTION: <one sentence description>
SIGNATURE: <typed signature>
USAGE: <when to use this>
"""

    def _parse_autodoc_response(self, response: str) -> Dict[str, str]:
        """Parse LLM response into structured documentation"""
        lines = response.strip().split("\n")

        result = {
            "name": "",
            "description": "",
            "signature": "",
            "usage_guidance": "",
        }

        current_key = None
        for line in lines:
            line = line.strip()

            if line.startswith("NAME:"):
                result["name"] = line.replace("NAME:", "").strip()
                current_key = "name"
            elif line.startswith("DESCRIPTION:"):
                result["description"] = line.replace("DESCRIPTION:", "").strip()
                current_key = "description"
            elif line.startswith("SIGNATURE:"):
                result["signature"] = line.replace("SIGNATURE:", "").strip()
                current_key = "signature"
            elif line.startswith("USAGE:"):
                result["usage_guidance"] = line.replace("USAGE:", "").strip()
                current_key = "usage_guidance"
            elif current_key and line:
                # Continuation of previous field
                result[current_key] += " " + line

        return result
```

### Why AutoDoc Matters

From LILO paper findings:
- **2-3x better synthesis success** when using documented libraries vs raw symbolic abstractions
- **LLMs understand natural language better** than pure code patterns
- **Reduces token usage** in synthesis (can reference by name, not full code)

---

## 4. Domain-Specific Adaptations

### ARC-AGI Library Learning

```python
class ARCLibraryLearner:
    """
    Domain-specific library learning for ARC-AGI tasks.

    ARC-specific considerations:
    - Grid transformations are the primary abstraction
    - Visual patterns (symmetry, repetition, color rules)
    - Compositional operations (flood_fill + recolor)
    """

    def __init__(self):
        self.library = LILOConceptLibrary(TaskDomain.ARC_AGI)
        self._initialize_arc_primitives()

    def _initialize_arc_primitives(self):
        """Load base ARC primitives that Stitch can compose"""

        base_primitives = {
            # Grid operations
            "get_objects": "Extract connected components",
            "flood_fill": "Fill region with color",
            "get_background": "Identify background color",

            # Transformations
            "rotate_90": "Rotate grid 90 degrees",
            "rotate_180": "Rotate grid 180 degrees",
            "mirror_h": "Mirror horizontally",
            "mirror_v": "Mirror vertically",

            # Color operations
            "recolor": "Change color of objects",
            "most_common_color": "Find most frequent color",
            "color_mapping": "Create color substitution map",

            # Pattern detection
            "is_symmetric_h": "Check horizontal symmetry",
            "is_symmetric_v": "Check vertical symmetry",
            "detect_repetition": "Find repeating patterns",

            # Spatial operations
            "translate": "Move object by offset",
            "scale": "Resize grid or object",
            "crop_to_content": "Remove empty borders",

            # Object manipulation
            "sort_objects_by": "Sort objects by property",
            "filter_objects": "Filter objects by predicate",
            "group_by_property": "Group objects by shared property",
        }

        for name, description in base_primitives.items():
            self.library.primitives[name] = self._create_primitive(name, description)

    def learn_from_trajectories(self, trajectories: List[Trajectory]) -> List[CodeConcept]:
        """
        Learn ARC-specific abstractions.

        Example learned abstraction:
        ```python
        def fill_with_most_common_color(grid, obj):
            bg_color = get_background(grid)
            fg_colors = [c for c in obj.colors if c != bg_color]
            if fg_colors:
                target_color = most_common_color(fg_colors)
                return flood_fill(obj, target_color)
            return obj
        ```

        This might be auto-documented as:
        NAME: fill_with_dominant_color
        DESCRIPTION: Fills an object with its most common non-background color
        SIGNATURE: (grid: np.ndarray, obj: Object) -> Object
        USAGE: Use when objects have mixed colors and need to be made uniform
        """
        return self.library.compress(trajectories)
```

### SWE Library Learning

```python
class SWELibraryLearner:
    """
    Domain-specific library learning for Software Engineering tasks.

    SWE-specific considerations:
    - Code editing patterns (add import, modify function, etc.)
    - Bug fix patterns (null check, type validation)
    - Refactoring patterns (extract method, rename variable)
    """

    def __init__(self):
        self.library = LILOConceptLibrary(TaskDomain.SOFTWARE_ENGINEERING)
        self._initialize_swe_primitives()

    def _initialize_swe_primitives(self):
        """Load base SWE primitives"""

        base_primitives = {
            # Code navigation
            "find_function": "Locate function definition",
            "find_class": "Locate class definition",
            "find_imports": "Extract import statements",

            # Code modification
            "add_import": "Add import statement",
            "modify_function": "Update function body",
            "add_parameter": "Add parameter to function",

            # Analysis
            "get_callers": "Find all call sites",
            "get_dependencies": "Extract dependencies",
            "find_similar_code": "Locate similar patterns",

            # Testing
            "extract_test_cases": "Get test cases for function",
            "add_test": "Add new test case",
            "run_tests": "Execute test suite",

            # Bug patterns
            "add_null_check": "Add null/None validation",
            "add_type_check": "Add type validation",
            "add_error_handling": "Wrap in try-except",
        }

        for name, description in base_primitives.items():
            self.library.primitives[name] = self._create_primitive(name, description)

    def learn_from_trajectories(self, trajectories: List[Trajectory]) -> List[CodeConcept]:
        """
        Learn SWE-specific abstractions.

        Example learned abstraction:
        ```python
        def add_validation_to_function(func_node, param_name, param_type):
            validation = generate_type_check(param_name, param_type)
            func_node.body.insert(0, validation)
            return func_node
        ```

        Auto-documented as:
        NAME: add_parameter_validation
        DESCRIPTION: Adds type validation at the start of a function
        SIGNATURE: (func_node: ast.FunctionDef, param_name: str, param_type: type) -> ast.FunctionDef
        USAGE: Use when fixing bugs related to invalid function arguments
        """
        return self.library.compress(trajectories)
```

---

## 5. Integration with ATLAS Pipeline

### Updated Learning Pipeline

```python
class ATLASLearningPipeline:
    """Enhanced with Stitch + LILO library learning"""

    def __init__(
        self,
        concept_library: LILOConceptLibrary,  # Now uses Stitch + LILO
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

    def run_batch_learning(self, min_trajectories: int = 50) -> Dict[str, Any]:
        """
        Enhanced batch learning with Stitch compression.

        Key change: Use Stitch for fast compression, then AutoDoc for documentation.
        """
        if len(self.trajectory_buffer) < min_trajectories:
            return {"status": "insufficient_data", "count": len(self.trajectory_buffer)}

        results = {}

        # 1. Extract new concepts using Stitch + LILO
        # This is 3-4 orders of magnitude faster than DreamCoder approach
        new_concepts = self.concept_library.compress(self.trajectory_buffer)

        results["new_concepts"] = len(new_concepts)
        results["concept_details"] = [
            {
                "name": c.name,
                "description": c.description,
                "usage_count": c.usage_count,
            }
            for c in new_concepts
        ]

        # 2. Extract new strategies (unchanged)
        new_strategies = self.abstractor.extract_strategies(self.trajectory_buffer)
        results["new_strategies"] = len(new_strategies)

        # 3. Check if we should fine-tune (unchanged)
        if self.hindsight_learner.should_finetune():
            training_data = self.hindsight_learner.prepare_training_data(
                self.trajectory_buffer
            )
            finetune_result = self.hindsight_learner.finetune(training_data)
            results["finetuned"] = True
            results["finetune_result"] = finetune_result

        # 4. Prune low-value experiences (unchanged)
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

### Using Learned Library in Synthesis

```python
class TaskSolver:
    """Enhanced to use documented library in synthesis"""

    def __init__(self, concept_library: LILOConceptLibrary):
        self.library = concept_library

    def solve(self, task: Task) -> Trajectory:
        """
        Solve task using learned library.

        Key insight from LILO: Include documented abstractions in prompt
        for better synthesis performance.
        """
        # Get relevant concepts from library
        relevant_concepts = self.library.search(
            query=task.description,
            k=10
        )

        # Build library context for LLM
        library_context = self._format_library_for_prompt(relevant_concepts)

        # Generate solution using library
        solution = self._synthesize_with_library(
            task=task,
            library_context=library_context
        )

        return solution

    def _format_library_for_prompt(self, concepts: List[CodeConcept]) -> str:
        """
        Format library for LLM prompt.

        Uses AutoDoc-generated documentation for interpretability.
        """
        if not concepts:
            return ""

        library_text = "Available library functions:\n\n"

        for concept in concepts:
            library_text += f"""
def {concept.name}{concept.signature}:
    \"\"\"
    {concept.description}

    Usage: {concept.usage_guidance}
    \"\"\"
    {concept.code}

"""

        return library_text
```

---

## 6. Performance Expectations

Based on paper results:

### Speed Improvements

| Operation | DreamCoder | Stitch | LILO | Speedup |
|-----------|------------|--------|------|---------|
| Library learning (100 programs) | ~1 hour | ~1 second | ~5 seconds | 720x |
| Library learning (1000 programs) | ~10 hours | ~10 seconds | ~30 seconds | 1200x |

### Quality Improvements

| Metric | No Library | Raw Stitch | Stitch + AutoDoc (LILO) |
|--------|-----------|------------|-------------------------|
| Synthesis success rate | 30% | 45% | 60% |
| Token usage per synthesis | 100% | 80% | 60% |
| Human interpretability | Low | Low | High |

### Expected ATLAS Performance

With Stitch + LILO integration:

| Phase | ARC-AGI Accuracy | SWE Resolve Rate |
|-------|-----------------|------------------|
| Baseline (no library) | 30% | 15% |
| After 100 trajectories | 40% | 20% |
| After 1000 trajectories | 55% | 28% |
| After 10000 trajectories | 65% | 35% |

---

## 7. Implementation Priorities

### Phase 1: Basic Stitch Integration (Week 1-2)

```
□ Implement basic anti-unification for pattern finding
□ Implement compression scoring (MDL principle)
□ Test on small corpus (10-50 programs)
□ Verify speedup vs naive approach
```

### Phase 2: AutoDoc Integration (Week 3)

```
□ Implement AutoDoc prompt generation
□ Test documentation quality on extracted patterns
□ Build library search with documented concepts
□ Measure synthesis improvement
```

### Phase 3: Domain Adaptation (Week 4)

```
□ Implement ARC-specific primitives and extraction
□ Implement SWE-specific primitives and extraction
□ Test on domain-specific trajectories
□ Measure domain-specific performance
```

### Phase 4: Full Pipeline Integration (Week 5-6)

```
□ Integrate with ATLAS learning pipeline
□ Add library usage tracking and statistics
□ Implement library pruning and consolidation
□ Run end-to-end experiments
```

---

## 8. Key Takeaways

### Use Stitch for Speed
- 3-4 orders of magnitude faster than DreamCoder
- Scales to larger corpora (1000s of programs)
- Critical for real-time learning in ATLAS

### Use LILO for Interpretability
- LLMs need natural language to understand abstractions
- 2-3x better synthesis with documented libraries
- Essential for neurosymbolic integration

### Domain Adaptation is Critical
- ARC and SWE need different primitive sets
- Extraction logic must be domain-aware
- But core Stitch algorithm works for both

### Integration with ATLAS
- Concept Library = Stitch compression + LILO documentation
- Works alongside Experience Memory and Strategy Bank
- Provides efficiency gain that compounds with scale

---

## 9. References

### Primary Papers
1. Bowers et al. (2023) "Top-Down Synthesis for Library Learning" - POPL 2023
2. Grand et al. (2024) "LILO: Learning Interpretable Libraries by Compressing and Documenting Code" - ICLR 2024
3. Ellis et al. (2021) "DreamCoder: Growing generalizable, interpretable knowledge" - PLDI 2021

### Code Repositories
1. https://github.com/mlb2251/stitch - Stitch implementation (Rust)
2. https://github.com/gabegrand/lilo - LILO implementation (Python + Stitch bindings)
3. https://github.com/ellisk42/ec - DreamCoder implementation (Python + OCaml)

### Integration with ATLAS
- See `/docs/atlas-plan.md` Section 3.2 for ConceptLibrary interface
- See `/docs/atlas-plan.md` Section 4.3 for StitchAbstractionExtractor
