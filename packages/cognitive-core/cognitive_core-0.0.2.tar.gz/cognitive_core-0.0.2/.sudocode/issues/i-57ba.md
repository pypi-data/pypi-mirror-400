---
id: i-57ba
title: Implement AbstractionExtractor with Pattern Extractors
priority: 1
created_at: '2026-01-08 07:49:25'
tags:
  - extractor
  - patterns
  - phase-6
relationships:
  - from_id: i-57ba
    from_uuid: 97d0ed81-11c8-46d3-9aeb-87088a3be3b5
    from_type: issue
    to_id: i-73dj
    to_uuid: 6305bbdd-5bf5-4c90-9008-aeebeb6429af
    to_type: issue
    relationship_type: blocks
    created_at: '2026-01-08 07:49:56'
    metadata: null
  - from_id: i-57ba
    from_uuid: 97d0ed81-11c8-46d3-9aeb-87088a3be3b5
    from_type: issue
    to_id: s-7jda
    to_uuid: 49803afb-f589-4d66-94ea-aeb7367a3801
    to_type: spec
    relationship_type: implements
    created_at: '2026-01-08 07:49:43'
    metadata: null
status: closed
closed_at: '2026-01-08 08:02:50'
---
# AbstractionExtractor Implementation

Implements [[s-7jda|Phase 6: Learning Pipeline]] abstraction extraction requirements.

## Goal

Implement AbstractionExtractor with LLM and text-based pattern extractors.

## Requirements

### 1. PatternExtractor Protocol

```python
class PatternExtractor(Protocol):
    """Protocol for code pattern extraction."""
    
    def extract(self, trajectories: list[Trajectory]) -> list[CodeConcept]:
        """Extract code patterns from trajectories."""
        ...
```

### 2. LLMPatternExtractor

```python
class LLMPatternExtractor:
    """LLM identifies conceptual patterns.
    
    Uses LLM to analyze successful trajectories and identify
    reusable code patterns and abstractions.
    """
    
    def __init__(self, llm: SimpleLLM | None = None):
        self._llm = llm
    
    def extract(self, trajectories: list[Trajectory]) -> list[CodeConcept]:
        successful = [t for t in trajectories if t.outcome.success]
        
        # Group by domain for focused extraction
        by_domain = group_by(successful, lambda t: t.task.domain)
        
        concepts = []
        for domain, trajs in by_domain.items():
            prompt = f'''
            Analyze these successful trajectories for {domain} tasks.
            Identify reusable code patterns.
            
            Trajectories:
            {format_trajectories(trajs)}
            
            Return JSON array of patterns:
            [{{"name": "pattern_name", "description": "...", 
              "code": "...", "signature": "...", "examples": [...]}}]
            '''
            ...
        return concepts
```

### 3. TextPatternExtractor

```python
class TextPatternExtractor:
    """AST-based syntactic pattern matching.
    
    Uses text/AST analysis to find common code structures.
    """
    
    def extract(self, trajectories: list[Trajectory]) -> list[CodeConcept]:
        # Extract code from trajectories
        code_samples = [extract_code(t) for t in trajectories if t.outcome.success]
        
        # Find common patterns via:
        # 1. Frequency analysis of function/method calls
        # 2. Common import patterns
        # 3. Similar control flow structures
        
        # Use AST parsing for Python code
        patterns = self._find_common_ast_patterns(code_samples)
        
        return [self._to_concept(p) for p in patterns]
```

### 4. AbstractionExtractor

```python
class AbstractionExtractor:
    """Extract reusable patterns from trajectories.
    
    Example:
        extractor = AbstractionExtractor(
            pattern_extractor=LLMPatternExtractor(llm),
            llm=llm,
        )
        concepts = extractor.extract_code_patterns(trajectories)
        strategies = extractor.extract_strategies(trajectories)
    """
    
    def __init__(
        self,
        pattern_extractor: PatternExtractor | None = None,
        llm: SimpleLLM | None = None,
    ):
        self._pattern_extractor = pattern_extractor or TextPatternExtractor()
        self._llm = llm
    
    def extract_code_patterns(
        self, 
        trajectories: list[Trajectory],
    ) -> list[CodeConcept]:
        """Extract code patterns via configured extractor."""
        return self._pattern_extractor.extract(trajectories)
    
    def extract_strategies(
        self, 
        trajectories: list[Trajectory],
    ) -> list[Strategy]:
        """ArcMemo-style strategy extraction.
        
        For each abstractable trajectory:
        1. Abstract task description → situation
        2. Abstract solution approach → suggestion
        3. Extract typed parameters
        """
        strategies = []
        for traj in trajectories:
            if traj.outcome.success and self.is_abstractable(traj):
                strategy = self._extract_strategy(traj)
                if strategy:
                    strategies.append(strategy)
        return strategies
    
    def is_abstractable(self, trajectory: Trajectory) -> bool:
        """LLM assessment of whether trajectory is worth extracting.
        
        Evaluates:
        - Novelty (is this a new pattern?)
        - Generalizability (will this help other tasks?)
        - Complexity (is it worth abstracting?)
        """
        if self._llm is None:
            # Fallback heuristic
            return trajectory.outcome.success and len(trajectory.steps) >= 3
        
        prompt = f'''
        Assess if this trajectory is worth extracting as a reusable pattern:
        
        Task: {trajectory.task.description}
        Steps: {len(trajectory.steps)}
        Outcome: {"Success" if trajectory.outcome.success else "Failure"}
        
        Consider:
        1. Novelty - Is this a new/unique approach?
        2. Generalizability - Could this help solve similar tasks?
        3. Complexity - Is it substantial enough to abstract?
        
        Return JSON: {{"abstractable": true/false, "reasoning": "..."}}
        '''
        ...
    
    def auto_document(self, concept: CodeConcept) -> CodeConcept:
        """LILO-style documentation generation."""
        prompt = f'''
        Generate documentation for this code pattern:
        
        Code: {concept.code}
        Examples: {concept.examples}
        
        Return JSON:
        {{"name": "snake_case_name", "description": "one sentence", 
          "signature": "type signature"}}
        '''
        ...
```

## Files

- `src/atlas/learning/extractor.py` - AbstractionExtractor + extractors
- `tests/unit/test_extractor.py` - Comprehensive tests

## Tests

- LLMPatternExtractor extracts concepts (mock LLM)
- TextPatternExtractor finds common patterns
- extract_strategies creates valid Strategy objects
- is_abstractable LLM assessment works
- auto_document generates good names
