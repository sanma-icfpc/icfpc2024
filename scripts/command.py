#!/usr/bin/env python3

import icfp


def command():
    verbose = False
    command = input()
    response = icfp.communicate(command)
    print(response)


if __name__ == '__main__':
    command()

