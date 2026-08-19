// SFENの盤面部分をパースして描画するための最小限のユーティリティ。
// (エンジン動作確認がこのデモの主眼なので、盤面は表示専用・操作不可)

const KANJI: Record<string, string> = {
  P: "歩", L: "香", N: "桂", S: "銀", G: "金", B: "角", R: "飛", K: "王",
  "+P": "と", "+L": "成香", "+N": "成桂", "+S": "成銀", "+B": "馬", "+R": "龍",
};

export interface BoardPiece {
  file: number; // 1-9 (右から左)
  rank: number; // 1-9 (上から下)
  sente: boolean;
  kanji: string;
}

export function parseSfenBoard(sfen: string): BoardPiece[] {
  const boardPart = sfen.trim().split(" ")[0];
  const rows = boardPart.split("/");
  const pieces: BoardPiece[] = [];

  rows.forEach((row, rowIdx) => {
    const rank = rowIdx + 1;
    let file = 9;
    let i = 0;
    while (i < row.length) {
      const ch = row[i];
      if (/\d/.test(ch)) {
        file -= Number(ch);
        i += 1;
        continue;
      }
      let code = ch;
      if (ch === "+") {
        code = "+" + row[i + 1];
        i += 2;
      } else {
        i += 1;
      }
      const sente = code === code.toUpperCase();
      const kanji = KANJI[code.toUpperCase()] ?? "?";
      pieces.push({ file, rank, sente, kanji });
      file -= 1;
    }
  });

  return pieces;
}

export function renderBoard(container: HTMLElement, sfen: string): void {
  const pieces = parseSfenBoard(sfen);
  const byKey = new Map(pieces.map((p) => [`${p.file},${p.rank}`, p]));

  container.innerHTML = "";
  container.className = "board";
  for (let rank = 1; rank <= 9; rank++) {
    for (let file = 9; file >= 1; file--) {
      const sq = document.createElement("div");
      sq.className = "square";
      const piece = byKey.get(`${file},${rank}`);
      if (piece) {
        const p = document.createElement("div");
        p.className = "piece" + (piece.sente ? "" : " gote");
        p.textContent = piece.kanji;
        sq.appendChild(p);
      }
      container.appendChild(sq);
    }
  }
}
