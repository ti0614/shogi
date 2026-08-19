"""棋譜データの基本モデル定義。"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class PieceType(str, Enum):
    FU = "FU"  # 歩
    KY = "KY"  # 香
    KE = "KE"  # 桂
    GI = "GI"  # 銀
    KI = "KI"  # 金
    KA = "KA"  # 角
    HI = "HI"  # 飛
    OU = "OU"  # 玉/王
    TO = "TO"  # と金
    NY = "NY"  # 成香
    NK = "NK"  # 成桂
    NG = "NG"  # 成銀
    UM = "UM"  # 馬
    RY = "RY"  # 龍


# 成る前 -> 成った後
PROMOTE_MAP = {
    PieceType.FU: PieceType.TO,
    PieceType.KY: PieceType.NY,
    PieceType.KE: PieceType.NK,
    PieceType.GI: PieceType.NG,
    PieceType.KA: PieceType.UM,
    PieceType.HI: PieceType.RY,
}
DEMOTE_MAP = {v: k for k, v in PROMOTE_MAP.items()}

# 持ち駒に戻すときの基本駒種（成り駒は元に戻す）
def base_type(piece: PieceType) -> PieceType:
    return DEMOTE_MAP.get(piece, piece)


# KIF漢字表記 <-> PieceType
KIF_PIECE_NAMES = {
    PieceType.FU: "歩",
    PieceType.KY: "香",
    PieceType.KE: "桂",
    PieceType.GI: "銀",
    PieceType.KI: "金",
    PieceType.KA: "角",
    PieceType.HI: "飛",
    PieceType.OU: "玉",
    PieceType.TO: "と",
    PieceType.NY: "成香",
    PieceType.NK: "成桂",
    PieceType.NG: "成銀",
    PieceType.UM: "馬",
    PieceType.RY: "龍",
}
KIF_NAME_TO_PIECE = {}
for _pt, _name in KIF_PIECE_NAMES.items():
    KIF_NAME_TO_PIECE[_name] = _pt
# よくある別表記のゆらぎ
KIF_NAME_TO_PIECE["王"] = PieceType.OU
KIF_NAME_TO_PIECE["竜"] = PieceType.RY
KIF_NAME_TO_PIECE["全"] = PieceType.NG
KIF_NAME_TO_PIECE["圭"] = PieceType.NK
KIF_NAME_TO_PIECE["杏"] = PieceType.NY


class Side(str, Enum):
    SENTE = "SENTE"  # 先手（黒）
    GOTE = "GOTE"  # 後手（白）

    @property
    def opponent(self) -> "Side":
        return Side.GOTE if self is Side.SENTE else Side.SENTE


Square = Optional[tuple]  # (file 1-9, rank 1-9) か、打の場合 None(from)


@dataclass
class Move:
    """一手分の情報。"""

    number: int
    side: Side
    piece: PieceType
    to_sq: tuple  # (file, rank)
    from_sq: Optional[tuple]  # Noneなら打
    is_drop: bool = False
    is_promotion: bool = False
    is_same: bool = False  # 「同」（直前の指し手と同じマス）
    captured: Optional[PieceType] = None  # 実際に取った駒（盤面シミュレーションで判明）
    think_time_sec: Optional[int] = None
    total_time_sec: Optional[int] = None
    comment: str = ""
    raw: str = ""


@dataclass
class Game:
    """1局分の棋譜データ。"""

    sente_name: str = ""
    gote_name: str = ""
    handicap: str = "平手"
    moves: list = field(default_factory=list)
    result: str = ""
    headers: dict = field(default_factory=dict)

    def __len__(self) -> int:
        return len(self.moves)
