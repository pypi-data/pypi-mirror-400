/**
 * Python subprocess client for Cognitive Core.
 *
 * Manages communication with the Python cognitive-core package via JSON
 * over stdin/stdout.
 */

import { spawn, ChildProcess } from "child_process";
import { EventEmitter } from "events";
import type {
  CommandRequest,
  CommandResponse,
  CognitiveCoreOptions,
} from "./types.js";

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
export class CognitiveCoreClient extends EventEmitter {
  private process: ChildProcess | null = null;
  private buffer = "";
  private pendingRequests: Map<
    number,
    {
      resolve: (value: CommandResponse) => void;
      reject: (error: Error) => void;
      timeout: NodeJS.Timeout;
    }
  > = new Map();
  private requestId = 0;
  private options: Required<CognitiveCoreOptions>;

  constructor(options: CognitiveCoreOptions = {}) {
    super();
    this.options = {
      pythonPath: options.pythonPath ?? "python",
      cwd: options.cwd ?? process.cwd(),
      env: options.env ?? {},
      timeout: options.timeout ?? 30000,
    };
  }

  /**
   * Start the Python subprocess.
   */
  async start(): Promise<void> {
    if (this.process) {
      throw new Error("Client already started");
    }

    return new Promise((resolve, reject) => {
      this.process = spawn(
        this.options.pythonPath,
        ["-m", "cognitive_core.cli", "--json"],
        {
          cwd: this.options.cwd,
          env: { ...process.env, ...this.options.env },
          stdio: ["pipe", "pipe", "pipe"],
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

      this.process.stdout?.on("data", (data: Buffer) => {
        this.handleData(data.toString());
      });

      this.process.stderr?.on("data", (data: Buffer) => {
        this.emit("stderr", data.toString());
      });

      // Give the process a moment to start, then verify it's running
      setTimeout(async () => {
        try {
          const response = await this.execute<{ version: string }>("version");
          if (response.version) {
            this.emit("ready", response);
            resolve();
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
  async stop(): Promise<void> {
    if (!this.process) {
      return;
    }

    return new Promise((resolve) => {
      if (this.process) {
        this.process.once("exit", () => {
          this.cleanup();
          resolve();
        });

        this.process.stdin?.end();
        this.process.kill("SIGTERM");

        // Force kill after timeout
        setTimeout(() => {
          if (this.process) {
            this.process.kill("SIGKILL");
          }
          resolve();
        }, 5000);
      } else {
        resolve();
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
  async execute<T = unknown>(
    command: string,
    args: Record<string, unknown> = {}
  ): Promise<T> {
    if (!this.process?.stdin) {
      throw new Error("Client not started. Call start() first.");
    }

    const request: CommandRequest = { command, args };
    const response = await this.sendRequest(request);

    if (!response.success) {
      throw new Error(response.error ?? "Unknown error");
    }

    return response.result as T;
  }

  /**
   * Check if the client is running.
   */
  get isRunning(): boolean {
    return this.process !== null && !this.process.killed;
  }

  private sendRequest(request: CommandRequest): Promise<CommandResponse> {
    return new Promise((resolve, reject) => {
      const id = this.requestId++;
      const json = JSON.stringify(request);

      const timeout = setTimeout(() => {
        this.pendingRequests.delete(id);
        reject(new Error(`Command timed out: ${request.command}`));
      }, this.options.timeout);

      this.pendingRequests.set(id, { resolve, reject, timeout });

      this.process?.stdin?.write(json + "\n");
    });
  }

  private handleData(data: string): void {
    this.buffer += data;

    // Process complete lines
    const lines = this.buffer.split("\n");
    this.buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (line.trim()) {
        try {
          const response = JSON.parse(line) as CommandResponse;
          this.handleResponse(response);
        } catch (error) {
          this.emit("parseError", { line, error });
        }
      }
    }
  }

  private handleResponse(response: CommandResponse): void {
    // For simplicity, we resolve the oldest pending request
    // A more robust implementation would use request IDs
    const [id, pending] = this.pendingRequests.entries().next().value ?? [
      null,
      null,
    ];

    if (id !== null && pending) {
      clearTimeout(pending.timeout);
      this.pendingRequests.delete(id);
      pending.resolve(response);
    }
  }

  private cleanup(): void {
    // Reject all pending requests
    for (const [id, pending] of this.pendingRequests) {
      clearTimeout(pending.timeout);
      pending.reject(new Error("Process terminated"));
    }
    this.pendingRequests.clear();
    this.process = null;
    this.buffer = "";
  }
}
