#!/usr/bin/env python3

import icfp
import sys

def command():
    verbose = False
    lines = []
    for line in sys.stdin:
        lines.append(line)
    command = '\n'.join(lines).strip()
    response = icfp.communicate(command)
    print(response)


if __name__ == '__main__':
    command()

