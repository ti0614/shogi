import "./style.css";
import { Shogiground } from "shogiground";
import type { Config } from "shogiground/config";
import type { Key } from "shogiground/types";
import type { MoveOrDrop } from "shogiops/types";
import { parseSquareName } from "shogiops/util";
import type { Shogi } from "shogiops/variant/shogi";
import { Engine } from "./engine";
import {
  PROMOTES_TO,
  UNPROMOTES_TO,
  createInitialPosition,
  dropDests,
  isPromotable,
  moveDests,
  sfenOf,
} from "./game";

const THINK_TIME_MS = 2000;

const app = document.querySelector<HTMLDivElement>("#app")!;
app.innerHTML = `
  <h1>将棋対局デモ（あなた: 先手 / エンジン: 後手）</h1>
  <p class="sub">
    盤面UIは <a href="https://github.com/WandererXII/shogiground" target="_blank" rel="noopener">shogiground</a>、
    ルール処理は <a href="https://github.com/WandererXII/shogiops" target="_blank" rel="noopener">shogiops</a>、
    思考エンジンは やねうら王(WASM版) を使用しています（すべてOSS）。
  </p>

  <div class="wrap">
    <div id="hand-top" class="sg-hand-wrap"></div>
    <div id="board-wrap" class="main-board">
      <div id="board" class="sg-wrap"></div>
    </div>
    <div id="hand-bottom" class="sg-hand-wrap"></div>
  </div>

  <div class="controls">
    <button id="resetBtn">対局をリセット</button>
    <span id="status">エンジン起動中…</span>
  </div>
`;

const boardEl = document.querySelector<HTMLDivElement>("#board")!;
const handTopEl = document.querySelector<HTMLDivElement>("#hand-top")!;
const handBottomEl = document.querySelector<HTMLDivElement>("#hand-bottom")!;
const statusEl = document.querySelector<HTMLSpanElement>("#status")!;
const resetBtn = document.querySelector<HTMLButtonElement>("#resetBtn")!;

const engine = new Engine(`${import.meta.env.BASE_URL}engine/engine-worker.js`);

let pos: Shogi = createInitialPosition();
let gameOver = false;
let engineThinking = false;

function rankLetterToNumber(key: Key): number {
  return key.charCodeAt(key.length - 1) - "a".charCodeAt(0) + 1;
}

function inPromotionZone(color: "sente" | "gote", key: Key): boolean {
  const rank = rankLetterToNumber(key);
  return color === "sente" ? rank <= 3 : rank >= 7;
}

function roleAt(key: Key): string | undefined {
  const sq = parseSquareName(key);
  return pos.board.get(sq)?.role;
}

function movePromotionDialog(orig: Key, dest: Key): boolean {
  const role = roleAt(orig);
  if (!role || !isPromotable(role)) return false;
  return inPromotionZone(pos.turn, orig) || inPromotionZone(pos.turn, dest);
}

function forceMovePromotion(orig: Key, dest: Key): boolean {
  const role = roleAt(orig);
  if (!role) return false;
  const destRank = rankLetterToNumber(dest);
  const lastRank = pos.turn === "sente" ? 1 : 9;
  const lastTwoRanks = pos.turn === "sente" ? [1, 2] : [8, 9];
  if ((role === "pawn" || role === "lance") && destRank === lastRank) return true;
  if (role === "knight" && lastTwoRanks.includes(destRank)) return true;
  return false;
}

const sg = Shogiground(
  {
    activeColor: "sente",
    orientation: "sente",
    highlight: { lastDests: true, check: true },
    animation: { enabled: true },
    draggable: { enabled: true, showGhost: true },
    selectable: { enabled: true },
    promotion: {
      promotesTo: (role) => PROMOTES_TO[role],
      unpromotesTo: (role) => UNPROMOTES_TO[role],
      movePromotionDialog,
      forceMovePromotion,
      dropPromotionDialog: () => false,
    },
    movable: {
      free: false,
      dests: moveDests(pos),
      events: { after: onUserMove },
    },
    droppable: {
      free: false,
      dests: dropDests(pos),
      events: { after: onUserDrop },
    },
  } satisfies Config,
  { board: boardEl, hands: { top: handTopEl, bottom: handBottomEl } },
);

function refreshBoard(): void {
  sg.set({
    sfen: { board: sfenOf(pos).split(" ")[0], hands: sfenOf(pos).split(" ")[2] },
    turnColor: pos.turn,
    activeColor: gameOver ? undefined : pos.turn,
    checks: pos.isCheck(),
    movable: { dests: moveDests(pos) },
    droppable: { dests: dropDests(pos) },
  });
}

function checkGameEnd(): boolean {
  const outcome = pos.outcome();
  if (!outcome) return false;
  gameOver = true;
  const winnerText =
    outcome.winner === "sente" ? "先手(あなた)の勝ち" : outcome.winner === "gote" ? "後手(エンジン)の勝ち" : "引き分け";
  statusEl.textContent = `対局終了: ${outcome.result} — ${winnerText}`;
  sg.set({ activeColor: undefined });
  return true;
}

async function applyMoveOrDrop(md: MoveOrDrop): Promise<void> {
  pos = pos.clone();
  pos.play(md);
  refreshBoard();
}

async function onUserMove(orig: Key, dest: Key, prom: boolean): Promise<void> {
  if (gameOver || engineThinking || pos.turn !== "sente") return;
  await applyMoveOrDrop({
    from: parseSquareName(orig),
    to: parseSquareName(dest),
    promotion: prom,
  });
  await afterHumanPly();
}

async function onUserDrop(piece: { color: string; role: string }, key: Key): Promise<void> {
  if (gameOver || engineThinking || pos.turn !== "sente") return;
  await applyMoveOrDrop({ role: piece.role as never, to: parseSquareName(key) });
  await afterHumanPly();
}

async function afterHumanPly(): Promise<void> {
  if (checkGameEnd()) return;
  await requestEngineMove();
}

async function requestEngineMove(): Promise<void> {
  engineThinking = true;
  statusEl.textContent = "エンジン思考中…";
  sg.set({ activeColor: undefined });

  const { bestmove, scoreCp, scoreMate } = await engine.bestMove(sfenOf(pos), THINK_TIME_MS);
  engineThinking = false;

  if (bestmove === "resign" || bestmove === "win") {
    gameOver = true;
    statusEl.textContent = bestmove === "resign" ? "エンジンが投了しました。あなたの勝ちです。" : "エンジンの勝ちです。";
    return;
  }

  await applyMoveOrDrop(parseUsiOrThrow(bestmove));

  if (checkGameEnd()) return;

  const scoreText =
    scoreMate !== undefined ? `詰み ${scoreMate}手` : scoreCp !== undefined ? `評価値 ${scoreCp}` : "";
  statusEl.textContent = `あなたの番です（${scoreText} / 直前の手: ${bestmove}）`;
  sg.set({ activeColor: "sente" });
}

function parseUsiOrThrow(usi: string): MoveOrDrop {
  // '*' を含むUSI表記（打つ手, 例: "P*5e"）と通常手("7g7f"/"8h2b+")の両方に対応
  if (usi.includes("*")) {
    const [roleChar, toStr] = usi.split("*");
    const roleMap: Record<string, string> = {
      P: "pawn",
      L: "lance",
      N: "knight",
      S: "silver",
      G: "gold",
      B: "bishop",
      R: "rook",
    };
    return { role: roleMap[roleChar] as never, to: parseSquareName(toStr as Key) };
  }
  const promotion = usi.endsWith("+");
  const body = promotion ? usi.slice(0, -1) : usi;
  const from = body.slice(0, 2) as Key;
  const to = body.slice(2, 4) as Key;
  return { from: parseSquareName(from), to: parseSquareName(to), promotion };
}

resetBtn.addEventListener("click", () => {
  pos = createInitialPosition();
  gameOver = false;
  engineThinking = false;
  engine.newGame();
  refreshBoard();
  statusEl.textContent = "あなたの番です（先手）";
});

engine.ready.then(() => {
  engine.newGame();
  refreshBoard();
  statusEl.textContent = "あなたの番です（先手）";
});
