"""KIF形式（柿木形式）の棋譜パーサー。"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from .models import Game, Move, Side, KIF_NAME_TO_PIECE, PROMOTE_MAP

_ZENKAKU_DIGITS = "０１２３４５６７８９"
_KANJI_NUM = "〇一二三四五六七八九"

# 長い表記から先にマッチさせる（「成香」を「香」より先に判定するため）
_PIECE_NAMES_SORTED = sorted(KIF_NAME_TO_PIECE.keys(), key=len, reverse=True)

_MOVE_LINE_RE = re.compile(
    r"^\s*(?P<num>\d+)\s+(?P<body>\S+)(?:\s+\(\s*(?P<think>[\d:]+)\s*/\s*(?P<total>[\d:]+)\s*\))?"
)
_HEADER_RE = re.compile(r"^([^：:]+)[：:](.*)$")


def _coord_to_int(ch: str) -> int:
    if ch in _ZENKAKU_DIGITS:
        return _ZENKAKU_DIGITS.index(ch)
    if ch in _KANJI_NUM:
        return _KANJI_NUM.index(ch)
    if ch.isdigit():
        return int(ch)
    raise ValueError(f"不明な座標文字: {ch!r}")


def _parse_time(s: Optional[str]) -> Optional[int]:
    if not s:
        return None
    parts = [int(p) for p in s.strip().split(":") if p != ""]
    sec = 0
    for p in parts:
        sec = sec * 60 + p
    return sec


def _match_piece_name(text: str) -> tuple:
    for name in _PIECE_NAMES_SORTED:
        if text.startswith(name):
            return name, KIF_NAME_TO_PIECE[name]
    raise ValueError(f"駒名を認識できません: {text!r}")


def _parse_move_body(body: str, prev_to_sq: Optional[tuple]) -> dict:
    is_same = body.startswith("同")
    if is_same:
        if prev_to_sq is None:
            raise ValueError("「同」の対象となる直前の指し手がありません")
        to_sq = prev_to_sq
        rest = body[1:]
        rest = rest.lstrip("　 ")
    else:
        file_num = _coord_to_int(body[0])
        rank_num = _coord_to_int(body[1])
        to_sq = (file_num, rank_num)
        rest = body[2:]

    piece_name, piece_type = _match_piece_name(rest)
    rest = rest[len(piece_name):]

    is_promotion = rest.startswith("成")
    if is_promotion:
        rest = rest[1:]
        piece_type = PROMOTE_MAP.get(piece_type, piece_type)

    is_drop = False
    from_sq = None
    if rest.startswith("打"):
        is_drop = True
    else:
        m = re.match(r"\((\d)(\d)\)", rest)
        if m:
            from_sq = (int(m.group(1)), int(m.group(2)))

    return dict(
        to_sq=to_sq,
        piece=piece_type,
        is_promotion=is_promotion,
        is_drop=is_drop,
        from_sq=from_sq,
        is_same=is_same,
    )


def parse_kif(text: str) -> Game:
    game = Game()
    prev_to_sq: Optional[tuple] = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip("\n").strip()
        if not line:
            continue
        # 「同　歩(23)」のように全角スペースが挟まる表記を正規化しておく
        # （そのままだと \S+ の指し手本体マッチが途中で切れてしまうため）。
        line = line.replace("　", "")
        if line.startswith("*"):
            if game.moves:
                game.moves[-1].comment += line[1:].strip() + "\n"
            continue
        if line.startswith("#"):
            continue
        if line.startswith("手数"):
            continue
        if line.startswith("まで"):
            game.result = line
            continue

        m = _MOVE_LINE_RE.match(line)
        if m:
            try:
                parsed = _parse_move_body(m.group("body"), prev_to_sq)
            except ValueError:
                continue
            number = int(m.group("num"))
            side = Side.SENTE if number % 2 == 1 else Side.GOTE
            move = Move(
                number=number,
                side=side,
                piece=parsed["piece"],
                to_sq=parsed["to_sq"],
                from_sq=parsed["from_sq"],
                is_drop=parsed["is_drop"],
                is_promotion=parsed["is_promotion"],
                is_same=parsed["is_same"],
                think_time_sec=_parse_time(m.group("think")),
                total_time_sec=_parse_time(m.group("total")),
                raw=line,
            )
            game.moves.append(move)
            prev_to_sq = move.to_sq
            continue

        hm = _HEADER_RE.match(line)
        if hm:
            key, val = hm.group(1).strip(), hm.group(2).strip()
            if key in ("先手", "下手"):
                game.sente_name = val
            elif key in ("後手", "上手"):
                game.gote_name = val
            elif key == "手合割":
                game.handicap = val
            else:
                game.headers[key] = val

    return game


def parse_kif_file(path) -> Game:
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
    return parse_kif(text)
