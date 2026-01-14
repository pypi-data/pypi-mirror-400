---
id: i-73dj
title: Implement LearningPipeline Orchestrator
priority: 2
created_at: '2026-01-08 07:49:26'
tags:
  - orchestration
  - phase-6
  - pipeline
status: open
---
# LearningPipeline Implementation

Implements [[s-7jda|Phase 6: Learning Pipeline]] orchestration requirements.

## Goal

Implement LearningPipeline to orchestrate the full learning process.

## Requirements

### 1. LearningPipeline Class

```python
class LearningPipeline:
    """Orchestrates the full learning process.
    
    Coordinates TrajectoryAnalyzer, AbstractionExtractor, and
    HindsightLearner to process trajectories and improve memory.
    
    Example:
        pipeline = LearningPipeline(
            memory=memory_system,
            analyzer=TrajectoryAnalyzer(),
            extractor=AbstractionExtractor(),
            hindsight=HindsightLearner(),
        )
        
        # Process single trajectory
        result = pipeline.process_trajectory(trajectory)
        
        # Run batch learning when ready
        if pipeline.should_run_batch():
            batch_result = pipeline.run_batch_learning()
    """
    
    def __init__(
        self,
        memory: MemorySystem,
        analyzer: TrajectoryAnalyzer | None = None,
        extractor: AbstractionExtractor | None = None,
        hindsight: HindsightLearner | None = None,
        config: LearningConfig | None = None,
    ):
        self._memory = memory
        self._config = config or LearningConfig()
        self._analyzer = analyzer or TrajectoryAnalyzer()
        self._extractor = extractor or AbstractionExtractor()
        self._hindsight = hindsight or HindsightLearner(
            memory=memory, config=self._config
        )
    
    def process_trajectory(self, trajectory: Trajectory) -> ProcessResult:
        """Process a single trajectory through the learning pipeline.
        
        Flow:
        1. Store in experience memory
        2. Analyze (credit assignment, error detection)
        3. Check abstractability
        4. Extract strategy if abstractable
        5. Accumulate for batch learning
        
        Args:
            trajectory: The trajectory to process.
            
        Returns:
            ProcessResult with processing details.
        """
        # 1. Store in memory
        stored = False
        if self._memory.experience_memory is not None:
            self._memory.experience_memory.store(trajectory)
            stored = True
        
        # 2. Analyze
        analysis = self._analyzer.analyze(trajectory)
        
        # 3. Check abstractability
        abstractable = self._extractor.is_abstractable(trajectory)
        
        # 4. Extract strategy if abstractable and successful
        strategy_extracted = False
        if abstractable and trajectory.outcome.success:
            strategies = self._extractor.extract_strategies([trajectory])
            if strategies and self._memory.strategy_bank is not None:
                for strategy in strategies:
                    self._memory.strategy_bank.write(strategy)
                strategy_extracted = True
        
        # 5. Accumulate for batch
        self._hindsight.accumulate(trajectory)
        
        return ProcessResult(
            trajectory_id=trajectory.task.id,
            stored=stored,
            analysis=analysis,
            abstractable=abstractable,
            strategy_extracted=strategy_extracted,
        )
    
    def should_run_batch(self) -> bool:
        """Check if batch learning should run."""
        return self._hindsight.should_run_batch()
    
    def run_batch_learning(
        self,
        min_trajectories: int | None = None,
    ) -> BatchResult:
        """Run batch learning on accumulated trajectories.
        
        Flow:
        1. Get accumulated trajectories
        2. Extract code patterns
        3. Add concepts to library
        4. Optionally prune low-value experiences
        5. Clear accumulator
        
        Args:
            min_trajectories: Override config minimum.
            
        Returns:
            BatchResult with learning outcomes.
        """
        trajectories = self._hindsight.get_accumulated()
        min_count = min_trajectories or self._config.min_trajectories
        
        if len(trajectories) < min_count:
            return BatchResult(
                trajectories_processed=0,
                concepts_extracted=0,
                strategies_extracted=0,
                experiences_pruned=0,
                success_rate=0.0,
            )
        
        # Calculate success rate
        success_count = sum(1 for t in trajectories if t.outcome.success)
        success_rate = success_count / len(trajectories) if trajectories else 0.0
        
        # Extract code patterns
        concepts = self._extractor.extract_code_patterns(trajectories)
        concepts_added = 0
        if self._memory.concept_library is not None:
            for concept in concepts:
                documented = self._extractor.auto_document(concept)
                self._memory.concept_library.add(documented)
                concepts_added += 1
        
        # Extract additional strategies from batch
        strategies = self._extractor.extract_strategies(trajectories)
        strategies_added = 0
        if self._memory.strategy_bank is not None:
            for strategy in strategies:
                self._memory.strategy_bank.write(strategy)
                strategies_added += 1
        
        # Prune low-value experiences
        pruned = 0
        if self._memory.experience_memory is not None:
            pruned = self._memory.experience_memory.prune({
                "min_success_rate": 0.1,  # Remove consistently failing
                "keep_diverse": True,
            })
        
        # Clear accumulator
        self._hindsight.clear_accumulated()
        
        return BatchResult(
            trajectories_processed=len(trajectories),
            concepts_extracted=concepts_added,
            strategies_extracted=strategies_added,
            experiences_pruned=pruned,
            success_rate=success_rate,
        )
    
    @property
    def accumulated_count(self) -> int:
        """Number of trajectories waiting for batch processing."""
        return self._hindsight.accumulated_count
```

### 2. Factory Function

```python
def create_learning_pipeline(
    memory: MemorySystem,
    llm: SimpleLLM | None = None,
    config: LearningConfig | None = None,
) -> LearningPipeline:
    """Create a configured learning pipeline.
    
    Args:
        memory: Memory system for storage.
        llm: Optional LLM for intelligent analysis.
        config: Optional configuration.
        
    Returns:
        Configured LearningPipeline.
    """
    config = config or LearningConfig()
    
    # Create credit strategy based on config
    if config.credit_strategy == "llm":
        credit_strategy = LLMCreditStrategy(llm)
    elif config.credit_strategy == "counterfactual":
        credit_strategy = CounterfactualCreditStrategy(llm)
    else:
        credit_strategy = SimpleCreditStrategy()
    
    # Create pattern extractor based on config
    if config.pattern_extractor == "llm":
        pattern_extractor = LLMPatternExtractor(llm)
    elif config.pattern_extractor == "text":
        pattern_extractor = TextPatternExtractor()
    else:  # "both"
        pattern_extractor = CombinedPatternExtractor(llm)
    
    return LearningPipeline(
        memory=memory,
        analyzer=TrajectoryAnalyzer(strategy=credit_strategy, llm=llm),
        extractor=AbstractionExtractor(pattern_extractor=pattern_extractor, llm=llm),
        hindsight=HindsightLearner(memory=memory, config=config),
        config=config,
    )
```

## Files

- `src/atlas/learning/pipeline.py` - LearningPipeline + factory
- `src/atlas/learning/__init__.py` - Exports
- `tests/unit/test_pipeline.py` - Comprehensive tests

## Tests

- process_trajectory stores and analyzes
- process_trajectory extracts strategy when abstractable
- should_run_batch respects triggers
- run_batch_learning extracts patterns
- run_batch_learning adds concepts to library
- run_batch_learning prunes experiences
- Factory creates correct components based on config
