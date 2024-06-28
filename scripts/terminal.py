#!/usr/bin/env python3

import os
import json
import urllib.request

# https://boundvariable.space/communicate
URL_DOMAIN = "boundvariable.space"
TOKEN = os.environ["SANMA_TOKEN"]
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def terminal():
    while True:
        print("> ", end="")
        command = input()
        cryptic_command = 'S' + encrypt(command)
        # print("Cryptic: ", cryptic_command)
        request = urllib.request.Request(f"https://{URL_DOMAIN}/communicate",
                                         data=cryptic_command.encode(),
                                         headers=HEADERS)
        with urllib.request.urlopen(request) as res:
            response = res.read().decode('utf-8')
        # response = requests.post(f"https://{URL_DOMAIN}/communicate",
        #                         data=cryptic_command,
        #                         headers=HEADERS)
        # print("Cryptic response: ", response)
        plain_response = decrypt(response)
        print("Response: ")
        print(plain_response)

mapping = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!\"#$%&'()*+,-./:;<=>?@[\\]^_`|~ \n"

def decrypt(s):
    return ''.join(mapping[ord(c) - 33] for c in s)

def encrypt(s):
    m = {}
    for i in range(len(mapping)):
        m[mapping[i]] = i
    return ''.join(chr(m[c] + 33) for c in s)

if __name__ == '__main__':
    terminal()

