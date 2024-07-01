"""
python-tspを使ってlambdamanをとく
https://github.com/fillipe-gsm/python-tsp
"""

import numpy as np
from typing import List, Tuple, Dict


action_dicts = [
    {
        (1, 0): "R",
        (-1, 0): "L",
        (0, 1): "D",
        (0, -1): "U"
    },
    {
        (0, 1): "D",
        (0, -1): "U",
        (1, 0): "R",
        (-1, 0): "L"
    },
    {
        (-1, 0): "L",
        (1, 0): "R",
        (0, 1): "D",
        (0, -1): "U"
    },
    {
        (0, -1): "U",
        (0, 1): "D",
        (1, 0): "R",
        (-1, 0): "L"
    },
    {
        (1, 0): "R",
        (-1, 0): "L",
        (0, -1): "U",
        (0, 1): "D",
    },
    {
        (0, 1): "D",
        (0, -1): "U",
        (-1, 0): "L",
        (1, 0): "R",
    },
    {
        (-1, 0): "L",
        (1, 0): "R",
        (0, -1): "U",
        (0, 1): "D",
    },
    {
        (0, -1): "U",
        (0, 1): "D",
        (-1, 0): "L",
        (1, 0): "R",
    },
]




class Board:
    def __init__(self, board: List[str], action_dict:Dict[Tuple[int, int], str]) -> None:
        self.board = board
        self.y_size = len(board)
        self.x_size = len(board[0])
        for i in range(self.y_size):
            if len(board[i]) != self.x_size:
                raise ValueError("Invalid Board")
        self.pills = []
        self.visited_pills = []
        self.walls = []
        for y in range(self.y_size):
            for x in range(self.x_size):
                if board[y][x] == 'L':
                    self.lambdaman = (x, y)
                elif board[y][x] == '.':
                    self.pills.append((x, y))
                elif board[y][x] == '#':
                    self.walls.append((x, y))
        self.action_dict = action_dict

    def finish(self) -> bool:
        return len(self.pills) == 0

    def get_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """
        ダイクストラ法でabの距離と経路を返す
        """
        def get_adjacent(pos: Tuple[int, int]) -> List[Tuple[int, int]]:
            x, y = pos
            return [(1, 0), (-1, 0), (0, 1), (0, -1)]
        
        def is_valid_pos(pos: Tuple[int, int]) -> bool:
            x, y = pos
            if x < 0 or x >= self.x_size or y < 0 or y >= self.y_size:
                return False
            if pos in self.walls:
                return False
            return True
        
        path_dict:Dict[Tuple[int, int], List[int]] = {}
        path_dict[pos1] = []
        queue = [pos1]
        while queue:
            x, y = queue.pop(0)
            for dx, dy in get_adjacent((x, y)):
                x_check = x + dx
                y_check = y + dy
                if not is_valid_pos((x_check, y_check)):
                    continue
                if (x_check, y_check) in path_dict:
                    continue
                path_dict[(x_check, y_check)] = path_dict[(x, y)] + [(dx, dy)]
                if (x_check, y_check) == pos2:
                    return (x_check, y_check), path_dict[(x_check, y_check)]
                queue.append((x_check, y_check))
        raise ValueError("Invalid Position")

    def find_nearest_pill(self, pos: Tuple[int, int]) -> Tuple[Tuple[int, int], List[int]]:
        """
        ダイクストラ法で最も近いPillを探し、そのpillまでの経路を返す
        """
        def get_adjacent(pos: Tuple[int, int]) -> List[Tuple[int, int]]:
            x, y = pos
            return self.action_dict.keys()
        
        def is_valid_pos(pos: Tuple[int, int]) -> bool:
            x, y = pos
            if x < 0 or x >= self.x_size or y < 0 or y >= self.y_size:
                return False
            if pos in self.walls:
                return False
            return True
        
        path_dict:Dict[Tuple[int, int], List[int]] = {}
        path_dict[pos] = []
        queue = [pos]
        while queue:
            x, y = queue.pop(0)
            for dx, dy in get_adjacent((x, y)):
                x_check = x + dx
                y_check = y + dy
                if not is_valid_pos((x_check, y_check)):
                    continue
                if (x_check, y_check) in path_dict:
                    continue
                path_dict[(x_check, y_check)] = path_dict[(x, y)] + [(dx, dy)]
                if (x_check, y_check) in self.pills and (x_check, y_check) not in self.visited_pills:
                    return (x_check, y_check), path_dict[(x_check, y_check)]
                queue.append((x_check, y_check))


    def print_board(self) -> None:
        for i in range(self.y_size):
            row = ""
            for j in range(self.x_size):
                if (j, i) == self.lambdaman:
                    row += "L"
                elif (j, i) in self.pills:
                    row += "."
                elif (j, i) in self.walls:
                    row += "#"
                else:
                    row += " "
            print(row)

    def go_path(self, path:List[Tuple[int, int]]) -> None:
        """
        pathで指定した経路を進ませる
        """
        for p in path:
            self.lambdaman = (self.lambdaman[0] + p[0], self.lambdaman[1] + p[1])
            if self.lambdaman in self.pills:
                self.visited_pills.append(self.lambdaman)
                self.pills.remove(self.lambdaman)



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=1)
    args = parser.parse_args()

    if args.n == -1:
        indice = [i for i in range(1, 20)]
    else:
        indice = [args.n]

    for idx in indice:
        board_str = open(f"data/courses/lambdaman/problems/lambdaman{idx}.txt", "r").read().strip().split("\n")
        best = ""
        for k in range(8):
            board = Board(board_str, action_dict=action_dicts[k])
            # board.print_board()
            out = ""
            while not board.finish():
                path = board.find_nearest_pill(board.lambdaman)
                board.go_path(path[1])
                print(path[1], len(board.pills))
                out += "".join([board.action_dict[p] for p in path[1]])
                # board.print_board()
            board.print_board()
            if len(out) < len(best) or best == "":
                best = out
            print(out)
        with open(f"lambdaman_sln_{idx}.txt", "w") as f:
            f.write(f"solve lambdaman{idx} {best}")

