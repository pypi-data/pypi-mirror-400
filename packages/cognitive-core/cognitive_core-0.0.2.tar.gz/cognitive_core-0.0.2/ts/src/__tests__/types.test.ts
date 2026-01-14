/**
 * Tests for TypeScript type definitions.
 *
 * These tests verify that the type definitions compile correctly
 * and match the expected structure.
 */

import { describe, it, expect } from "vitest";
import type {
  Task,
  Step,
  Outcome,
  Trajectory,
  Experience,
  Strategy,
  CodeConcept,
  Candidate,
  RoutingDecision,
  Grid,
  ARCTask,
  StepResult,
  VerificationSpec,
  CognitiveCoreOptions,
} from "../types.js";

describe("Type definitions", () => {
  describe("Task", () => {
    it("should accept valid task object", () => {
      const task: Task = {
        id: "task-1",
        domain: "arc",
        description: "Test task",
        context: { key: "value" },
        verification: { method: "exact_match" },
      };

      expect(task.id).toBe("task-1");
      expect(task.domain).toBe("arc");
    });

    it("should accept task with all verification fields", () => {
      const task: Task = {
        id: "task-2",
        domain: "swe",
        description: "SWE task",
        context: {},
        verification: {
          method: "test_suite",
          expectedOutput: "success",
          testCommand: "pytest",
          timeout: 30000,
        },
      };

      expect(task.verification.timeout).toBe(30000);
    });
  });

  describe("Step", () => {
    it("should accept step with all fields", () => {
      const step: Step = {
        thought: "Analyzing the pattern",
        action: "rotate_grid(90)",
        observation: "Grid rotated successfully",
        metadata: { tokens: 100 },
      };

      expect(step.action).toBe("rotate_grid(90)");
    });

    it("should accept step with minimal fields", () => {
      const step: Step = {
        action: "noop",
        observation: "No change",
      };

      expect(step.thought).toBeUndefined();
    });
  });

  describe("Outcome", () => {
    it("should accept successful outcome", () => {
      const outcome: Outcome = {
        success: true,
        partialScore: 1.0,
      };

      expect(outcome.success).toBe(true);
    });

    it("should accept failed outcome with error", () => {
      const outcome: Outcome = {
        success: false,
        partialScore: 0.5,
        errorInfo: "Shape mismatch",
        verificationDetails: { expected: [2, 2], actual: [3, 3] },
      };

      expect(outcome.errorInfo).toBe("Shape mismatch");
    });
  });

  describe("Trajectory", () => {
    it("should accept complete trajectory", () => {
      const trajectory: Trajectory = {
        task: {
          id: "t1",
          domain: "arc",
          description: "test",
          context: {},
          verification: { method: "exact" },
        },
        steps: [
          { action: "think", observation: "done" },
        ],
        outcome: { success: true },
        agentId: "agent-1",
        timestamp: "2024-01-01T00:00:00Z",
        llmCalls: 5,
        totalTokens: 1000,
        wallTimeSeconds: 10.5,
      };

      expect(trajectory.agentId).toBe("agent-1");
      expect(trajectory.llmCalls).toBe(5);
    });
  });

  describe("Memory types", () => {
    it("should accept Experience", () => {
      const exp: Experience = {
        id: "exp-1",
        taskInput: "input",
        solutionOutput: "output",
        feedback: "correct",
        success: true,
        trajectoryId: "traj-1",
        timestamp: "2024-01-01",
      };

      expect(exp.success).toBe(true);
    });

    it("should accept Strategy", () => {
      const strategy: Strategy = {
        id: "strat-1",
        situation: "When grid has symmetry",
        suggestion: "Try reflection operation",
        parameters: [{ name: "axis", type: "string" }],
        usageCount: 10,
        successRate: 0.8,
      };

      expect(strategy.successRate).toBe(0.8);
    });

    it("should accept CodeConcept", () => {
      const concept: CodeConcept = {
        id: "concept-1",
        name: "rotate_90",
        description: "Rotate grid 90 degrees",
        code: "def rotate_90(grid): ...",
        signature: "(grid: Grid) -> Grid",
        examples: [["[[1,2],[3,4]]", "[[3,1],[4,2]]"]],
        usageCount: 50,
        successRate: 0.95,
      };

      expect(concept.name).toBe("rotate_90");
    });
  });

  describe("Search types", () => {
    it("should accept Candidate", () => {
      const candidate: Candidate = {
        solution: [[1, 0], [0, 1]],
        confidence: 0.9,
        reasoning: "Pattern matches training",
        source: "generated",
        fitness: 0.85,
        parentIds: ["parent-1"],
      };

      expect(candidate.source).toBe("generated");
    });

    it("should accept RoutingDecision", () => {
      const decision: RoutingDecision = {
        strategy: "evolutionary",
        relevantConcepts: [],
        similarExperiences: [],
        suggestedStrategies: [],
        estimatedDifficulty: 0.7,
        searchBudget: 100,
      };

      expect(decision.strategy).toBe("evolutionary");
    });
  });

  describe("ARC types", () => {
    it("should accept Grid", () => {
      const grid: Grid = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
      ];

      expect(grid.length).toBe(3);
      expect(grid[0].length).toBe(3);
    });

    it("should accept ARCTask", () => {
      const task: ARCTask = {
        id: "arc-001",
        train: [
          [[[0, 1], [1, 0]], [[1, 0], [0, 1]]],
        ],
        test: [
          [[[0, 0], [1, 1]], [[1, 1], [0, 0]]],
        ],
      };

      expect(task.train.length).toBe(1);
      expect(task.test.length).toBe(1);
    });
  });

  describe("StepResult", () => {
    it("should accept step result", () => {
      const result: StepResult = {
        observation: "Action completed",
        reward: 0.5,
        done: false,
        info: { step: 1 },
      };

      expect(result.done).toBe(false);
    });
  });

  describe("CognitiveCoreOptions", () => {
    it("should accept all options", () => {
      const options: CognitiveCoreOptions = {
        pythonPath: "/usr/bin/python3",
        cwd: "/home/user/project",
        env: { PYTHONPATH: "/custom/path" },
        timeout: 60000,
      };

      expect(options.timeout).toBe(60000);
    });

    it("should accept partial options", () => {
      const options: CognitiveCoreOptions = {
        timeout: 30000,
      };

      expect(options.pythonPath).toBeUndefined();
    });
  });
});
