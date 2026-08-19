from pathlib import Path

from shogi_kifu_analyzer import GameAnalyzer, parse_kif_file, parse_csa_file
from shogi_kifu_analyzer.models import PieceType, Side

SAMPLE_KIF = Path(__file__).resolve().parent.parent / "samples" / "sample_game.kif"
SAMPLE_CSA = Path(__file__).resolve().parent.parent / "samples" / "sample_game.csa"


def test_capture_and_promotion_tracked_from_kif():
    game = parse_kif_file(SAMPLE_KIF)
    stats = GameAnalyzer().analyze(game)

    assert stats.total_moves == 14
    # 10手目: 後手が２四で先手歩を取る
    assert stats.gote.capture_count == 2  # 10手目と14手目
    assert stats.gote.captured_piece_counts["FU"] == 1
    assert stats.gote.captured_piece_counts["UM"] == 1
    # 13手目: 先手の角が成って角(馬)で駒を取る
    assert stats.sente.capture_count == 1
    assert stats.sente.captured_piece_counts["FU"] == 1
    assert stats.sente.promotion_count == 1
    assert stats.sente.drop_count == 0
    assert stats.gote.drop_count == 1


def test_kif_and_csa_produce_same_stats():
    kif_stats = GameAnalyzer().analyze(parse_kif_file(SAMPLE_KIF))
    csa_stats = GameAnalyzer().analyze(parse_csa_file(SAMPLE_CSA))

    assert kif_stats.sente.capture_count == csa_stats.sente.capture_count
    assert kif_stats.gote.capture_count == csa_stats.gote.capture_count
    assert kif_stats.sente.promotion_count == csa_stats.sente.promotion_count
    assert kif_stats.material_balance_final == csa_stats.material_balance_final


def test_think_time_stats():
    game = parse_kif_file(SAMPLE_KIF)
    stats = GameAnalyzer().analyze(game)
    assert stats.sente.max_think_time_sec == 12
    assert stats.sente.max_think_time_move == 13


def test_to_dict_is_json_serializable():
    import json

    game = parse_kif_file(SAMPLE_KIF)
    stats = GameAnalyzer().analyze(game)
    data = stats.to_dict()
    json.dumps(data, ensure_ascii=False)  # 例外が出なければOK
    assert data["total_moves"] == 14
