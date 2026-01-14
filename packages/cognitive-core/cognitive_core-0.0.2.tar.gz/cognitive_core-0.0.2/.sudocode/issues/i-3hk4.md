---
id: i-3hk4
title: Implement full SWEEnvironment with Docker
priority: 1
created_at: '2026-01-08 05:58:45'
tags:
  - docker
  - environment
  - phase-5
  - swe
relationships:
  - from_id: i-3hk4
    from_uuid: 0da9cebf-f62c-424b-a32b-d4064b666a71
    from_type: issue
    to_id: i-9lmj
    to_uuid: 27ed0f7f-d5f3-4e8f-8997-b38ec18de847
    to_type: issue
    relationship_type: blocks
    created_at: '2026-01-08 06:00:47'
    metadata: null
  - from_id: i-3hk4
    from_uuid: 0da9cebf-f62c-424b-a32b-d4064b666a71
    from_type: issue
    to_id: s-6d5x
    to_uuid: 883e1201-e690-4a7d-99ce-20a045f37b4c
    to_type: spec
    relationship_type: implements
    created_at: '2026-01-08 06:00:47'
    metadata: null
status: closed
closed_at: '2026-01-08 06:10:42'
---
# Full SWEEnvironment Implementation

Implements [[s-6d5x|Phase 5: Advanced Search]] SWEEnvironment requirements.

## Goal

Replace the SWEEnvironment stub with full Docker-based evaluation using swebench.

## Requirements

### 1. Dependencies

Add to pyproject.toml:
```toml
swebench = ">=2.0.0"
docker = ">=7.0.0"
```

### 2. SWEEnvironment Class

```python
class SWEEnvironment:
    """SWE-bench environment with Docker evaluation."""
    
    def __init__(
        self,
        docker_client: docker.DockerClient | None = None,
        timeout: int = 300,
        image_namespace: str = "",  # Empty for local builds on ARM
        cleanup: bool = True,
    ):
        self._task: Task | None = None
        self._docker = docker_client or docker.from_env()
        self._timeout = timeout
        self._namespace = image_namespace
        self._cleanup = cleanup
        self._container: docker.Container | None = None
    
    def reset(self, task: Task) -> str:
        """Set up Docker container for SWE-bench task.
        
        Expects task.context to contain:
        - repo: Repository name (e.g., "astropy/astropy")
        - version: Version/commit to test
        - instance_id: SWE-bench instance ID
        """
        # Pull or build appropriate image
        # Start container
        # Return task description
        ...
    
    def step(self, action: str) -> tuple[str, float, bool]:
        """Execute action in container.
        
        Args:
            action: Either a patch (diff format) or shell command
            
        Returns:
            (observation, reward, done)
        """
        # Detect if action is patch or command
        # Apply patch or execute command
        # Return output
        ...
    
    def verify(self, solution: Any) -> Outcome:
        """Run tests and return outcome.
        
        Args:
            solution: Patch string to apply
            
        Returns:
            Outcome with test results and partial score
        """
        # Apply solution patch
        # Run test suite
        # Parse results
        # Calculate partial_score = tests_passed / total_tests
        ...
    
    def cleanup(self) -> None:
        """Clean up Docker container."""
        if self._container and self._cleanup:
            self._container.remove(force=True)
    
    @property
    def task(self) -> Task:
        if self._task is None:
            raise RuntimeError("No task set. Call reset() first.")
        return self._task
```

### 3. Docker Image Management

```python
def _get_or_build_image(self, repo: str, version: str) -> str:
    """Get existing image or build new one.
    
    Uses swebench's image building infrastructure.
    """
    image_name = f"swebench/{repo.replace('/', '__')}:{version}"
    
    try:
        self._docker.images.get(image_name)
        return image_name
    except docker.errors.ImageNotFound:
        # Build using swebench
        ...
```

### 4. Test Execution

```python
def _run_tests(self, test_cmd: str | None = None) -> dict:
    """Run tests in container and parse results.
    
    Returns:
        {
            "passed": int,
            "failed": int, 
            "total": int,
            "output": str,
        }
    """
    ...
```

### 5. InteractiveEnvironment Support

SWEEnvironment should implement the full InteractiveEnvironment protocol:
- `step()` for interactive exploration
- State tracking for multi-step edits
- Rollback support

## Files

- `src/atlas/environments/swe.py` - Full implementation
- `tests/unit/test_swe_environment.py` - Unit tests with mocked Docker
- `tests/integration/test_swe_environment.py` - Integration tests (requires Docker)

## Tests

- Container lifecycle (create, execute, cleanup)
- Patch application
- Test execution and parsing
- Partial scoring calculation
- Timeout handling
- Error recovery

## Notes

- Tests requiring Docker should be marked with `@pytest.mark.docker`
- Consider using Epoch AI's optimized images for faster setup
- ARM (M-series Mac) users need `--namespace ''` for local builds
