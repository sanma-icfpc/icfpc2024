#!/usr/bin/env python3

import argparse
import colorama
import icfp


def terminal(send_raw_icpc):
    verbose = False
    prompt = 'raw> ' if send_raw_icpc else 'ascii> '
    while True:
        print(colorama.Back.BLUE + colorama.Fore.WHITE + prompt, end="")
        try:
            command = input()
        finally:
            print(colorama.Style.RESET_ALL, end="")
        response = icfp.communicate(command, verbose, send_translate=not send_raw_icpc)
        print(response)


if __name__ == '__main__':
    colorama.init(autoreset=False)
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw', action='store_true', default=False)
    args = parser.parse_args()
    terminal(send_raw_icpc=args.raw)

