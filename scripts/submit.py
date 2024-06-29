#!/usr/bin/env python3

import colorama
import os
import sys

import icfp


# このスクリプトの使い方
# はじめに入力データをproblems/(問題名)/(入力データ名).txtとして取得する。
# 次に出力データをsolutions/(問題名)/(入力データ名).solution.txtとして出力する。
# 最後に「submit.py (問題名)」を実行する。


def usage():
    print("usage: submit.py problem_name")


def terminal():
    verbose = False
    problem_name = sys.argv[1]
    problems_directory_path = f"data/problems/{problem_name}"
    for file_name in os.listdir(problems_directory_path):
        problem_file_path = os.path.join(problems_directory_path, file_name)
        if not os.path.isfile(problem_file_path):
            continue
        problem_file_name = os.path.basename(problem_file_path)
        problem_file_extension = os.path.splitext(problem_file_path)[1]
        if problem_file_extension != ".txt":
            continue
        problem_file_title = os.path.splitext(problem_file_name)[0]

        # 途中の入力データからsubmitする場合、以下をコメントアウトする。
        # if problem_file_title <= "spaceship13":
        #     continue

        solution_file_path = f"data/solutions/{problem_name}/{problem_file_title}.solution.txt"
        with open(solution_file_path) as file:
            solution = file.readline().strip()

        print(colorama.Back.BLUE + colorama.Fore.WHITE + "> ", end="")
        command = f"solve {problem_file_title} {solution}"
        print(colorama.Style.RESET_ALL, end="")
        response = icfp.communicate(command, verbose)
        print(response)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage()
        sys.exit()

    colorama.init(autoreset=False)
    terminal()

