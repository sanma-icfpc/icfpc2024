#!/usr/bin/env python3

import os
import requests

# https://boundvariable.space/communicate
URL_DOMAIN = "boundvariable.space"
TOKEN = os.environ["SANMA_TOKEN"]
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def communicate(ascii_command, verbose=False):
    icfp_command = 'S' + encrypt(ascii_command)
    response = requests.post(f"https://{URL_DOMAIN}/communicate",
                            data=icfp_command,
                            headers=HEADERS)
    response = response.text
    if verbose:
        print("ICFP response: ", response)
    return process(response)


def process(response):
    if response.startswith('S'):
        return decrypt(response[1:])
    return decrypt(response)

mapping = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!\"#$%&'()*+,-./:;<=>?@[\\]^_`|~ \n"

def decrypt(s):
    return ''.join(mapping[ord(c) - 33] for c in s)

def encrypt(s):
    m = {}
    for i in range(len(mapping)):
        m[mapping[i]] = i
    return ''.join(chr(m[c] + 33) for c in s)


if __name__ == '__main__':
    print("Do not use icfp.py directly. Use terminal.py or command.py instead.")