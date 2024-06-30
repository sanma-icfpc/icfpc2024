#!/usr/bin/env python3

import argparse
import sys
import icfp

def command():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-send-translate', action='store_false', dest='send_translate', help='Do not translate ICFP to human readable text.')
    parser.add_argument('--no-translate', action='store_false', dest='translate', help='Do not translate ICFP to human readable text.')
    parser.add_argument('--no-communicate', action='store_false', dest='communicate')
    parser.add_argument('-v', '--verbose', action='store_true', help='Print verbose output.')
    args = parser.parse_args()

    verbose = False
    lines = []
    for line in sys.stdin:
        lines.append(line)
    command = '\n'.join(lines).strip()
    if args.communicate:
        response = icfp.communicate(command, verbose=args.verbose, send_translate=args.send_translate, recv_translate=args.translate)
    else:
        response = icfp.icfp2ascii(command, verbose=args.verbose)
    print(response)


if __name__ == '__main__':
    command()

