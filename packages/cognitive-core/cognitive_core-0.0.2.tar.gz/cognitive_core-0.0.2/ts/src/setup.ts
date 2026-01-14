/**
 * Setup utilities for managing Python virtual environment and dependencies.
 */

import { spawn, execSync } from "child_process";
import { existsSync, mkdirSync } from "fs";
import { join, resolve } from "path";
import { platform } from "os";

export interface SetupOptions {
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

export interface SetupResult {
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
 * Find a working Python executable.
 */
function findPython(preferredPath?: string): string {
  const candidates = preferredPath
    ? [preferredPath]
    : platform() === "win32"
      ? ["python", "python3", "py"]
      : ["python3", "python"];

  for (const cmd of candidates) {
    try {
      execSync(`${cmd} --version`, { stdio: "pipe" });
      return cmd;
    } catch {
      continue;
    }
  }

  throw new Error(
    "Python not found. Please install Python 3.10+ and ensure it's in your PATH.\n" +
    "Download from: https://www.python.org/downloads/"
  );
}

/**
 * Get paths for executables within a virtual environment.
 */
function getVenvPaths(venvDir: string): { python: string; pip: string } {
  const isWindows = platform() === "win32";
  const binDir = isWindows ? "Scripts" : "bin";
  const ext = isWindows ? ".exe" : "";

  return {
    python: join(venvDir, binDir, `python${ext}`),
    pip: join(venvDir, binDir, `pip${ext}`),
  };
}

/**
 * Run a command and optionally stream output.
 */
function runCommand(
  command: string,
  args: string[],
  options: { verbose?: boolean; cwd?: string } = {}
): Promise<string> {
  return new Promise((resolve, reject) => {
    const proc = spawn(command, args, {
      cwd: options.cwd,
      stdio: options.verbose ? "inherit" : "pipe",
      shell: platform() === "win32",
    });

    let output = "";

    if (!options.verbose) {
      proc.stdout?.on("data", (data) => {
        output += data.toString();
      });
      proc.stderr?.on("data", (data) => {
        output += data.toString();
      });
    }

    proc.on("error", reject);
    proc.on("close", (code) => {
      if (code === 0) {
        resolve(output);
      } else {
        reject(new Error(`Command failed with code ${code}: ${command} ${args.join(" ")}\n${output}`));
      }
    });
  });
}

/**
 * Check if cognitive-core is installed and get its version.
 */
async function getInstalledVersion(pythonPath: string): Promise<string | null> {
  try {
    const output = await runCommand(pythonPath, [
      "-c",
      "import cognitive_core; print(cognitive_core.__version__)",
    ]);
    return output.trim();
  } catch {
    return null;
  }
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
export async function setup(options: SetupOptions = {}): Promise<SetupResult> {
  const {
    venvDir = ".cognitive-core",
    pythonPath: preferredPython,
    version,
    extras = [],
    verbose = true,
  } = options;

  const venvPath = resolve(venvDir);
  const log = verbose ? console.log.bind(console) : () => {};

  // Find Python
  log("🔍 Finding Python...");
  const systemPython = findPython(preferredPython);
  log(`   Found: ${systemPython}`);

  // Check Python version
  const versionOutput = execSync(`${systemPython} --version`, { encoding: "utf-8" });
  const versionMatch = versionOutput.match(/Python (\d+)\.(\d+)/);
  if (versionMatch) {
    const [, major, minor] = versionMatch;
    if (parseInt(major) < 3 || (parseInt(major) === 3 && parseInt(minor) < 10)) {
      throw new Error(
        `Python 3.10+ required, found ${versionOutput.trim()}.\n` +
        "Please upgrade Python: https://www.python.org/downloads/"
      );
    }
  }

  // Check if venv already exists
  const venvPaths = getVenvPaths(venvPath);
  const venvExists = existsSync(venvPaths.python);
  let created = false;

  if (!venvExists) {
    log("📦 Creating virtual environment...");
    mkdirSync(venvPath, { recursive: true });
    await runCommand(systemPython, ["-m", "venv", venvPath], { verbose });
    created = true;
    log(`   Created: ${venvPath}`);
  } else {
    log(`📦 Using existing virtual environment: ${venvPath}`);
  }

  // Check if cognitive-core is already installed
  let installedVersion = await getInstalledVersion(venvPaths.python);

  if (!installedVersion) {
    log("⬇️  Installing cognitive-core...");

    // Build package spec
    let packageSpec = "cognitive-core";
    if (version) {
      packageSpec += `==${version}`;
    }
    if (extras.length > 0) {
      packageSpec += `[${extras.join(",")}]`;
    }

    await runCommand(
      venvPaths.pip,
      ["install", "--upgrade", "pip"],
      { verbose }
    );

    await runCommand(
      venvPaths.pip,
      ["install", packageSpec],
      { verbose }
    );

    installedVersion = await getInstalledVersion(venvPaths.python);
    log(`   Installed: cognitive-core ${installedVersion}`);
  } else {
    log(`✅ cognitive-core ${installedVersion} already installed`);
  }

  log("");
  log("🎉 Setup complete!");
  log(`   Python: ${venvPaths.python}`);
  log(`   Version: ${installedVersion}`);
  log("");

  return {
    venvPath,
    pythonPath: venvPaths.python,
    pipPath: venvPaths.pip,
    created,
    version: installedVersion ?? "unknown",
  };
}

/**
 * Check if cognitive-core is set up in the given directory.
 */
export function isSetUp(venvDir: string = ".cognitive-core"): boolean {
  const venvPath = resolve(venvDir);
  const venvPaths = getVenvPaths(venvPath);
  return existsSync(venvPaths.python);
}

/**
 * Get the Python path for an existing setup.
 * Returns null if not set up.
 */
export function getPythonPath(venvDir: string = ".cognitive-core"): string | null {
  const venvPath = resolve(venvDir);
  const venvPaths = getVenvPaths(venvPath);
  return existsSync(venvPaths.python) ? venvPaths.python : null;
}
