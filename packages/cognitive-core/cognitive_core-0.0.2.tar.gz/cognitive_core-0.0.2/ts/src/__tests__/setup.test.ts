/**
 * Tests for setup utilities.
 *
 * Note: These tests are skipped by default as they modify the filesystem
 * and install packages. Run with SETUP_TESTS=1 to enable.
 */

import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { existsSync, rmSync } from "fs";
import { join } from "path";
import { tmpdir } from "os";
import { setup, isSetUp, getPythonPath } from "../setup.js";

const RUN_SETUP_TESTS = process.env.SETUP_TESTS === "1";
const TEST_DIR = join(tmpdir(), "cognitive-core-test-" + Date.now());

describe.skipIf(!RUN_SETUP_TESTS)("setup", () => {
  const venvDir = join(TEST_DIR, ".cognitive-core");

  afterAll(() => {
    // Cleanup test directory
    if (existsSync(TEST_DIR)) {
      rmSync(TEST_DIR, { recursive: true, force: true });
    }
  });

  it("should create virtual environment", async () => {
    const result = await setup({
      venvDir,
      verbose: false,
    });

    expect(result.created).toBe(true);
    expect(existsSync(result.venvPath)).toBe(true);
    expect(existsSync(result.pythonPath)).toBe(true);
    expect(result.version).toMatch(/^\d+\.\d+\.\d+$/);
  }, 120000); // 2 minute timeout for installation

  it("should detect existing setup", async () => {
    expect(isSetUp(venvDir)).toBe(true);
  });

  it("should return python path for existing setup", () => {
    const pythonPath = getPythonPath(venvDir);
    expect(pythonPath).not.toBeNull();
    expect(existsSync(pythonPath!)).toBe(true);
  });

  it("should reuse existing environment", async () => {
    const result = await setup({
      venvDir,
      verbose: false,
    });

    expect(result.created).toBe(false);
  });

  it("should return null for non-existent setup", () => {
    const pythonPath = getPythonPath("./non-existent-dir");
    expect(pythonPath).toBeNull();
  });

  it("should report false for non-existent setup", () => {
    expect(isSetUp("./non-existent-dir")).toBe(false);
  });
});

describe("setup helpers (no installation)", () => {
  it("isSetUp returns false for missing directory", () => {
    expect(isSetUp("./definitely-does-not-exist")).toBe(false);
  });

  it("getPythonPath returns null for missing directory", () => {
    expect(getPythonPath("./definitely-does-not-exist")).toBeNull();
  });
});
