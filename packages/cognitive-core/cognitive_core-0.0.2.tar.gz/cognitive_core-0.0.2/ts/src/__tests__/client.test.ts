/**
 * Tests for the CognitiveCoreClient subprocess wrapper.
 */

import { describe, it, expect, beforeAll, afterAll, beforeEach, afterEach } from "vitest";
import { CognitiveCoreClient } from "../client.js";

describe("CognitiveCoreClient", () => {
  describe("lifecycle", () => {
    it("should start and stop cleanly", async () => {
      const client = new CognitiveCoreClient();

      expect(client.isRunning).toBe(false);

      await client.start();
      expect(client.isRunning).toBe(true);

      await client.stop();
      expect(client.isRunning).toBe(false);
    });

    it("should throw if started twice", async () => {
      const client = new CognitiveCoreClient();

      await client.start();

      await expect(client.start()).rejects.toThrow("already started");

      await client.stop();
    });

    it("should handle stop on non-started client", async () => {
      const client = new CognitiveCoreClient();

      // Should not throw
      await client.stop();
      expect(client.isRunning).toBe(false);
    });
  });

  describe("execute", () => {
    let client: CognitiveCoreClient;

    beforeEach(async () => {
      client = new CognitiveCoreClient();
      await client.start();
    });

    afterEach(async () => {
      await client.stop();
    });

    it("should execute version command", async () => {
      const result = await client.execute<{ version: string }>("version");

      expect(result).toHaveProperty("version");
      expect(typeof result.version).toBe("string");
      expect(result.version).toMatch(/^\d+\.\d+\.\d+$/);
    });

    it("should execute env.create command", async () => {
      const result = await client.execute<{ env_id: string; domain: string }>(
        "env.create",
        { domain: "arc" }
      );

      expect(result).toHaveProperty("env_id");
      expect(result).toHaveProperty("domain");
      expect(result.domain).toBe("arc");
    });

    it("should execute env.reset command", async () => {
      const result = await client.execute<{ env_id: string; observation: string }>(
        "env.reset",
        {
          env_id: "test_env",
          task: {
            id: "task-1",
            description: "Test task",
          },
        }
      );

      expect(result).toHaveProperty("observation");
    });

    it("should execute env.step command", async () => {
      const result = await client.execute<{
        observation: string;
        reward: number;
        done: boolean;
        info: Record<string, unknown>;
      }>("env.step", {
        env_id: "test_env",
        action: "test action",
      });

      expect(result).toHaveProperty("observation");
      expect(result).toHaveProperty("reward");
      expect(result).toHaveProperty("done");
      expect(typeof result.reward).toBe("number");
      expect(typeof result.done).toBe("boolean");
    });

    it("should execute env.verify command", async () => {
      const result = await client.execute<{
        success: boolean;
        partial_score: number;
        details: Record<string, unknown>;
      }>("env.verify", {
        env_id: "test_env",
        solution: [[1, 0], [0, 1]],
      });

      expect(result).toHaveProperty("success");
      expect(result).toHaveProperty("partial_score");
      expect(typeof result.success).toBe("boolean");
      expect(typeof result.partial_score).toBe("number");
    });

    it("should execute memory.search command", async () => {
      const result = await client.execute<{ message: string }>(
        "memory.search",
        { query: "test query", k: 5 }
      );

      expect(result).toHaveProperty("message");
    });

    it("should throw on unknown command", async () => {
      await expect(
        client.execute("unknown.command", {})
      ).rejects.toThrow("Unknown command");
    });

    it("should throw when not started", async () => {
      const newClient = new CognitiveCoreClient();

      await expect(
        newClient.execute("version")
      ).rejects.toThrow("not started");
    });
  });

  describe("options", () => {
    it("should accept custom python path", async () => {
      const client = new CognitiveCoreClient({
        pythonPath: "python3",
      });

      await client.start();
      const result = await client.execute<{ version: string }>("version");
      expect(result.version).toBeDefined();
      await client.stop();
    });

    it("should accept custom timeout", () => {
      const client = new CognitiveCoreClient({
        timeout: 60000,
      });

      // Just verify it doesn't throw
      expect(client).toBeDefined();
    });
  });

  describe("events", () => {
    it("should emit ready event on start", async () => {
      const client = new CognitiveCoreClient();

      const readyPromise = new Promise<void>((resolve) => {
        client.on("ready", () => resolve());
      });

      await client.start();
      await readyPromise;

      await client.stop();
    });

    it("should emit exit event on stop", async () => {
      const client = new CognitiveCoreClient();

      await client.start();

      const exitPromise = new Promise<{ code: number | null; signal: string | null }>((resolve) => {
        client.on("exit", (data) => resolve(data));
      });

      await client.stop();
      const exitData = await exitPromise;

      expect(exitData).toHaveProperty("code");
      expect(exitData).toHaveProperty("signal");
    });
  });
});
