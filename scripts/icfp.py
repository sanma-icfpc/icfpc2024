#!/usr/bin/env python3

import icfp_peria
import icfp_tsuzuki

def communicate(command, verbose=False):
    return icfp_peria.communicate(command, verbose)
    # return icfp_tsuzuki.communicate(command, verbose)

if __name__ == '__main__':
    print("icfp.py is not intended to be run as a script. Please run command.py instead.")
