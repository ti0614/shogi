"""CSA形式の棋譜パーサー。"""

from __future__ import annotations

import re
from pathlib import Path

from .models import Game, Move, PieceType, Side

_MOVE_RE = re.compile(r"^([+-])(\d)(\d)(\d)(\d)([A-Z]{2})$")


def parse_csa(text: str) -> Game:
    game = Game()

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("N+"):
            game.sente_name = line[2:].strip()
            continue
        if line.startswith("N-"):
            game.gote_name = line[2:].strip()
            continue
        if line.startswith("T"):
            rest = line[1:]
            if rest.lstrip("-").isdigit() and game.moves:
                game.moves[-1].think_time_sec = int(rest)
            continue
        if line.startswith("%"):
            game.result = line
            continue
        if line[0] in "+-":
            m = _MOVE_RE.match(line)
            if not m:
                continue
            sign, f1, r1, f2, r2, piece_code = m.groups()
            side = Side.SENTE if sign == "+" else Side.GOTE
            from_sq = None if (f1 == "0" and r1 == "0") else (int(f1), int(r1))
            to_sq = (int(f2), int(r2))
            try:
                piece = PieceType(piece_code)
            except ValueError:
                continue
            number = len(game.moves) + 1
            move = Move(
                number=number,
                side=side,
                piece=piece,
                to_sq=to_sq,
                from_sq=from_sq,
                is_drop=from_sq is None,
                raw=line,
            )
            game.moves.append(move)
            continue
        # ヘッダ行（V2.2, PI, P1..P9, $EVENT: 等）はそのまま保持しておく
        if ":" in line:
            key, _, val = line.partition(":")
            game.headers[key.strip()] = val.strip()
        else:
            game.headers.setdefault("_lines", []).append(line)

    return game


def parse_csa_file(path) -> Game:
    p = Path(path)
    data = p.read_bytes()
    for encoding in ("utf-8-sig", "cp932", "shift_jis"):
        try:
            text = data.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        text = data.decode("utf-8", errors="replace")
    return parse_csa(text)
