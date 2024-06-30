#!/usr/bin/env python3

import os
import requests

import icfp_peria

# https://boundvariable.space/communicate
URL_DOMAIN = "boundvariable.space"
TOKEN = os.environ["SANMA_TOKEN"]
HEADERS = {"Authorization": f"Bearer {TOKEN}"}


def communicate(ascii_command, verbose=False, send_translate=True, recv_translate=True):
    if send_translate:
        icfp_command = 'S' + encrypt(ascii_command)
    else:
        icfp_command = ascii_command
    response = requests.post(f"https://{URL_DOMAIN}/communicate",
                            data=icfp_command,
                            headers=HEADERS)
    response = response.text
    if verbose:
        print("ICFP response: ", response, file=sys.stderr)
    if recv_translate:
        response = icfp2ascii(response, verbose)
    return response


def icfp2ascii(icfp, verbose=False):
    return icfp_peria.icfp2ascii(icfp, verbose)


mapping = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!\"#$%&'()*+,-./:;<=>?@[\\]^_`|~ \n"
crypt_map = {}

def decrypt(s):
    return ''.join(mapping[ord(c) - 33] for c in s)

def encrypt(s):
    global crypt_map
    if len(crypt_map) == 0:
        for i in range(len(mapping)):
            crypt_map[mapping[i]] = i

    return ''.join(chr(crypt_map[c] + 33) for c in s)


if __name__ == '__main__':
    print("icfp.py is not intended to be run as a script. Please run command.py instead.")
