import "./style.css";
import { renderBoard } from "./sfenBoard";

const STARTPOS_SFEN = "lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b - 1";

const app = document.querySelector<HTMLDivElement>("#app")!;
app.innerHTML = `
  <h1>将棋エンジン(WASM)デモ</h1>
  <p class="sub">やねうら王のWebAssembly版をブラウザ内で動かし、局面(SFEN)から最善手を求めます。</p>

  <div id="board"></div>

  <label for="sfen">局面(SFEN)</label>
  <textarea id="sfen" rows="2">${STARTPOS_SFEN}</textarea>

  <div class="controls">
    <button id="applyBtn">この局面を表示</button>
    <button id="thinkBtn" disabled>思考する (2秒)</button>
    <span id="status">エンジン起動中…</span>
  </div>

  <pre id="log"></pre>
`;

const boardEl = document.querySelector<HTMLDivElement>("#board")!;
const sfenEl = document.querySelector<HTMLTextAreaElement>("#sfen")!;
const applyBtn = document.querySelector<HTMLButtonElement>("#applyBtn")!;
const thinkBtn = document.querySelector<HTMLButtonElement>("#thinkBtn")!;
const statusEl = document.querySelector<HTMLSpanElement>("#status")!;
const logEl = document.querySelector<HTMLPreElement>("#log")!;

renderBoard(boardEl, STARTPOS_SFEN);

applyBtn.addEventListener("click", () => {
  renderBoard(boardEl, sfenEl.value);
});

function log(line: string): void {
  logEl.textContent += line + "\n";
  logEl.scrollTop = logEl.scrollHeight;
}

const worker = new Worker("/engine/engine-worker.js");

let ready = false;

worker.onmessage = (e: MessageEvent<string>) => {
  const line = e.data;

  if (line === "__engine_ready__") {
    worker.postMessage("usi");
    return;
  }

  log(line);

  if (line === "usiok") {
    worker.postMessage("isready");
    return;
  }
  if (line === "readyok") {
    ready = true;
    thinkBtn.disabled = false;
    statusEl.textContent = "準備完了";
    return;
  }
  if (line.startsWith("bestmove")) {
    statusEl.textContent = "思考完了: " + line;
    thinkBtn.disabled = false;
  }
};

thinkBtn.addEventListener("click", () => {
  if (!ready) return;
  logEl.textContent = "";
  thinkBtn.disabled = true;
  statusEl.textContent = "思考中…";
  worker.postMessage(`position sfen ${sfenEl.value.trim()}`);
  worker.postMessage("go movetime 2000");
});
