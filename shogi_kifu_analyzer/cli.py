"""CLI: 棋譜ファイルを解析して結果を表示する。

使い方:
    python -m shogi_kifu_analyzer path/to/game.kif
    python -m shogi_kifu_analyzer path/to/game.csa --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .analyzer import GameAnalyzer
from .csa_parser import parse_csa_file
from .kif_parser import parse_kif_file


def _load_game(path: Path):
    suffix = path.suffix.lower()
    if suffix == ".csa":
        return parse_csa_file(path)
    return parse_kif_file(path)


def _print_report(game, stats) -> None:
    print(f"先手: {game.sente_name or '(不明)'}")
    print(f"後手: {game.gote_name or '(不明)'}")
    print(f"手合割: {game.handicap}")
    print(f"総手数: {stats.total_moves}")
    print()
    for label, side_stats in (("先手", stats.sente), ("後手", stats.gote)):
        print(f"--- {label} ---")
        print(f"  指し手数: {side_stats.move_count}")
        print(f"  駒取り数: {side_stats.capture_count}")
        print(f"  成り数:   {side_stats.promotion_count}")
        print(f"  打った数: {side_stats.drop_count}")
        print(f"  平均消費時間: {side_stats.avg_think_time_sec:.1f}秒")
        if side_stats.max_think_time_move is not None:
            print(
                f"  最大消費時間: {side_stats.max_think_time_sec}秒 "
                f"(第{side_stats.max_think_time_move}手)"
            )
        print()
    print(f"最終盤面の駒得点差（正=先手有利）: {stats.material_balance_final}")
    if stats.result_reason:
        print(f"結果: {stats.result_reason}")
    print()
    print("序盤の指し手:")
    print(" ".join(stats.opening_moves))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="将棋の棋譜(KIF/CSA)を解析する")
    parser.add_argument("kifu_file", type=Path, help="棋譜ファイルのパス (.kif / .csa)")
    parser.add_argument(
        "--json", action="store_true", help="解析結果をJSONで出力する"
    )
    parser.add_argument(
        "--opening-moves",
        type=int,
        default=10,
        help="序盤として表示する手数（デフォルト10）",
    )
    args = parser.parse_args(argv)

    if not args.kifu_file.exists():
        print(f"ファイルが見つかりません: {args.kifu_file}", file=sys.stderr)
        return 1

    game = _load_game(args.kifu_file)
    analyzer = GameAnalyzer(opening_move_count=args.opening_moves)
    stats = analyzer.analyze(game)

    if args.json:
        print(json.dumps(stats.to_dict(), ensure_ascii=False, indent=2))
    else:
        _print_report(game, stats)
    return 0


if __name__ == "__main__":
    sys.exit(main())
