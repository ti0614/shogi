export interface BestMoveResult {
  bestmove: string;
  scoreCp?: number;
  scoreMate?: number;
}

export class Engine {
  private worker: Worker;
  readonly ready: Promise<void>;
  private onLine?: (line: string) => void;

  constructor(workerUrl: string) {
    this.worker = new Worker(workerUrl);
    this.ready = new Promise((resolveReady) => {
      this.worker.onmessage = (e: MessageEvent<string>) => {
        const line = e.data;
        if (line === "__engine_ready__") {
          this.worker.postMessage("usi");
          return;
        }
        if (line === "usiok") {
          this.worker.postMessage("isready");
          return;
        }
        if (line === "readyok") {
          resolveReady();
          return;
        }
        this.onLine?.(line);
      };
    });
  }

  bestMove(sfen: string, movetimeMs: number): Promise<BestMoveResult> {
    return new Promise((resolve) => {
      let scoreCp: number | undefined;
      let scoreMate: number | undefined;

      this.onLine = (line) => {
        const cpMatch = line.match(/score cp (-?\d+)/);
        if (cpMatch) scoreCp = Number(cpMatch[1]);
        const mateMatch = line.match(/score mate (-?\d+)/);
        if (mateMatch) scoreMate = Number(mateMatch[1]);

        if (line.startsWith("bestmove")) {
          const bestmove = line.split(" ")[1];
          this.onLine = undefined;
          resolve({ bestmove, scoreCp, scoreMate });
        }
      };

      this.worker.postMessage(`position sfen ${sfen}`);
      this.worker.postMessage(`go movetime ${movetimeMs}`);
    });
  }

  newGame(): void {
    this.worker.postMessage("usinewgame");
  }
}
