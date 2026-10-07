"""Benson opponent-playout property checks with actual counts and seed logs."""
import argparse
import numpy as np
from ncago.go.generators import living
from ncago.go.labels import benson
from ncago.go.rules import Position,chains
from .common import Run


def run(playouts=2000,seed=2026):
    log = Run("2-properties",{"playouts_per_chain":playouts,"seed":seed,"fixtures":4,"moves_per_playout":30},seed)
    rng = np.random.default_rng(seed)
    checked,moves = 0,0
    for fixture in range(4):
        board = living(9,rng,True)
        labels,_ = benson(board)
        for chain in chains(board):
            if labels[chain.points[0]] not in (0,1):
                continue
            for _ in range(playouts):
                pos = Position(board.copy(),3-chain.color)
                for _ in range(30):
                    legal = pos.legal_moves()
                    point = legal[int(rng.integers(len(legal)))]
                    pos = pos.play(point).play(None)
                    moves += 1
                if any(pos.board[p] != chain.color for p in chain.points):
                    log.finish("failed",reason="Pass-alive chain captured in opponent playout",fixture=fixture)
                    raise AssertionError("Benson property failed")
                checked += 1
        print(f"Benson properties: fixture {fixture+1}/4, {checked} playouts checked",flush=True)
    return log.finish("passed",playouts=checked,opponent_moves=moves,playouts_per_chain=playouts,seed=seed)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--playouts",type=int,default=2000)
    run(parser.parse_args().playouts)
