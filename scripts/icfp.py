#!/usr/bin/env python3

from collections import deque
import os
import requests
import unittest

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
    return icfp2ascii(response)

class Boolean(object):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def evaluate(self):
        return self

class Integer(object):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def evaluate(self):
        return self

class String(object):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

    def evaluate(self):
        return self

class UnaryOperator(object):
    def __init__(self, operator, value):
        self.operator = operator
        self.value = value

    def __str__(self):
        return f"{self.operator}{self.value}"

    def substitute(self, parameter, value):
        if isinstance(self.value, LambdaUse) and self.value.parameter == parameter:
            self.value = value
        return self

    def evaluate(self):
        op = self.operator
        val = self.value.evaluate()
        if op == '-' and type(val) is Integer:
            return Integer(-val.value)
        if op == '!' and type(val) is Boolean:
            return Boolean(not val.value)
        if op == '#' and type(val) is String:
            return Integer(icfp2int(val.value))
        if op == '$' and type(val) is Integer:
            return String(int2icfp(val.value))
        # There can be lambdas under this.
        return self

class BinaryOperator(object):
    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right

    def __str__(self):
        return f"({self.left} {self.operator} {self.right})"

    def substitute(self, parameter, value):
        if isinstance(self.left, LambdaUse) and self.left.parameter == parameter:
            self.left = value
        if isinstance(self.right, LambdaUse) and self.right.parameter == parameter:
            self.right = value
        return self

    def evaluate(self):
        op = self.operator
        x = self.left.evaluate()
        y = self.right.evaluate()
        tx, ty = type(x), type(y)
        if op == '+' and tx is Integer and ty is Integer:
            return Integer(x.value + y.value)
        if op == '-' and tx is Integer and ty is Integer:
            return Integer(x.value - y.value)
        if op == '*' and tx is Integer and ty is Integer:
            return Integer(x.value * y.value)
        if op == '/' and tx is Integer and ty is Integer:
            q = abs(x.value) // abs(y.value)
            if x.value * y.value < 0:
                q = -q
            return Integer(q)
        if op == '%' and tx is Integer and ty is Integer:
            x, y = x.value, y.value
            q = abs(x) // abs(y)
            if x * y < 0:
                q = -q
            r = x - q * y
            return Integer(r)
        if op == '<' and tx is Integer and ty is Integer:
            return Boolean(x.value < y.value)
        if op == '>' and tx is Integer and ty is Integer:
            return Boolean(x.value > y.value)
        if op == '<' and tx is Integer and ty is Integer:
            return Boolean(x.value < y.value)
        if op == '=' and tx is Integer and ty is Integer:
            return Boolean(x.value == y.value)
        if op == '=' and tx is Boolean and ty is Boolean:
            return Boolean(x.value == y.value)
        if op == '=' and tx is String and ty is String:
            return Boolean(x.value == y.value)
        if op == '|' and tx is Boolean and ty is Boolean:
            return Boolean(x.value or y.value)
        if op == '&' and tx is Boolean and ty is Boolean:
            return Boolean(x.value and y.value)
        if op == '.' and tx is String and ty is String:
            return String(x.value + y.value)
        if op == 'T' and tx is Integer and ty is String:
            return String(y.value[:x.value])
        if op == 'D' and tx is Integer and ty is String:
            return String(y.value[x.value:])
        if op == '$':
            assert isinstance(x, LambdaArg), f'{x} is not LambdaArg'
            x.setArgument(y)
            return x.evaluate()

        return self

class If(object):
    def __init__(self, condition, true_branch, false_branch):
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch

    def __str__(self):
        return f"IF {self.condition}:\nTHEN:\n{self.true_branch}\nELSE:\n{self.false_branch}"

    def evaluate(self):
        c = self.condition.evaluate()
        t = self.true_branch.evaluate()
        f = self.false_branch.evaluate()
        if type(c) is Boolean:
            return t if c else f
        return self

class LambdaArg(object):
    def __init__(self, parameter, definition):
        self.parameter = parameter
        self.definition = definition
        self.argument = None

    def setArgument(self, argument):
        self.argument = argument

    def __str__(self):
        return f"L{self.parameter}.({self.definition})"

    def evaluate(self):
        if self.argument is None:
            # unresolved
            return self
        else:
            return self.definition.substitute(self.parameter, self.argument).evaluate()

class LambdaUse(object):
    def __init__(self, parameter):
        self.parameter = parameter

    def __str__(self):
        return f"v({self.parameter})"

    def evaluate(self):
        return self


def icfp2ascii(response):
    tokens = deque(response.split(' '))
    ast = parse(tokens)
    ast = ast.evaluate()
    return str(ast.evaluate())

def parse(tokens):
    token = tokens.popleft()
    indicator, body = token[0], token[1:]
    if indicator == 'T':
        return Boolean(True)
    if indicator == 'F':
        return Boolean(False)
    if indicator == 'I':
        return Integer(asc2int(body))
    if indicator == 'S':
        return String(decrypt(body))
    if indicator == 'U':
        operand = parse(tokens)
        return UnaryOperator(body, operand)
    if indicator == 'B':
        left = parse(tokens)
        right = parse(tokens)
        return BinaryOperator(body, left, right)
    if indicator == 'L':
        param = asc2int(body)
        definition = parse(tokens)
        return LambdaArg(param, definition)
    if indicator == 'v':
        param = asc2int(body)
        return LambdaUse(param)
    if indicator == '?':
        c = parse(tokens)
        t = parse(tokens)
        f = parse(tokens)
        return If(c, t, f)
    print("Unknown indicator [{}]: {}".format(indicator, body))
    return None


def asc2int(body):
    value = 0
    for c in body:
        value = value * 94 + ord(c) - 33
    return value


def int2asc(value):
    result = []
    while value > 0:
        result.append(chr(value % 94 + 33))
        value //= 94
    return ''.join(reversed(result))


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

def icfp2int(icfp):
    global crypt_map
    if len(crypt_map) == 0:
        for i in range(len(mapping)):
            crypt_map[mapping[i]] = i

    value = 0
    for c in icfp:
        value = value * 94 + crypt_map[c]
    return value

def int2icfp(value):
    result = []
    while value > 0:
        result.append(mapping[value % 94])
        value //= 94
    return ''.join(reversed(result))

class TestICFP(unittest.TestCase):
    def test_icfp2ascii(self):
        data = [
            ("T", "True"), # Boolean
            ("F", "False"),
            ("I/6", "1337"), # Integer
            ("SB%,,/}Q/2,$_", "Hello World!"), # String
            ("U- I$", "-3"), # Unary operator
            ("U! T", "False"),
            ("U# S4%34", "15818151"),
            ("U$ I4%34", "test"),
            ("B+ I# I$", "5"), # Binary operator
            ("B- I$ I#", "1"),
            ("B* I$ I#", "6"),
            ("B/ U- I( I#", "-3"),
            ("B% U- I( I#", "-1"),
            ("B< I$ I#", "False"),
            ("B> I$ I#", "True"),
            ("B= I$ I#", "False"),
            ("B| T F", "True"),
            ("B& T F", "False"),
            ("B. S4% S34", "test"),
            ("BT I$ S4%34", "tes"),
            ("BD I$ S4%34", "t"),
            ("B$ L! B+ v! v! I#", "4"), # (v0 => v0 + v0)(2) == 4
            ("B$ L# U- v# I%", "-4"), # (v2 => - v2)(4) == -4
            ("B$ L! B+ v! I\" I$", "4"), # (v0 => v0 + 1)(3) == 4
            ("B$ L! B+ v! B$ L# U- v# I$ I% ", "1"), # (v0 => v0 + (v2 => - v2)))(3)(4) == 1
        ]
        for icfp, expect in data:
            actual = icfp2ascii(icfp)

            self.assertEqual(actual, expect)

    def test_icfp_eval(self):
        icfp = 'B$ L# B$ L" B+ v" v" B* I$ I# v8'
        actual = icfp2ascii(icfp)
        self.assertEqual(actual, "12") # I-

if __name__ == '__main__':
    unittest.main()