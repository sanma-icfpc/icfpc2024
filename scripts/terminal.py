#!/usr/bin/env python3

import colorama
import icfp


def terminal():
    verbose = False
    while True:
        print(colorama.Back.BLUE + colorama.Fore.WHITE + "> ", end="")
        command = input()
        print(colorama.Style.RESET_ALL, end="")
        response = icfp.communicate(command, verbose)
        print(response)


if __name__ == '__main__':
    colorama.init(autoreset=False)
    terminal()

