from pathlib import Path

from shogi_kifu_analyzer import parse_kif_file
from shogi_kifu_analyzer.models import PieceType, Side

SAMPLE = Path(__file__).resolve().parent.parent / "samples" / "sample_game.kif"


def test_parses_headers():
    game = parse_kif_file(SAMPLE)
    assert game.sente_name == "藤井太郎"
    assert game.gote_name == "羽生次郎"
    assert game.handicap == "平手"


def test_parses_move_count():
    game = parse_kif_file(SAMPLE)
    assert len(game.moves) == 14


def test_first_move():
    game = parse_kif_file(SAMPLE)
    m = game.moves[0]
    assert m.side is Side.SENTE
    assert m.piece is PieceType.FU
    assert m.to_sq == (7, 6)
    assert m.from_sq == (7, 7)
    assert m.think_time_sec == 9
    assert m.total_time_sec == 9


def test_same_square_move():
    game = parse_kif_file(SAMPLE)
    m = game.moves[9]  # 10手目「同　歩(23)」
    assert m.is_same is True
    assert m.to_sq == (2, 4)
    assert m.from_sq == (2, 3)


def test_drop_move():
    game = parse_kif_file(SAMPLE)
    m = game.moves[11]  # 12手目「２三歩打」
    assert m.is_drop is True
    assert m.from_sq is None
    assert m.to_sq == (2, 3)


def test_promotion_notation():
    game = parse_kif_file(SAMPLE)
    m = game.moves[12]  # 13手目「７三角成(28)」
    assert m.piece is PieceType.UM
    assert m.from_sq == (2, 8)
    assert m.to_sq == (7, 3)
