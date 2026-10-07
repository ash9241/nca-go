"""Independent sgfmill cross-check with replayable seeds and move counts."""
import argparse
import time
import numpy as np
from sgfmill import boards
from ncago.go.rules import Position, IllegalMove
from .common import Run


def crosscheck(games, seed=2026, sizes=(9,19), max_moves_factor=2):
    rng = np.random.default_rng(seed)
    moves, by_size = 0, {}
    for game in range(games):
        size = sizes[game % len(sizes)]
        p, ref = Position.empty(size), boards.Board(size)
        count = 0
        for _ in range(max_moves_factor*size*size):
            move = None
            if rng.random() > .015:
                empty = np.argwhere(p.board == 0)
                for i in rng.permutation(len(empty)):
                    candidate = tuple(empty[i])
                    try:
                        child = p.play(candidate)
                        move = candidate
                        break
                    except IllegalMove:
                        continue
                else:
                    child = p.play(None)
            else:
                child = p.play(None)
            if move is not None:
                ref.play(*move, "b" if p.to_move == 1 else "w")
            actual = np.array([[{None:0,"b":1,"w":2}[ref.get(r,c)] for c in range(size)] for r in range(size)], np.int8)
            if not np.array_equal(child.board, actual):
                raise AssertionError(f"Mismatch game={game} move={count} seed={seed}")
            p = child
            moves += 1
            count += 1
            if p.passes == 2:
                break
        by_size[str(size)] = by_size.get(str(size),0)+1
        if (game+1) % max(1, games//10) == 0:
            print(f"crosscheck {game+1}/{games}: {moves} matching moves", flush=True)
    return {"games": games, "games_by_size": by_size, "moves": moves, "matched_moves": moves,
            "match_fraction": 1.0 if moves else None, "seed": seed}


def run(games=12, seed=2026):
    log = Run("0", {"games":games,"seed":seed,"sizes":[9,19],"max_moves_factor":2}, seed)
    try:
        metrics = crosscheck(games, seed)
        return log.finish("passed", gate="G0" if games >= 10000 else "G0-smoke", **metrics)
    except Exception as error:
        log.finish("failed", reason=str(error))
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--games", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()
    run(args.games,args.seed)


if __name__ == "__main__":
    main()
