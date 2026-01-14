/**
 * Cognitive Core - TypeScript client for the meta-learning framework.
 *
 * This package provides a TypeScript API for interacting with the Python
 * cognitive-core package via subprocess communication.
 *
 * @example
 * ```typescript
 * import { CognitiveCore } from "cognitive-core";
 *
 * const core = new CognitiveCore();
 * await core.start();
 *
 * // Create an environment
 * const env = await core.env.create("arc");
 *
 * // Reset with a task
 * const observation = await core.env.reset(env.envId, {
 *   id: "task-1",
 *   domain: "arc",
 *   description: "Solve this puzzle",
 *   context: { grids: { train: [...], test: [...] } },
 * });
 *
 * // Verify a solution
 * const outcome = await core.env.verify(env.envId, solution);
 *
 * await core.stop();
 * ```
 *
 * @packageDocumentation
 */

import { CognitiveCoreClient } from "./client.js";
import { setup, isSetUp, getPythonPath } from "./setup.js";
import type {
  Task,
  Outcome,
  StepResult,
  CognitiveCoreOptions,
  Experience,
  Strategy,
  CodeConcept,
} from "./types.js";

// Re-export types
export * from "./types.js";
export { CognitiveCoreClient } from "./client.js";
export { setup, isSetUp, getPythonPath } from "./setup.js";
export type { SetupOptions, SetupResult } from "./setup.js";

/**
 * Environment operations
 */
class EnvironmentAPI {
  constructor(private client: CognitiveCoreClient) {}

  /**
   * Create a new environment.
   */
  async create(domain: string = "passthrough"): Promise<{ envId: string; domain: string }> {
    const result = await this.client.execute<{ env_id: string; domain: string }>(
      "env.create",
      { domain }
    );
    return { envId: result.env_id, domain: result.domain };
  }

  /**
   * Reset an environment with a task.
   */
  async reset(envId: string, task: Partial<Task>): Promise<{ envId: string; observation: string }> {
    const result = await this.client.execute<{ env_id: string; observation: string }>(
      "env.reset",
      { env_id: envId, task }
    );
    return { envId: result.env_id, observation: result.observation };
  }

  /**
   * Execute an action in the environment.
   */
  async step(envId: string, action: string): Promise<StepResult> {
    return this.client.execute("env.step", { env_id: envId, action });
  }

  /**
   * Verify a solution.
   */
  async verify(envId: string, solution: unknown): Promise<Outcome> {
    const result = await this.client.execute<{
      success: boolean;
      partial_score: number;
      details: Record<string, unknown>;
    }>("env.verify", { env_id: envId, solution });

    return {
      success: result.success,
      partialScore: result.partial_score,
      verificationDetails: result.details,
    };
  }
}

/**
 * Memory operations
 */
class MemoryAPI {
  constructor(private client: CognitiveCoreClient) {}

  /**
   * Search for similar experiences.
   */
  async searchExperiences(query: string, k: number = 5): Promise<Experience[]> {
    const result = await this.client.execute<{ experiences: Experience[] }>(
      "memory.search",
      { query, k, type: "experience" }
    );
    return result.experiences ?? [];
  }

  /**
   * Search for relevant strategies.
   */
  async searchStrategies(query: string, k: number = 5): Promise<Strategy[]> {
    const result = await this.client.execute<{ strategies: Strategy[] }>(
      "memory.search",
      { query, k, type: "strategy" }
    );
    return result.strategies ?? [];
  }

  /**
   * Search for relevant concepts.
   */
  async searchConcepts(query: string, k: number = 5): Promise<CodeConcept[]> {
    const result = await this.client.execute<{ concepts: CodeConcept[] }>(
      "memory.search",
      { query, k, type: "concept" }
    );
    return result.concepts ?? [];
  }

  /**
   * Store a trajectory in memory.
   */
  async store(trajectory: unknown): Promise<{ id: string }> {
    return this.client.execute("memory.store", { trajectory });
  }
}

/**
 * Search operations
 */
class SearchAPI {
  constructor(private client: CognitiveCoreClient) {}

  /**
   * Solve a task using the configured search strategy.
   */
  async solve(task: Partial<Task>): Promise<{ trajectory: unknown; outcome: Outcome }> {
    return this.client.execute("search.solve", { task });
  }
}

/**
 * Main Cognitive Core client with high-level API.
 *
 * @example
 * ```typescript
 * // Quick start (uses system Python or auto-detects venv)
 * const core = new CognitiveCore();
 * await core.start();
 *
 * // With explicit setup first
 * import { setup, CognitiveCore } from "cognitive-core";
 * const { pythonPath } = await setup();
 * const core = new CognitiveCore({ pythonPath });
 * await core.start();
 * ```
 */
export class CognitiveCore {
  private client: CognitiveCoreClient;

  /**
   * Environment operations (create, reset, step, verify)
   */
  public readonly env: EnvironmentAPI;

  /**
   * Memory operations (search, store)
   */
  public readonly memory: MemoryAPI;

  /**
   * Search operations (solve)
   */
  public readonly search: SearchAPI;

  constructor(options: CognitiveCoreOptions = {}) {
    // Auto-detect venv if pythonPath not specified
    let pythonPath = options.pythonPath;
    if (!pythonPath) {
      const venvPython = getPythonPath();
      if (venvPython) {
        pythonPath = venvPython;
      }
    }

    this.client = new CognitiveCoreClient({ ...options, pythonPath });
    this.env = new EnvironmentAPI(this.client);
    this.memory = new MemoryAPI(this.client);
    this.search = new SearchAPI(this.client);
  }

  /**
   * Start the Python subprocess.
   */
  async start(): Promise<void> {
    await this.client.start();
  }

  /**
   * Stop the Python subprocess.
   */
  async stop(): Promise<void> {
    await this.client.stop();
  }

  /**
   * Get the version of the Python cognitive-core package.
   */
  async version(): Promise<string> {
    const result = await this.client.execute<{ version: string }>("version");
    return result.version;
  }

  /**
   * Check if the client is running.
   */
  get isRunning(): boolean {
    return this.client.isRunning;
  }

  /**
   * Access the underlying client for advanced usage.
   */
  get rawClient(): CognitiveCoreClient {
    return this.client;
  }
}

// Default export
export default CognitiveCore;
