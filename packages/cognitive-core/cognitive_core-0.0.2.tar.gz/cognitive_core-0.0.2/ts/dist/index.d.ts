import { EventEmitter } from 'events';

/**
 * TypeScript type definitions for Cognitive Core.
 *
 * These types mirror the Python dataclasses in cognitive_core.core.types
 */
/**
 * Verification specification for tasks
 */
interface VerificationSpec {
    method: string;
    expectedOutput?: unknown;
    testCommand?: string;
    timeout?: number;
}
/**
 * Domain-agnostic task representation
 */
interface Task {
    id: string;
    domain: string;
    description: string;
    context: Record<string, unknown>;
    verification: VerificationSpec;
}
/**
 * Single step in a trajectory
 */
interface Step {
    thought?: string;
    action: string;
    observation: string;
    metadata?: Record<string, unknown>;
}
/**
 * Result of a trajectory
 */
interface Outcome {
    success: boolean;
    partialScore?: number;
    errorInfo?: string;
    verificationDetails?: Record<string, unknown>;
}
/**
 * Complete trajectory for a task attempt
 */
interface Trajectory {
    task: Task;
    steps: Step[];
    outcome: Outcome;
    agentId: string;
    timestamp: string;
    llmCalls?: number;
    totalTokens?: number;
    wallTimeSeconds?: number;
}
/**
 * Reusable code pattern
 */
interface CodeConcept {
    id: string;
    name: string;
    description: string;
    code: string;
    signature: string;
    examples: Array<[string, string]>;
    usageCount?: number;
    successRate?: number;
}
/**
 * Stored experience for retrieval
 */
interface Experience {
    id: string;
    taskInput: string;
    solutionOutput: string;
    feedback: string;
    success: boolean;
    trajectoryId: string;
    timestamp: string;
}
/**
 * Abstract reasoning pattern
 */
interface Strategy {
    id: string;
    situation: string;
    suggestion: string;
    parameters: Array<Record<string, string>>;
    usageCount?: number;
    successRate?: number;
}
/**
 * A candidate solution
 */
interface Candidate {
    solution: unknown;
    confidence: number;
    reasoning: string;
    source: "generated" | "adapted" | "retrieved";
    fitness?: number;
    parentIds?: string[];
    trajectory?: Trajectory;
}
/**
 * Output of task router
 */
interface RoutingDecision {
    strategy: "direct" | "evolutionary" | "mcts" | "adapt";
    relevantConcepts: CodeConcept[];
    similarExperiences: Experience[];
    suggestedStrategies: Strategy[];
    estimatedDifficulty: number;
    searchBudget: number;
}
/**
 * Step result from environment
 */
interface StepResult {
    observation: string;
    reward: number;
    done: boolean;
    info: Record<string, unknown>;
}
/**
 * ARC grid type (2D array of integers 0-9)
 */
type Grid = number[][];
/**
 * ARC task structure
 */
interface ARCTask {
    id: string;
    train: Array<[Grid, Grid]>;
    test: Array<[Grid, Grid]>;
}
/**
 * Command request to Python subprocess
 */
interface CommandRequest {
    command: string;
    args?: Record<string, unknown>;
}
/**
 * Response from Python subprocess
 */
interface CommandResponse<T = unknown> {
    success: boolean;
    result?: T;
    error?: string;
}
/**
 * Options for CognitiveCore client
 */
interface CognitiveCoreOptions {
    /**
     * Path to Python executable (default: "python")
     */
    pythonPath?: string;
    /**
     * Working directory for Python process
     */
    cwd?: string;
    /**
     * Environment variables for Python process
     */
    env?: Record<string, string>;
    /**
     * Timeout for commands in milliseconds (default: 30000)
     */
    timeout?: number;
}

/**
 * Python subprocess client for Cognitive Core.
 *
 * Manages communication with the Python cognitive-core package via JSON
 * over stdin/stdout.
 */

/**
 * Client that communicates with the Python cognitive-core package.
 *
 * @example
 * ```typescript
 * const client = new CognitiveCoreClient();
 * await client.start();
 *
 * const result = await client.execute("version");
 * console.log(result); // { version: "0.1.0" }
 *
 * await client.stop();
 * ```
 */
declare class CognitiveCoreClient extends EventEmitter {
    private process;
    private buffer;
    private pendingRequests;
    private requestId;
    private options;
    constructor(options?: CognitiveCoreOptions);
    /**
     * Start the Python subprocess.
     */
    start(): Promise<void>;
    /**
     * Stop the Python subprocess.
     */
    stop(): Promise<void>;
    /**
     * Execute a command on the Python process.
     *
     * @param command - Command to execute (e.g., "memory.search", "env.reset")
     * @param args - Command arguments
     * @returns Command result
     */
    execute<T = unknown>(command: string, args?: Record<string, unknown>): Promise<T>;
    /**
     * Check if the client is running.
     */
    get isRunning(): boolean;
    private sendRequest;
    private handleData;
    private handleResponse;
    private cleanup;
}

/**
 * Setup utilities for managing Python virtual environment and dependencies.
 */
interface SetupOptions {
    /**
     * Directory where the virtual environment will be created.
     * Defaults to ".cognitive-core" in current working directory.
     */
    venvDir?: string;
    /**
     * Python executable to use for creating the venv.
     * Defaults to "python3" on Unix, "python" on Windows.
     */
    pythonPath?: string;
    /**
     * Version of cognitive-core to install.
     * Defaults to latest.
     */
    version?: string;
    /**
     * Extra pip packages to install.
     */
    extras?: string[];
    /**
     * Whether to show installation progress.
     * Defaults to true.
     */
    verbose?: boolean;
}
interface SetupResult {
    /**
     * Path to the virtual environment directory.
     */
    venvPath: string;
    /**
     * Path to the Python executable in the venv.
     */
    pythonPath: string;
    /**
     * Path to pip in the venv.
     */
    pipPath: string;
    /**
     * Whether the venv was newly created (vs already existed).
     */
    created: boolean;
    /**
     * Installed version of cognitive-core.
     */
    version: string;
}
/**
 * Setup the Python environment for cognitive-core.
 *
 * Creates a virtual environment and installs the cognitive-core package.
 *
 * @example
 * ```typescript
 * import { setup } from "cognitive-core";
 *
 * // Basic setup
 * const result = await setup();
 * console.log(`Installed cognitive-core ${result.version}`);
 *
 * // Custom options
 * const result = await setup({
 *   venvDir: "./my-venv",
 *   extras: ["arc", "embeddings"],
 *   verbose: true,
 * });
 * ```
 */
declare function setup(options?: SetupOptions): Promise<SetupResult>;
/**
 * Check if cognitive-core is set up in the given directory.
 */
declare function isSetUp(venvDir?: string): boolean;
/**
 * Get the Python path for an existing setup.
 * Returns null if not set up.
 */
declare function getPythonPath(venvDir?: string): string | null;

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

/**
 * Environment operations
 */
declare class EnvironmentAPI {
    private client;
    constructor(client: CognitiveCoreClient);
    /**
     * Create a new environment.
     */
    create(domain?: string): Promise<{
        envId: string;
        domain: string;
    }>;
    /**
     * Reset an environment with a task.
     */
    reset(envId: string, task: Partial<Task>): Promise<{
        envId: string;
        observation: string;
    }>;
    /**
     * Execute an action in the environment.
     */
    step(envId: string, action: string): Promise<StepResult>;
    /**
     * Verify a solution.
     */
    verify(envId: string, solution: unknown): Promise<Outcome>;
}
/**
 * Memory operations
 */
declare class MemoryAPI {
    private client;
    constructor(client: CognitiveCoreClient);
    /**
     * Search for similar experiences.
     */
    searchExperiences(query: string, k?: number): Promise<Experience[]>;
    /**
     * Search for relevant strategies.
     */
    searchStrategies(query: string, k?: number): Promise<Strategy[]>;
    /**
     * Search for relevant concepts.
     */
    searchConcepts(query: string, k?: number): Promise<CodeConcept[]>;
    /**
     * Store a trajectory in memory.
     */
    store(trajectory: unknown): Promise<{
        id: string;
    }>;
}
/**
 * Search operations
 */
declare class SearchAPI {
    private client;
    constructor(client: CognitiveCoreClient);
    /**
     * Solve a task using the configured search strategy.
     */
    solve(task: Partial<Task>): Promise<{
        trajectory: unknown;
        outcome: Outcome;
    }>;
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
declare class CognitiveCore {
    private client;
    /**
     * Environment operations (create, reset, step, verify)
     */
    readonly env: EnvironmentAPI;
    /**
     * Memory operations (search, store)
     */
    readonly memory: MemoryAPI;
    /**
     * Search operations (solve)
     */
    readonly search: SearchAPI;
    constructor(options?: CognitiveCoreOptions);
    /**
     * Start the Python subprocess.
     */
    start(): Promise<void>;
    /**
     * Stop the Python subprocess.
     */
    stop(): Promise<void>;
    /**
     * Get the version of the Python cognitive-core package.
     */
    version(): Promise<string>;
    /**
     * Check if the client is running.
     */
    get isRunning(): boolean;
    /**
     * Access the underlying client for advanced usage.
     */
    get rawClient(): CognitiveCoreClient;
}

export { type ARCTask, type Candidate, type CodeConcept, CognitiveCore, CognitiveCoreClient, type CognitiveCoreOptions, type CommandRequest, type CommandResponse, type Experience, type Grid, type Outcome, type RoutingDecision, type SetupOptions, type SetupResult, type Step, type StepResult, type Strategy, type Task, type Trajectory, type VerificationSpec, CognitiveCore as default, getPythonPath, isSetUp, setup };
