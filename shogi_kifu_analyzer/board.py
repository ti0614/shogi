"""簡易将棋盤シミュレーター。

指し手を1手ずつ適用し、駒の位置・持ち駒・取られた駒を追跡する。
合法手判定などのルールチェックは行わず、棋譜に書かれた指し手をそのまま反映する
（分析用途に割り切った実装）。
"""

from __future__ import annotations

from collections import Counter
from typing import Dict, Optional, Tuple

from .models import PROMOTE_MAP, Move, PieceType, Side, base_type

SENTE_PROMOTION_RANKS = {1, 2, 3}
GOTE_PROMOTION_RANKS = {7, 8, 9}

_INITIAL_LAYOUT = {
    Side.SENTE: {
        (1, 9): PieceType.KY, (2, 9): PieceType.KE, (3, 9): PieceType.GI,
        (4, 9): PieceType.KI, (5, 9): PieceType.OU, (6, 9): PieceType.KI,
        (7, 9): PieceType.GI, (8, 9): PieceType.KE, (9, 9): PieceType.KY,
        (8, 8): PieceType.HI, (2, 8): PieceType.KA,
        **{(f, 7): PieceType.FU for f in range(1, 10)},
    },
    Side.GOTE: {
        (1, 1): PieceType.KY, (2, 1): PieceType.KE, (3, 1): PieceType.GI,
        (4, 1): PieceType.KI, (5, 1): PieceType.OU, (6, 1): PieceType.KI,
        (7, 1): PieceType.GI, (8, 1): PieceType.KE, (9, 1): PieceType.KY,
        (2, 2): PieceType.HI, (8, 2): PieceType.KA,
        **{(f, 3): PieceType.FU for f in range(1, 10)},
    },
}


class Board:
    def __init__(self, handicap: str = "平手") -> None:
        self.squares: Dict[Tuple[int, int], Tuple[Side, PieceType]] = {}
        self.hands: Dict[Side, Counter] = {Side.SENTE: Counter(), Side.GOTE: Counter()}
        self._setup(handicap)

    def _setup(self, handicap: str) -> None:
        # 駒落ちは平手を基本にして上手（後手）側の駒を間引く簡易対応。
        for side, layout in _INITIAL_LAYOUT.items():
            for sq, piece in layout.items():
                self.squares[sq] = (side, piece)
        if handicap and handicap not in ("平手", ""):
            self._apply_handicap(handicap)

    def _apply_handicap(self, handicap: str) -> None:
        removal_map = {
            "香落ち": [(1, 1)],
            "右香落ち": [(9, 1)],
            "角落ち": [(8, 2)],
            "飛車落ち": [(2, 2)],
            "飛香落ち": [(2, 2), (1, 1)],
            "二枚落ち": [(2, 2), (8, 2)],
            "三枚落ち": [(2, 2), (8, 2), (1, 1)],
            "四枚落ち": [(2, 2), (8, 2), (1, 1), (9, 1)],
            "六枚落ち": [(2, 2), (8, 2), (1, 1), (9, 1), (2, 1), (8, 1)],
        }
        for sq in removal_map.get(handicap, []):
            self.squares.pop(sq, None)

    def piece_at(self, sq: Tuple[int, int]) -> Optional[Tuple[Side, PieceType]]:
        return self.squares.get(sq)

    def apply_move(self, move: Move) -> None:
        """指し手を盤面に反映し、move.captured を埋める。"""
        if move.is_drop:
            self.squares[move.to_sq] = (move.side, move.piece)
            hand = self.hands[move.side]
            key = base_type(move.piece)
            if hand[key] > 0:
                hand[key] -= 1
            return

        # 移動元の駒種と比較して「成り」を判定する（KIF/CSAどちらの棋譜でも
        # move.piece は移動後の最終的な駒種を表すため、これで一意に判定できる）。
        origin = self.squares.get(move.from_sq) if move.from_sq is not None else None
        if origin is not None and PROMOTE_MAP.get(origin[1]) == move.piece:
            move.is_promotion = True

        existing = self.squares.get(move.to_sq)
        if existing is not None and existing[0] != move.side:
            captured_type = existing[1]
            move.captured = captured_type
            self.hands[move.side][base_type(captured_type)] += 1

        if move.from_sq is not None:
            self.squares.pop(move.from_sq, None)

        self.squares[move.to_sq] = (move.side, move.piece)

    @staticmethod
    def is_promotion_zone(side: Side, rank: int) -> bool:
        if side is Side.SENTE:
            return rank in SENTE_PROMOTION_RANKS
        return rank in GOTE_PROMOTION_RANKS
