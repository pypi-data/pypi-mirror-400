/**
 * TypeScript type definitions for Cognitive Core.
 *
 * These types mirror the Python dataclasses in cognitive_core.core.types
 */

// =============================================================================
// Core Types
// =============================================================================

/**
 * Verification specification for tasks
 */
export interface VerificationSpec {
  method: string;
  expectedOutput?: unknown;
  testCommand?: string;
  timeout?: number;
}

/**
 * Domain-agnostic task representation
 */
export interface Task {
  id: string;
  domain: string;
  description: string;
  context: Record<string, unknown>;
  verification: VerificationSpec;
}

/**
 * Single step in a trajectory
 */
export interface Step {
  thought?: string;
  action: string;
  observation: string;
  metadata?: Record<string, unknown>;
}

/**
 * Result of a trajectory
 */
export interface Outcome {
  success: boolean;
  partialScore?: number;
  errorInfo?: string;
  verificationDetails?: Record<string, unknown>;
}

/**
 * Complete trajectory for a task attempt
 */
export interface Trajectory {
  task: Task;
  steps: Step[];
  outcome: Outcome;
  agentId: string;
  timestamp: string;
  llmCalls?: number;
  totalTokens?: number;
  wallTimeSeconds?: number;
}

// =============================================================================
// Memory Types
// =============================================================================

/**
 * Reusable code pattern
 */
export interface CodeConcept {
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
export interface Experience {
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
export interface Strategy {
  id: string;
  situation: string;
  suggestion: string;
  parameters: Array<Record<string, string>>;
  usageCount?: number;
  successRate?: number;
}

// =============================================================================
// Search Types
// =============================================================================

/**
 * A candidate solution
 */
export interface Candidate {
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
export interface RoutingDecision {
  strategy: "direct" | "evolutionary" | "mcts" | "adapt";
  relevantConcepts: CodeConcept[];
  similarExperiences: Experience[];
  suggestedStrategies: Strategy[];
  estimatedDifficulty: number;
  searchBudget: number;
}

// =============================================================================
// Environment Types
// =============================================================================

/**
 * Step result from environment
 */
export interface StepResult {
  observation: string;
  reward: number;
  done: boolean;
  info: Record<string, unknown>;
}

/**
 * ARC grid type (2D array of integers 0-9)
 */
export type Grid = number[][];

/**
 * ARC task structure
 */
export interface ARCTask {
  id: string;
  train: Array<[Grid, Grid]>;
  test: Array<[Grid, Grid]>;
}

// =============================================================================
// Client Types
// =============================================================================

/**
 * Command request to Python subprocess
 */
export interface CommandRequest {
  command: string;
  args?: Record<string, unknown>;
}

/**
 * Response from Python subprocess
 */
export interface CommandResponse<T = unknown> {
  success: boolean;
  result?: T;
  error?: string;
}

/**
 * Options for CognitiveCore client
 */
export interface CognitiveCoreOptions {
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
