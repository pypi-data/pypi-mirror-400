// src/client.ts
import { spawn } from "child_process";
import { EventEmitter } from "events";
var CognitiveCoreClient = class extends EventEmitter {
  process = null;
  buffer = "";
  pendingRequests = /* @__PURE__ */ new Map();
  requestId = 0;
  options;
  constructor(options = {}) {
    super();
    this.options = {
      pythonPath: options.pythonPath ?? "python",
      cwd: options.cwd ?? process.cwd(),
      env: options.env ?? {},
      timeout: options.timeout ?? 3e4
    };
  }
  /**
   * Start the Python subprocess.
   */
  async start() {
    if (this.process) {
      throw new Error("Client already started");
    }
    return new Promise((resolve2, reject) => {
      this.process = spawn(
        this.options.pythonPath,
        ["-m", "cognitive_core.cli", "--json"],
        {
          cwd: this.options.cwd,
          env: { ...process.env, ...this.options.env },
          stdio: ["pipe", "pipe", "pipe"]
        }
      );
      this.process.on("error", (error) => {
        this.emit("error", error);
        reject(error);
      });
      this.process.on("exit", (code, signal) => {
        this.emit("exit", { code, signal });
        this.cleanup();
      });
      this.process.stdout?.on("data", (data) => {
        this.handleData(data.toString());
      });
      this.process.stderr?.on("data", (data) => {
        this.emit("stderr", data.toString());
      });
      setTimeout(async () => {
        try {
          const response = await this.execute("version");
          if (response.version) {
            this.emit("ready", response);
            resolve2();
          } else {
            reject(new Error("Failed to verify Python process"));
          }
        } catch (error) {
          reject(error);
        }
      }, 100);
    });
  }
  /**
   * Stop the Python subprocess.
   */
  async stop() {
    if (!this.process) {
      return;
    }
    return new Promise((resolve2) => {
      if (this.process) {
        this.process.once("exit", () => {
          this.cleanup();
          resolve2();
        });
        this.process.stdin?.end();
        this.process.kill("SIGTERM");
        setTimeout(() => {
          if (this.process) {
            this.process.kill("SIGKILL");
          }
          resolve2();
        }, 5e3);
      } else {
        resolve2();
      }
    });
  }
  /**
   * Execute a command on the Python process.
   *
   * @param command - Command to execute (e.g., "memory.search", "env.reset")
   * @param args - Command arguments
   * @returns Command result
   */
  async execute(command, args = {}) {
    if (!this.process?.stdin) {
      throw new Error("Client not started. Call start() first.");
    }
    const request = { command, args };
    const response = await this.sendRequest(request);
    if (!response.success) {
      throw new Error(response.error ?? "Unknown error");
    }
    return response.result;
  }
  /**
   * Check if the client is running.
   */
  get isRunning() {
    return this.process !== null && !this.process.killed;
  }
  sendRequest(request) {
    return new Promise((resolve2, reject) => {
      const id = this.requestId++;
      const json = JSON.stringify(request);
      const timeout = setTimeout(() => {
        this.pendingRequests.delete(id);
        reject(new Error(`Command timed out: ${request.command}`));
      }, this.options.timeout);
      this.pendingRequests.set(id, { resolve: resolve2, reject, timeout });
      this.process?.stdin?.write(json + "\n");
    });
  }
  handleData(data) {
    this.buffer += data;
    const lines = this.buffer.split("\n");
    this.buffer = lines.pop() ?? "";
    for (const line of lines) {
      if (line.trim()) {
        try {
          const response = JSON.parse(line);
          this.handleResponse(response);
        } catch (error) {
          this.emit("parseError", { line, error });
        }
      }
    }
  }
  handleResponse(response) {
    const [id, pending] = this.pendingRequests.entries().next().value ?? [
      null,
      null
    ];
    if (id !== null && pending) {
      clearTimeout(pending.timeout);
      this.pendingRequests.delete(id);
      pending.resolve(response);
    }
  }
  cleanup() {
    for (const [id, pending] of this.pendingRequests) {
      clearTimeout(pending.timeout);
      pending.reject(new Error("Process terminated"));
    }
    this.pendingRequests.clear();
    this.process = null;
    this.buffer = "";
  }
};

// src/setup.ts
import { spawn as spawn2, execSync } from "child_process";
import { existsSync, mkdirSync } from "fs";
import { join, resolve } from "path";
import { platform } from "os";
function findPython(preferredPath) {
  const candidates = preferredPath ? [preferredPath] : platform() === "win32" ? ["python", "python3", "py"] : ["python3", "python"];
  for (const cmd of candidates) {
    try {
      execSync(`${cmd} --version`, { stdio: "pipe" });
      return cmd;
    } catch {
      continue;
    }
  }
  throw new Error(
    "Python not found. Please install Python 3.10+ and ensure it's in your PATH.\nDownload from: https://www.python.org/downloads/"
  );
}
function getVenvPaths(venvDir) {
  const isWindows = platform() === "win32";
  const binDir = isWindows ? "Scripts" : "bin";
  const ext = isWindows ? ".exe" : "";
  return {
    python: join(venvDir, binDir, `python${ext}`),
    pip: join(venvDir, binDir, `pip${ext}`)
  };
}
function runCommand(command, args, options = {}) {
  return new Promise((resolve2, reject) => {
    const proc = spawn2(command, args, {
      cwd: options.cwd,
      stdio: options.verbose ? "inherit" : "pipe",
      shell: platform() === "win32"
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
        resolve2(output);
      } else {
        reject(new Error(`Command failed with code ${code}: ${command} ${args.join(" ")}
${output}`));
      }
    });
  });
}
async function getInstalledVersion(pythonPath) {
  try {
    const output = await runCommand(pythonPath, [
      "-c",
      "import cognitive_core; print(cognitive_core.__version__)"
    ]);
    return output.trim();
  } catch {
    return null;
  }
}
async function setup(options = {}) {
  const {
    venvDir = ".cognitive-core",
    pythonPath: preferredPython,
    version,
    extras = [],
    verbose = true
  } = options;
  const venvPath = resolve(venvDir);
  const log = verbose ? console.log.bind(console) : () => {
  };
  log("\u{1F50D} Finding Python...");
  const systemPython = findPython(preferredPython);
  log(`   Found: ${systemPython}`);
  const versionOutput = execSync(`${systemPython} --version`, { encoding: "utf-8" });
  const versionMatch = versionOutput.match(/Python (\d+)\.(\d+)/);
  if (versionMatch) {
    const [, major, minor] = versionMatch;
    if (parseInt(major) < 3 || parseInt(major) === 3 && parseInt(minor) < 10) {
      throw new Error(
        `Python 3.10+ required, found ${versionOutput.trim()}.
Please upgrade Python: https://www.python.org/downloads/`
      );
    }
  }
  const venvPaths = getVenvPaths(venvPath);
  const venvExists = existsSync(venvPaths.python);
  let created = false;
  if (!venvExists) {
    log("\u{1F4E6} Creating virtual environment...");
    mkdirSync(venvPath, { recursive: true });
    await runCommand(systemPython, ["-m", "venv", venvPath], { verbose });
    created = true;
    log(`   Created: ${venvPath}`);
  } else {
    log(`\u{1F4E6} Using existing virtual environment: ${venvPath}`);
  }
  let installedVersion = await getInstalledVersion(venvPaths.python);
  if (!installedVersion) {
    log("\u2B07\uFE0F  Installing cognitive-core...");
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
    log(`\u2705 cognitive-core ${installedVersion} already installed`);
  }
  log("");
  log("\u{1F389} Setup complete!");
  log(`   Python: ${venvPaths.python}`);
  log(`   Version: ${installedVersion}`);
  log("");
  return {
    venvPath,
    pythonPath: venvPaths.python,
    pipPath: venvPaths.pip,
    created,
    version: installedVersion ?? "unknown"
  };
}
function isSetUp(venvDir = ".cognitive-core") {
  const venvPath = resolve(venvDir);
  const venvPaths = getVenvPaths(venvPath);
  return existsSync(venvPaths.python);
}
function getPythonPath(venvDir = ".cognitive-core") {
  const venvPath = resolve(venvDir);
  const venvPaths = getVenvPaths(venvPath);
  return existsSync(venvPaths.python) ? venvPaths.python : null;
}

// src/index.ts
var EnvironmentAPI = class {
  constructor(client) {
    this.client = client;
  }
  /**
   * Create a new environment.
   */
  async create(domain = "passthrough") {
    const result = await this.client.execute(
      "env.create",
      { domain }
    );
    return { envId: result.env_id, domain: result.domain };
  }
  /**
   * Reset an environment with a task.
   */
  async reset(envId, task) {
    const result = await this.client.execute(
      "env.reset",
      { env_id: envId, task }
    );
    return { envId: result.env_id, observation: result.observation };
  }
  /**
   * Execute an action in the environment.
   */
  async step(envId, action) {
    return this.client.execute("env.step", { env_id: envId, action });
  }
  /**
   * Verify a solution.
   */
  async verify(envId, solution) {
    const result = await this.client.execute("env.verify", { env_id: envId, solution });
    return {
      success: result.success,
      partialScore: result.partial_score,
      verificationDetails: result.details
    };
  }
};
var MemoryAPI = class {
  constructor(client) {
    this.client = client;
  }
  /**
   * Search for similar experiences.
   */
  async searchExperiences(query, k = 5) {
    const result = await this.client.execute(
      "memory.search",
      { query, k, type: "experience" }
    );
    return result.experiences ?? [];
  }
  /**
   * Search for relevant strategies.
   */
  async searchStrategies(query, k = 5) {
    const result = await this.client.execute(
      "memory.search",
      { query, k, type: "strategy" }
    );
    return result.strategies ?? [];
  }
  /**
   * Search for relevant concepts.
   */
  async searchConcepts(query, k = 5) {
    const result = await this.client.execute(
      "memory.search",
      { query, k, type: "concept" }
    );
    return result.concepts ?? [];
  }
  /**
   * Store a trajectory in memory.
   */
  async store(trajectory) {
    return this.client.execute("memory.store", { trajectory });
  }
};
var SearchAPI = class {
  constructor(client) {
    this.client = client;
  }
  /**
   * Solve a task using the configured search strategy.
   */
  async solve(task) {
    return this.client.execute("search.solve", { task });
  }
};
var CognitiveCore = class {
  client;
  /**
   * Environment operations (create, reset, step, verify)
   */
  env;
  /**
   * Memory operations (search, store)
   */
  memory;
  /**
   * Search operations (solve)
   */
  search;
  constructor(options = {}) {
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
  async start() {
    await this.client.start();
  }
  /**
   * Stop the Python subprocess.
   */
  async stop() {
    await this.client.stop();
  }
  /**
   * Get the version of the Python cognitive-core package.
   */
  async version() {
    const result = await this.client.execute("version");
    return result.version;
  }
  /**
   * Check if the client is running.
   */
  get isRunning() {
    return this.client.isRunning;
  }
  /**
   * Access the underlying client for advanced usage.
   */
  get rawClient() {
    return this.client;
  }
};
var index_default = CognitiveCore;
export {
  CognitiveCore,
  CognitiveCoreClient,
  index_default as default,
  getPythonPath,
  isSetUp,
  setup
};
