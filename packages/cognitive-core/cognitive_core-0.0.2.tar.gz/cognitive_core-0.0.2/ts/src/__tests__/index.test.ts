/**
 * Tests for the high-level CognitiveCore API.
 */

import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { CognitiveCore } from "../index.js";

describe("CognitiveCore", () => {
  let core: CognitiveCore;

  beforeEach(async () => {
    core = new CognitiveCore();
    await core.start();
  });

  afterEach(async () => {
    await core.stop();
  });

  describe("lifecycle", () => {
    it("should start and stop cleanly", async () => {
      const newCore = new CognitiveCore();

      expect(newCore.isRunning).toBe(false);

      await newCore.start();
      expect(newCore.isRunning).toBe(true);

      await newCore.stop();
      expect(newCore.isRunning).toBe(false);
    });

    it("should report correct running state", () => {
      expect(core.isRunning).toBe(true);
    });
  });

  describe("version", () => {
    it("should return version string", async () => {
      const version = await core.version();

      expect(typeof version).toBe("string");
      expect(version).toMatch(/^\d+\.\d+\.\d+$/);
    });

    it("should return 0.1.0 for current version", async () => {
      const version = await core.version();

      expect(version).toBe("0.1.0");
    });
  });

  describe("env API", () => {
    it("should create environment", async () => {
      const result = await core.env.create("arc");

      expect(result).toHaveProperty("envId");
      expect(result).toHaveProperty("domain");
      expect(result.domain).toBe("arc");
    });

    it("should create passthrough environment by default", async () => {
      const result = await core.env.create();

      expect(result.domain).toBe("passthrough");
    });

    it("should reset environment with task", async () => {
      const env = await core.env.create("arc");

      const result = await core.env.reset(env.envId, {
        id: "test-task",
        domain: "arc",
        description: "Test task description",
      });

      expect(result).toHaveProperty("envId");
      expect(result).toHaveProperty("observation");
    });

    it("should execute step in environment", async () => {
      const env = await core.env.create("arc");
      await core.env.reset(env.envId, { id: "task", description: "test" });

      const result = await core.env.step(env.envId, "analyze pattern");

      expect(result).toHaveProperty("observation");
      expect(result).toHaveProperty("reward");
      expect(result).toHaveProperty("done");
      expect(result).toHaveProperty("info");
    });

    it("should verify solution", async () => {
      const env = await core.env.create("arc");
      await core.env.reset(env.envId, { id: "task", description: "test" });

      const outcome = await core.env.verify(env.envId, [[1, 0], [0, 1]]);

      expect(outcome).toHaveProperty("success");
      expect(outcome).toHaveProperty("partialScore");
      expect(typeof outcome.success).toBe("boolean");
      expect(typeof outcome.partialScore).toBe("number");
    });
  });

  describe("memory API", () => {
    it("should search experiences", async () => {
      const experiences = await core.memory.searchExperiences("test query", 5);

      expect(Array.isArray(experiences)).toBe(true);
    });

    it("should search strategies", async () => {
      const strategies = await core.memory.searchStrategies("symmetry task", 3);

      expect(Array.isArray(strategies)).toBe(true);
    });

    it("should search concepts", async () => {
      const concepts = await core.memory.searchConcepts("grid rotation", 5);

      expect(Array.isArray(concepts)).toBe(true);
    });

    it("should use default k value", async () => {
      // Should not throw with default k
      const experiences = await core.memory.searchExperiences("query");
      expect(Array.isArray(experiences)).toBe(true);
    });
  });

  describe("search API", () => {
    it("should solve task", async () => {
      const result = await core.search.solve({
        id: "test-task",
        domain: "arc",
        description: "Solve this puzzle",
      });

      expect(result).toHaveProperty("message");
    });
  });

  describe("rawClient", () => {
    it("should expose underlying client", () => {
      expect(core.rawClient).toBeDefined();
      expect(core.rawClient.isRunning).toBe(true);
    });

    it("should allow direct command execution", async () => {
      const result = await core.rawClient.execute<{ version: string }>("version");

      expect(result.version).toBe("0.1.0");
    });
  });
});

describe("CognitiveCore options", () => {
  it("should accept custom options", async () => {
    const core = new CognitiveCore({
      pythonPath: "python3",
      timeout: 60000,
    });

    await core.start();
    expect(core.isRunning).toBe(true);

    await core.stop();
  });
});
