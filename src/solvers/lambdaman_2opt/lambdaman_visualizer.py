import numpy as np
from typing import List, Tuple, Dict


action_dict_inv = {
    "R" : (1, 0),
    "L" : (-1, 0),
    "D" : (0, 1),
    "U" : (0, -1)
}

class Board:
    def __init__(self, board: List[str]) -> None:
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
        print(f"remaining pills: {len(self.pills)}")
        print(f"visited pills: {len(self.visited_pills)}")

    def go_path(self, path:str, wait_cnt:int=1) -> None:
        """
        pathで指定した経路を進ませる
        """
        cnt = 0
        next_wait = 1
        for pchar in path:
            p = action_dict_inv[pchar]
            self.lambdaman = (self.lambdaman[0] + p[0], self.lambdaman[1] + p[1])
            if self.lambdaman in self.pills:
                self.visited_pills.append(self.lambdaman)
                self.pills.remove(self.lambdaman)
            cnt += 1
            next_wait -= 1
            
            if next_wait == 0:
                self.print_board()
                print("walk counts", cnt)
                next_wait = input()
                # check input is digit
                
                if next_wait == "q":
                    return
                
                if next_wait.isdigit() and next_wait != "":
                    next_wait = int(next_wait)
                else:
                    next_wait = wait_cnt

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--sln")
    parser.add_argument("--wait", type=int, default=1)
    args = parser.parse_args()

    with open(args.sln) as f:
        sln_str = f.read().split(" ")
    
    board_id = int(sln_str[1].strip().replace("lambdaman", ""))
    board_str = open(f"data/courses/lambdaman/problems/lambdaman{board_id}.txt", "r").read().strip().split("\n")
    sln = sln_str[2]
    board = Board(board_str)
    # board.print_board()
    board.go_path(sln, args.wait)