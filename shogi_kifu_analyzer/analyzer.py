"""棋譜の統計分析。"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import List, Optional

from .board import Board
from .models import Game, PieceType, Side

# 駒の簡易点数評価（一般的な目安値。玉は評価対象外）
PIECE_VALUES = {
    PieceType.FU: 1,
    PieceType.KY: 3,
    PieceType.KE: 3,
    PieceType.GI: 5,
    PieceType.KI: 6,
    PieceType.KA: 8,
    PieceType.HI: 10,
    PieceType.TO: 6,
    PieceType.NY: 6,
    PieceType.NK: 6,
    PieceType.NG: 6,
    PieceType.UM: 10,
    PieceType.RY: 12,
    PieceType.OU: 0,
}


@dataclass
class SideStats:
    move_count: int = 0
    capture_count: int = 0
    promotion_count: int = 0
    drop_count: int = 0
    total_think_time_sec: int = 0
    max_think_time_sec: int = 0
    max_think_time_move: Optional[int] = None
    piece_move_counts: Counter = field(default_factory=Counter)
    captured_piece_counts: Counter = field(default_factory=Counter)

    @property
    def avg_think_time_sec(self) -> float:
        if self.move_count == 0:
            return 0.0
        return self.total_think_time_sec / self.move_count


@dataclass
class GameStats:
    total_moves: int = 0
    sente: SideStats = field(default_factory=SideStats)
    gote: SideStats = field(default_factory=SideStats)
    material_balance_final: int = 0  # 正なら先手有利（駒の点数差）
    winner: Optional[Side] = None
    result_reason: str = ""
    opening_moves: List[str] = field(default_factory=list)

    def side_stats(self, side: Side) -> SideStats:
        return self.sente if side is Side.SENTE else self.gote

    def to_dict(self) -> dict:
        def side_dict(s: SideStats) -> dict:
            return {
                "move_count": s.move_count,
                "capture_count": s.capture_count,
                "promotion_count": s.promotion_count,
                "drop_count": s.drop_count,
                "avg_think_time_sec": round(s.avg_think_time_sec, 2),
                "max_think_time_sec": s.max_think_time_sec,
                "max_think_time_move": s.max_think_time_move,
                "piece_move_counts": dict(s.piece_move_counts),
                "captured_piece_counts": dict(s.captured_piece_counts),
            }

        return {
            "total_moves": self.total_moves,
            "sente": side_dict(self.sente),
            "gote": side_dict(self.gote),
            "material_balance_final": self.material_balance_final,
            "winner": self.winner.value if self.winner else None,
            "result_reason": self.result_reason,
            "opening_moves": self.opening_moves,
        }


def _infer_result(game: Game) -> tuple:
    result = (game.result or "").strip()
    if not result:
        return None, ""
    if "先手の勝ち" in result:
        return Side.SENTE, result
    if "後手の勝ち" in result:
        return Side.GOTE, result
    # CSAの結果表記（%TORYOなど）は、それ単独では勝者を特定できないため
    # 理由のみ記録する。
    return None, result


class GameAnalyzer:
    """1局分の棋譜を解析し、GameStats を生成する。"""

    def __init__(self, opening_move_count: int = 10) -> None:
        self.opening_move_count = opening_move_count

    def analyze(self, game: Game) -> GameStats:
        board = Board(handicap=game.handicap)
        stats = GameStats(total_moves=len(game.moves))

        for move in game.moves:
            board.apply_move(move)
            side_stats = stats.side_stats(move.side)

            side_stats.move_count += 1
            side_stats.piece_move_counts[move.piece.value] += 1
            if move.is_drop:
                side_stats.drop_count += 1
            if move.is_promotion:
                side_stats.promotion_count += 1
            if move.captured is not None:
                side_stats.capture_count += 1
                side_stats.captured_piece_counts[move.captured.value] += 1

            if move.think_time_sec is not None:
                side_stats.total_think_time_sec += move.think_time_sec
                if move.think_time_sec > side_stats.max_think_time_sec:
                    side_stats.max_think_time_sec = move.think_time_sec
                    side_stats.max_think_time_move = move.number

        stats.material_balance_final = self._material_balance(board)
        stats.winner, stats.result_reason = _infer_result(game)
        stats.opening_moves = [
            _move_to_text(m) for m in game.moves[: self.opening_move_count]
        ]
        return stats

    @staticmethod
    def _material_balance(board: Board) -> int:
        total = 0
        for side, piece in board.squares.values():
            value = PIECE_VALUES.get(piece, 0)
            total += value if side is Side.SENTE else -value
        for piece, count in board.hands[Side.SENTE].items():
            total += PIECE_VALUES.get(piece, 0) * count
        for piece, count in board.hands[Side.GOTE].items():
            total -= PIECE_VALUES.get(piece, 0) * count
        return total


_FILE_KANJI = "１２３４５６７８９"
_RANK_KANJI = "一二三四五六七八九"


def _move_to_text(move) -> str:
    side_mark = "▲" if move.side is Side.SENTE else "△"
    if move.is_same:
        dest = "同"
    else:
        f, r = move.to_sq
        dest = f"{_FILE_KANJI[f - 1]}{_RANK_KANJI[r - 1]}"
    promo = "成" if move.is_promotion else ""
    drop = "打" if move.is_drop else ""
    return f"{side_mark}{dest}{move.piece.value}{promo}{drop}"
