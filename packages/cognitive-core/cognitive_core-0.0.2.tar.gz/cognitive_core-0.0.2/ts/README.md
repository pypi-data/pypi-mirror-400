# cognitive-core

TypeScript client for [Cognitive Core](https://github.com/alexngai/meta-learning-engine) - A meta-learning framework for learning from agent trajectories.

## Installation

```bash
npm install cognitive-core
```

**Prerequisites:** Python 3.10+

## Setup

The package can automatically set up a Python virtual environment and install dependencies:

```typescript
import { setup, CognitiveCore } from "cognitive-core";

// One-time setup (creates .cognitive-core/ venv)
const { pythonPath, version } = await setup();
console.log(`Installed cognitive-core ${version}`);

// CognitiveCore automatically uses the venv
const core = new CognitiveCore();
await core.start();
```

### Setup Options

```typescript
await setup({
  // Custom venv location (default: ".cognitive-core")
  venvDir: "./my-venv",

  // Install optional features
  extras: ["arc", "embeddings", "llm"],

  // Specific version
  version: "0.1.0",

  // Quiet mode
  verbose: false,
});
```

### Manual Installation

If you prefer to manage Python yourself:

```bash
pip install cognitive-core
```

Then use the system Python:

```typescript
const core = new CognitiveCore({ pythonPath: "python3" });
```

## Quick Start

```typescript
import { CognitiveCore } from "cognitive-core";

const core = new CognitiveCore();

// Start the Python subprocess
await core.start();

// Get version
const version = await core.version();
console.log(`Running cognitive-core v${version}`);

// Create an environment
const env = await core.env.create("arc");

// Reset with a task
const { observation } = await core.env.reset(env.envId, {
  id: "task-1",
  domain: "arc",
  description: "Transform the input grid",
  context: {
    grids: {
      train: [
        [[[0, 1], [1, 0]], [[1, 0], [0, 1]]],
      ],
      test: [
        [[[0, 0], [1, 1]], [[1, 1], [0, 0]]],
      ],
    },
  },
});

// Verify a solution
const outcome = await core.env.verify(env.envId, [[1, 1], [0, 0]]);
console.log(`Success: ${outcome.success}, Score: ${outcome.partialScore}`);

// Stop the subprocess
await core.stop();
```

## API

### CognitiveCore

Main client class.

```typescript
const core = new CognitiveCore(options?: CognitiveCoreOptions);
```

**Options:**
- `pythonPath`: Path to Python executable (default: `"python"`)
- `cwd`: Working directory for Python process
- `env`: Environment variables for Python process
- `timeout`: Command timeout in milliseconds (default: `30000`)

**Methods:**
- `start()`: Start the Python subprocess
- `stop()`: Stop the Python subprocess
- `version()`: Get Python package version
- `isRunning`: Check if client is running

### Environment API (`core.env`)

- `create(domain)`: Create a new environment
- `reset(envId, task)`: Reset environment with a task
- `step(envId, action)`: Execute an action
- `verify(envId, solution)`: Verify a solution

### Memory API (`core.memory`)

- `searchExperiences(query, k)`: Search for similar experiences
- `searchStrategies(query, k)`: Search for relevant strategies
- `searchConcepts(query, k)`: Search for code concepts
- `store(trajectory)`: Store a trajectory

### Search API (`core.search`)

- `solve(task)`: Solve a task using configured search strategy

## Low-Level Client

For advanced usage, access the raw subprocess client:

```typescript
import { CognitiveCoreClient } from "cognitive-core";

const client = new CognitiveCoreClient();
await client.start();

// Execute arbitrary commands
const result = await client.execute("custom.command", { arg: "value" });

await client.stop();
```

## Types

Full TypeScript types are included for all data structures:

```typescript
import type {
  Task,
  Trajectory,
  Outcome,
  Experience,
  Strategy,
  CodeConcept,
  Grid,
  ARCTask,
} from "cognitive-core";
```

## License

MIT
