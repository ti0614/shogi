import { shogigroundDropDests, shogigroundMoveDests } from "shogiops/compat";
import { makeSfen, initialSfen, parseSfen } from "shogiops/sfen";
import { Shogi } from "shogiops/variant/shogi";

export function createInitialPosition(): Shogi {
  return parseSfen("standard", initialSfen("standard")).unwrap() as Shogi;
}

export function sfenOf(pos: Shogi): string {
  return makeSfen(pos);
}

export function moveDests(pos: Shogi) {
  return shogigroundMoveDests(pos);
}

export function dropDests(pos: Shogi) {
  return shogigroundDropDests(pos);
}

export function isPromotable(role: string): boolean {
  return ["pawn", "lance", "knight", "silver", "bishop", "rook"].includes(role);
}

export const PROMOTES_TO: Record<string, string> = {
  pawn: "tokin",
  lance: "promotedlance",
  knight: "promotedknight",
  silver: "promotedsilver",
  bishop: "horse",
  rook: "dragon",
};

export const UNPROMOTES_TO: Record<string, string> = Object.fromEntries(
  Object.entries(PROMOTES_TO).map(([base, promoted]) => [promoted, base]),
);
