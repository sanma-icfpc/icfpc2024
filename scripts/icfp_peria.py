#!/usr/bin/env python3

from collections import deque
import os
import sys
import unittest

def icfp2ascii(icfp, verbose=False):
    ast = compile(icfp, verbose)
    return ast.value if type(ast) is String else str(ast)


class Boolean(object):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def dump(self, level):
        dump(level, str(self))

    def optimize(self):
        return self, False

    def evaluate(self, _):
        return self


class Integer(object):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def dump(self, level):
        dump(level, str(self))

    def optimize(self):
        return self, False

    def evaluate(self, _):
        return self


class String(object):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f'"{self.value}"'

    def dump(self, level):
        dump(level, str(self))

    def optimize(self):
        return self, False

    def evaluate(self, _):
        return self


class UnaryOperator(object):
    def __init__(self, operator, value):
        self.operator = operator
        self.value = value

    def __str__(self):
        op = self.operator
        if op in ('-', '!'):
            return f"{self.operator}{self.value}"
        if op == '#':
            return f"STR2INT({self.value})"
        if op == '$':
            return f"INT2STR({self.value})"

    def dump(self, level):
        op = self.operator
        if op == '#':
            op = 'STR2INT'
        elif op == '$':
            op = 'INT2STR'
        dump(level, op)
        self.value.dump(level + 1)

    def optimize(self):
        op = self.operator
        val, updated = self.value.optimize()
        if op == '-' and type(val) is Integer:
            return Integer(-val.value), True
        if op == '!' and type(val) is Boolean:
            return Boolean(not val.value), True
        if op == '#' and type(val) is String:
            return Integer(icfp2int(val.value)), True
        if op == '$' and type(val) is Integer:
            return String(int2icfp(val.value)), True
        # There can be lambdas under this.
        return self, updated

    def evaluate(self, variable):
        self.value = self.value.evaluate(variable)
        return self


class BinaryOperator(object):
    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right

    def __str__(self):
        return f"({self.left} {self.operator} {self.right})"

    def dump(self, level):
        op = self.operator
        dump(level, op)
        self.left.dump(level + 1)
        self.right.dump(level + 1)

    def optimize(self):
        op = self.operator
        x, updatex = self.left.optimize()
        y, updatey = self.right.optimize()
        tx, ty = type(x), type(y)
        if op == '+' and tx is Integer and ty is Integer:
            return Integer(x.value + y.value), True
        if op == '-' and tx is Integer and ty is Integer:
            return Integer(x.value - y.value), True
        if op == '*' and tx is Integer and ty is Integer:
            return Integer(x.value * y.value), True
        if op == '/' and tx is Integer and ty is Integer:
            q = abs(x.value) // abs(y.value)
            if x.value * y.value < 0:
                q = -q
            return Integer(q), True
        if op == '%' and tx is Integer and ty is Integer:
            x, y = x.value, y.value
            q = abs(x) // abs(y)
            if x * y < 0:
                q = -q
            r = x - q * y
            return Integer(r), True
        if op == '<' and tx is Integer and ty is Integer:
            return Boolean(x.value < y.value), True
        if op == '>' and tx is Integer and ty is Integer:
            return Boolean(x.value > y.value), True
        if op == '<' and tx is Integer and ty is Integer:
            return Boolean(x.value < y.value), True
        if op == '=' and tx is Integer and ty is Integer:
            return Boolean(x.value == y.value), True
        if op == '=' and tx is Boolean and ty is Boolean:
            return Boolean(x.value == y.value), True
        if op == '=' and tx is String and ty is String:
            return Boolean(x.value == y.value), True
        if op == '|' and tx is Boolean and ty is Boolean:
            return Boolean(x.value or y.value), True
        if op == '&' and tx is Boolean and ty is Boolean:
            return Boolean(x.value and y.value), True
        if op == '.' and tx is String and ty is String:
            return String(x.value + y.value), True
        if op == 'T' and tx is Integer and ty is String:
            return String(y.value[:x.value]), True
        if op == 'D' and tx is Integer and ty is String:
            return String(y.value[x.value:]), True
        return self, (updatex or updatey)

    def evaluate(self, variable):
        self.left = self.left.evaluate(variable)
        self.right = self.right.evaluate(variable)
        return self


class If(object):
    def __init__(self, condition, true_branch, false_branch):
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch

    def __str__(self):
        return f"IF {self.condition}:\nTHEN:\n  {self.true_branch}\nELSE:\n  {self.false_branch}"

    def dump(self, level):
        dump(level, "IF")
        self.condition.dump(level + 1)
        dump(level, "THEN")
        self.true_branch.dump(level + 1)
        dump(level, "ELSE")
        self.false_branch.dump(level + 1)

    def optimize(self):
        c, updatec = self.condition.optimize()
        if type(c) is Boolean:
            # Do not optimize branches until the condition is evaluated.
            if c.value:
                return self.true_branch.optimize()
            else:
                return self.false_branch.optimize()
        return self, updatec

    def evaluate(self, variable):
        self.condition = self.condition.evaluate(variable)
        self.true_branch = self.true_branch.evaluate(variable)
        self.false_branch = self.false_branch.evaluate(variable)
        return self


class LambdaEvaluator(BinaryOperator):
    def __init__(self, left, right):
        super().__init__('$', left, right)

    def __str__(self):
        return f"(lambda {self.left} : {self.right})"

    def dump(self, level):
        dump(level, "EVAL")
        self.left.dump(level + 1)
        dump(level, "WHERE")
        self.right.dump(level + 1)

    def evaluate(self, variable):
        self.right = self.right.evaluate(variable)
        if type(self.left) == Lambda:
            key = self.left.parameter
            val = self.right
            return self.left.definition.evaluate((key, val))
        self.left = self.left.evaluate(variable)
        return self


class Lambda(object):
    def __init__(self, parameter, definition):
        self.parameter = parameter
        self.definition = definition

    def __str__(self):
        return f"Lambda (x{self.parameter}) {self.definition}"

    def dump(self, level):
        dump(level, "Lambda x{}".format(self.parameter))
        self.definition.dump(level + 1)

    def optimize(self):
        definition, updated = self.definition.optimize()
        if updated:
            return Lambda(self.parameter, definition), True
        return self, False

    def evaluate(self, variable):
        if variable is None:
            self.definition = self.definition.evaluate(variable)
            return self

        key, _ = variable
        if key == self.parameter:
            variable = None

        self.definition = self.definition.evaluate(variable)
        return self


class Variable(object):
    def __init__(self, parameter):
        self.parameter = parameter

    def __str__(self):
        return f"x{self.parameter}"

    def dump(self, level):
        dump(level, "x{}".format(self.parameter))

    def optimize(self):
        return self, False

    def evaluate(self, variable):
        if variable is None:
            return self
        key, val = variable
        if key == self.parameter:
            return val
        return self


def dump(level, message):
    print("| " * level + message, file=sys.stderr)


def compile(icfp, verbose=False):
    tokens = deque(icfp.split(' '))
    ast = parse(tokens)
    if verbose:
        dump(0, "Input")
        ast.dump(0)

    count = 0
    while True:
        ast, _ = ast.optimize()
        if verbose:
            ast.dump(0)
        ast = ast.evaluate(None)
        if type(ast) is String or count > 5:
            break
        count += 1
    return ast

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
        if body == '$':
            return LambdaEvaluator(left, right)
        return BinaryOperator(body, left, right)
    if indicator == 'L':
        param = asc2int(body)
        definition = parse(tokens)
        return Lambda(param, definition)
    if indicator == 'v':
        param = asc2int(body)
        return Variable(param)
    if indicator == '?':
        c = parse(tokens)
        t = parse(tokens)
        f = parse(tokens)
        return If(c, t, f)
    print("Unknown indicator [{}]: {}".format(indicator, body), file=sys.stderr)
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
        ]
        for icfp, expect in data:
            actual = translate(icfp)

            self.assertEqual(actual, expect)

    def test_lambda(self):
        icfp = 'B$ B$ L# L$ v# B. SB%,,/ S}Q/2,$_ IK'
        actual = translate(icfp)
        self.assertEqual(actual, "Hello World!")

    def test_icfp_eval(self):
        icfp = 'B$ L# B$ L" B+ v" v" B* I$ I# v8'
        actual = translate(icfp)
        self.assertEqual(actual, "12")

    def test_contest(self):
        x = 2 + 311 * 124753942619
        s = int2icfp(x)

class TestEnd2End(unittest.TestCase):
    def test_language(self):
        with open('scripts/test_data/language_test.icfp') as f:
            icfp = f.read().strip()
        ast = compile(icfp, verbose=False)
        self.assertTrue(type(ast) is String, ast.dump(0))
        self.assertEqual(ast.value, "Self-check OK, send `solve language_test 4w3s0m3` to claim points for it")

    def test_lambdaman6(self):
        with open('scripts/test_data/lambdaman6_test.icfp') as f:
            icfp = f.read().strip()
        ast = compile(icfp, verbose=True)
        dump(0, "Output")
        self.assertEqual(type(ast), String, ast.dump(0))

if __name__ == '__main__':
    unittest.main()