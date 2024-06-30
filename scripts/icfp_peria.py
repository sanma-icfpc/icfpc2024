#!/usr/bin/env python3

from collections import deque
from pathlib import Path
import copy
import sys
import time
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
        return self

    def evaluate(self, _):
        return self

    def apply(self, _k, _v):
        return self


class Integer(object):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def dump(self, level):
        dump(level, str(self))

    def optimize(self):
        return self

    def evaluate(self, _):
        return self

    def apply(self, _k, _v):
        return self


class String(object):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f'"{self.value}"'

    def dump(self, level):
        dump(level, str(self))

    def optimize(self):
        return self

    def evaluate(self, _):
        return self

    def apply(self, _k, _v):
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
        val = self.value.optimize()
        if op == '-' and type(val) is Integer:
            return Integer(-val.value)
        if op == '!' and type(val) is Boolean:
            return Boolean(not val.value)
        if op == '#' and type(val) is String:
            return Integer(icfp2int(val.value))
        if op == '$' and type(val) is Integer:
            return String(int2icfp(val.value))
        # There can be lambdas under this node.
        return self

    def evaluate(self, values):
        value = self.value.evaluate(values).optimize()
        if value != self.value:
            return UnaryOperator(self.operator, value)
        return self

    def apply(self, k, v):
        value = self.value.apply(k, v).optimize()
        if value != self.value:
            return UnaryOperator(self.operator, value)
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
        x = self.left.optimize()
        y = self.right.optimize()
        tx, ty = type(x), type(y)
        if op == '+':
            if tx is Integer and x.value == 0:
                return y
            if ty is Integer and y.value == 0:
                return x
            if tx is Integer and ty is Integer:
                return Integer(x.value + y.value)
        if op == '-':
            if ty is Integer and y.value == 0:
                return x
            if tx is Integer and ty is Integer:
                return Integer(x.value - y.value)
        if op == '*':
            if tx is Integer:
                if x.value == 0:
                    return Integer(0)
                if x.value == 1:
                    return y
            if ty is Integer:
                if y.value == 0:
                    return Integer(0)
                if y.value == 1:
                    return x
            if tx is Integer and ty is Integer:
                return Integer(x.value * y.value)
        if op == '/':
            if tx is Integer and x.value == 0:
                return Integer(0)
            if ty is Integer and y.value == 1:
                return x
            if tx is Integer and ty is Integer:
                q = abs(x.value) // abs(y.value)
                if x.value * y.value < 0:
                    q = -q
                return Integer(q)
        if op == '%':
            if tx is Integer and x.value == 0:
                return Integer(0)
            if tx is Integer and ty is Integer:
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
        if op == '=':
            if tx == ty and tx in (Integer, Boolean, String):
                return Boolean(x.value == y.value)
        if op == '|':
            if tx is Boolean and x.value:
                return Boolean(True)
            if ty is Boolean and y.value:
                return Boolean(True)
            if tx is Boolean and ty is Boolean:
                return Boolean(x.value or y.value)
        if op == '&':
            if tx is Boolean and not x.value:
                return Boolean(False)
            if ty is Boolean and not y.value:
                return Boolean(False)
            if tx is Boolean and ty is Boolean:
                return Boolean(x.value and y.value)
        if op == '.' and tx is String and ty is String:
            return String(x.value + y.value)
        if op == 'T' and tx is Integer and ty is String:
            return String(y.value[:x.value])
        if op == 'D' and tx is Integer and ty is String:
            return String(y.value[x.value:])

        if x != self.left or y != self.right:
            return BinaryOperator(self.operator, x, y)
        return self

    def evaluate(self, values):
        left = self.left.evaluate(values).optimize()
        right = self.right.evaluate(values).optimize()
        if left != self.left or right != self.right:
            return BinaryOperator(self.operator, left, right)
        return self

    def apply(self, k, v):
        left = self.left.apply(k, v).optimize()
        right = self.right.apply(k, v).optimize()
        if left != self.left or right != self.right:
            return BinaryOperator(self.operator, left, right)
        return self


class If(object):
    def __init__(self, condition, true_branch, false_branch):
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch

    def __str__(self):
        return f"\nIF {self.condition}:\nTHEN: {self.true_branch}\nELSE: {self.false_branch}"

    def dump(self, level):
        dump(level, "IF")
        self.condition.dump(level + 1)
        dump(level, "THEN")
        self.true_branch.dump(level + 1)
        dump(level, "ELSE")
        self.false_branch.dump(level + 1)

    def optimize(self):
        c = self.condition.optimize()
        if type(c) is Boolean:
            # Do not optimize branches until the condition is evaluated.
            if c.value:
                return self.true_branch.optimize()
            else:
                return self.false_branch.optimize()
        return self

    def evaluate(self, values):
        condition = self.condition.evaluate(values).optimize()
        if type(condition) is Boolean:
            if condition.value:
                return self.true_branch.evaluate(values)
            else:
                return self.false_branch.evaluate(values)

        if condition != self.condition:
            return If(condition, self.true_branch, self.false_branch)
        return self

    def apply(self, k, v):
        condition = self.condition.apply(k, v).optimize()
        if type(condition) is Boolean:
            if condition.value:
                return self.true_branch.apply(k, v).optimize()
            else:
                return self.false_branch.apply(k, v).optimize()

        true_branch = self.true_branch.apply(k, v).optimize()
        false_branch = self.false_branch.apply(k, v).optimize()
        if condition != self.condition or true_branch != self.true_branch or false_branch != self.false_branch:
            return If(condition, true_branch, false_branch)
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

    def optimize(self):
        x = self.left.optimize()
        y = self.right.optimize()
        if x != self.left or y != self.right:
            return LambdaEvaluator(x, y)
        return self

    def evaluate(self, _):
        left = self.left
        if type(left) is Lambda:
            key = left.parameter
            value = self.right
            # dump(0, f"Match x{key} = {value}")
            return left.definition.apply(key, value).optimize()

        left = left.evaluate(self.right).optimize()
        if left != self.left:
            return LambdaEvaluator(left, self.right)
        return self

    def apply(self, k, v):
        left = self.left.apply(k, v).optimize()
        right = self.right.apply(k, v).optimize()
        if left != self.left or right != self.right:
            return LambdaEvaluator(left, right)
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
        definition = self.definition.optimize()
        if definition != self.definition:
            return Lambda(self.parameter, definition)
        return self

    def evaluate(self, values):
        definition = self.definition.evaluate(values).optimize()
        if definition != self.definition:
            return Lambda(self.parameter, definition)
        return self

    def apply(self, k, v):
        if self.parameter == k:
            return self
        definition = self.definition.apply(k, v).optimize()
        if definition != self.definition:
            return Lambda(self.parameter, definition)
        return self


class Variable(object):
    def __init__(self, parameter):
        self.parameter = parameter

    def __str__(self):
        return f"x{self.parameter}"

    def dump(self, level):
        dump(level, "v{}".format(self.parameter))

    def optimize(self):
        return self

    def evaluate(self, _):
        return self

    def apply(self, k, v):
        if self.parameter == k:
            return copy.copy(v)
        return self


def dump(level, message):
    print("| " * level + message, file=sys.stderr)


def compile(icfp, verbose=False):
    tokens = deque(icfp.split(' '))
    ast = parse(tokens)
    if verbose:
        dump(0, "Input")

    count = 0
    while True:
        if verbose:
            # ast.dump(0)
            dump(0, f'{ast}\n')
            # time.sleep(1)
        next = ast.evaluate(None).optimize()
        if next == ast:
            break
        ast = next
        if type(ast) is String or count > 1000000:
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

def I_decode(icfp):
    value = 0
    for c in icfp:
        value = value * 94 + ord(c) - 33
    return value

def I_encode(value):
    result = []
    while True:
        result.append(chr(value % 94 + 33))
        value //= 94
        if value == 0: break
    return ''.join(reversed(result))

class TestICFP(unittest.TestCase):
    def test_I_code(self):
        self.assertEqual(I_decode('!'), 0)
        self.assertEqual(I_decode('/6'), 1337) # from the rules
        self.assertEqual(I_encode(0), '!')
        self.assertEqual(I_encode(1337), '/6')

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
            actual = icfp2ascii(icfp)
            self.assertEqual(actual, expect)

    def test_lambda(self):
        icfp = 'B$ B$ L# L$ v# B. SB%,,/ S}Q/2,$_ IK'
        actual = icfp2ascii(icfp)
        self.assertEqual(actual, "Hello World!")

    def test_icfp_eval(self):
        icfp = 'B$ L# B$ L" B+ v" v" B* I$ I# v8'
        actual = icfp2ascii(icfp)
        self.assertEqual(actual, "12")

    def test_simple_language_test(self):
        icfp = 'B$ B$ B$ B$ L$ L$ L$ L# v$ I" I# I$ I%'
        actual = icfp2ascii(icfp)
        self.assertEqual(actual, "3")

    def test_contest(self):
        x = 2 + 311 * 124753942619
        s = int2icfp(x)

class TestEnd2End(unittest.TestCase):
    SCRIPT_DIR = Path(__file__).parent
    TEST_DATA_DIR = SCRIPT_DIR / 'test_data'

    def test_language(self):
        with open(self.TEST_DATA_DIR / 'language_test.icfp') as f:
            icfp = f.read().strip()
        ast = compile(icfp)
        self.assertTrue(type(ast) is String)
        self.assertEqual(ast.value, "Self-check OK, send `solve language_test 4w3s0m3` to claim points for it")

    def test_lambdaman6(self):
        with open(self.TEST_DATA_DIR / 'lambdaman6_test.icfp') as f:
            icfp = f.read().strip()
        ast = compile(icfp)
        self.assertEqual(type(ast), String)


class TestEfficiency(unittest.TestCase):
    SCRIPT_DIR = Path(__file__).parent
    ROOT_DIR = SCRIPT_DIR.parent
    PROBLEMS_DIR = ROOT_DIR / 'data' / 'courses' / 'efficiency' / 'problems'

    def run_test(self, id, verbose=False):
        filename = f'efficiency{id}.icfp'
        with open(self.PROBLEMS_DIR / filename) as f:
            icfp = f.read().strip()
        ast = compile(icfp, verbose)
        self.assertEqual(type(ast), Integer)
        return ast.value

    # Eval from the leaf node.
    def dis_test_efficiency1(self):
        value = self.run_test('1')
        self.assertEqual(value, 4**22)

    # "* 0" operation results in 0.
    def dis_test_efficiency2(self):
        value = self.run_test('2')
        self.assertEqual(value, 2134)

    # Optimize the recursive call that produces too many "+1" operation.
    def dis_test_efficiency3(self):
        value = self.run_test('3')
        self.assertEqual(value, 9345875634)

    # Fibonacci number. Memo-ization is required.
    def dis_test_efficiency4(self):
        value = self.run_test('4')
        self.assertEqual(value, 165580141)

    # It outputs (2^k)-1 for x<(2^k)-1, where k is 2,3,5,7,13,17, and 31.
    # Reason of the equence is not sure.
    def dis_test_efficiency5(self):
        value = self.run_test('5')
        self.assertEqual(value, 2**31-1)

    # It outputs 42. f(x) is minimum in 2,3,4,6,10,12,16,22,28... where f(x) > x.
    def dis_test_efficiency6(self):
        value = self.run_test('6')
        self.assertEqual(value, 42)

if __name__ == '__main__':
    unittest.main()
