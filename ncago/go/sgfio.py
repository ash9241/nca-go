from pathlib import Path
from sgfmill import sgf
from .rules import Position


def read_sgf(path):
    game = sgf.Sgf_game.from_bytes(Path(path).read_bytes())
    root = game.get_root()
    pos = Position.empty(game.get_size())
    black, white, empty = root.get_setup_stones()
    for color, points in ((1, black), (2, white), (0, empty)):
        for p in points:
            pos.board[p] = color
    if root.has_property("PL"):
        pos.to_move = 1 if root.get("PL") == "b" else 2
    positions = [pos]
    for node in game.get_main_sequence()[1:]:
        color, move = node.get_move()
        if color is not None:
            pos = pos.play(move, 1 if color == "b" else 2)
            positions.append(pos)
    return positions


def write_sgf(path, size, moves, komi=7.5):
    game = sgf.Sgf_game(size=size)
    game.get_root().set("KM", komi)
    game.get_root().set("RU", "Tromp-Taylor")
    for color, point in moves:
        game.extend_main_sequence().set_move("b" if color == 1 else "w", point)
    Path(path).write_bytes(game.serialise())
