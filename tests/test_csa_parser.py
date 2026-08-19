from pathlib import Path

from shogi_kifu_analyzer import parse_csa_file
from shogi_kifu_analyzer.models import PieceType, Side

SAMPLE = Path(__file__).resolve().parent.parent / "samples" / "sample_game.csa"


def test_parses_headers():
    game = parse_csa_file(SAMPLE)
    assert game.sente_name == "藤井太郎"
    assert game.gote_name == "羽生次郎"


def test_parses_move_count():
    game = parse_csa_file(SAMPLE)
    assert len(game.moves) == 14


def test_first_move():
    game = parse_csa_file(SAMPLE)
    m = game.moves[0]
    assert m.side is Side.SENTE
    assert m.piece is PieceType.FU
    assert m.from_sq == (7, 7)
    assert m.to_sq == (7, 6)
    assert m.think_time_sec == 9


def test_drop_move():
    game = parse_csa_file(SAMPLE)
    m = game.moves[11]
    assert m.is_drop is True
    assert m.from_sq is None
    assert m.to_sq == (2, 3)


def test_promoted_piece_code():
    game = parse_csa_file(SAMPLE)
    m = game.moves[12]
    assert m.piece is PieceType.UM
    assert m.from_sq == (2, 8)
    assert m.to_sq == (7, 3)


def test_result():
    game = parse_csa_file(SAMPLE)
    assert game.result == "%CHUDAN"
