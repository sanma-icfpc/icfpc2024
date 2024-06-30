#!/usr/bin/env python3

import os
import re
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

def reduce_extended_icfp(extended_icfp):
    '''
    myfunc := L! U- v!
    main := B$ $myfunc I#
    みたいなのを入力として、B$ L! U- v! I# を出力する
    両脇にスペースのある()は消す
    '''
    vardict = {}
    for line in extended_icfp.splitlines():
        line = line.strip()
        if len(line) == 0 or line[0] == '#':
            continue
        mo = re.match(r'^\s*([a-zA-Z0-9_]+)\s*:=\s*(.*)$', line)
        if mo is None:
            raise ValueError(f'invalid line: "{line}"')
        name, value = mo.groups()
        vardict[name] = value

    def resolve(s):
        s = s.replace(' ( ', ' ').replace(' ) ', ' ')
        for name, value in vardict.items():
            s = re.sub(r'\$' + name + r'\b', value, s)
        return s

    def resolve_all(s):
        step = resolve(s)
        if step == s:
            return step
        return resolve_all(step)

    return resolve_all(vardict['main'])

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
