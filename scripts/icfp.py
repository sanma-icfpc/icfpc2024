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

    def substitute(self, parameter, value, evaluator):
        return self

    def evaluate(self, evaluator):
        return self

class Integer(object):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def substitute(self, parameter, value, evaluator):
        return self

    def evaluate(self, evaluator):
        return self

class String(object):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

    def substitute(self, parameter, value, evaluator):
        return self

    def evaluate(self, evaluator):
        return self

def is_value_term(term):
    return isinstance(term, Boolean) or isinstance(term, Integer) or isinstance(term, String)

class Evaluator(object):
    def __init__(self, max_num_strict_evaluation=None, max_num_beta_reduction=None, max_any_step=None):
        self.max_num_strict_evaluation = max_num_strict_evaluation
        self.max_num_beta_reduction = max_num_beta_reduction
        self.max_any_step = max_any_step
        self.num_strict_evaluation = 0
        self.num_beta_reduction = 0

    def update(self, strict_evaluation, beta_reduction):
        self.num_strict_evaluation += strict_evaluation
        self.num_beta_reduction += beta_reduction
    
    def is_limit_reached(self):
        return (
            (self.max_num_strict_evaluation is not None and self.max_num_strict_evaluation <= self.num_strict_evaluation) or
            (self.max_num_beta_reduction is not None and self.max_num_beta_reduction <= self.num_beta_reduction) or
            (self.max_any_step is not None and self.max_any_step <= self.num_strict_evaluation + self.num_beta_reduction)
        )

    def __call__(self, expr):
        if self.is_limit_reached():
            return expr
        val = expr.evaluate(self)
        return val

    def try_substitute(self, expr, parameter, value):
        if isinstance(expr, LambdaUse) and expr.parameter == parameter:
            self.update(0, 1)
            return value
        else:
            expr.substitute(parameter, value, self)
            return expr

    def __repr__(self):
        return f'<Evaluator(strict {self.num_strict_evaluation}/{self.max_num_strict_evaluation}, beta {self.num_beta_reduction}/{self.max_num_beta_reduction}, any {self.num_beta_reduction+self.num_strict_evaluation}/{self.max_any_step})'

class UnaryOperator(object):
    def __init__(self, operator, value):
        self.operator = operator
        self.value = value

    def __str__(self):
        return f"{self.operator}{self.value}"

    def substitute(self, parameter, value, evaluator):
        if isinstance(self.value, LambdaUse) and self.value.parameter == parameter:
            self.value = value
            evaluator.update(0, 1)
        else:
            self.value.substitute(parameter, value, evaluator)
        return self

    def evaluate(self, evaluator):
        op = self.operator
        val = evaluator(self.value)
        if not evaluator.is_limit_reached():
            if op == '-' and type(val) is Integer:
                evaluator.update(1, 0)
                return Integer(-val.value)
            if op == '!' and type(val) is Boolean:
                evaluator.update(1, 0)
                return Boolean(not val.value)
            if op == '#' and type(val) is String:
                evaluator.update(1, 0)
                return Integer(icfp2int(val.value))
            if op == '$' and type(val) is Integer:
                evaluator.update(1, 0)
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

    def substitute(self, parameter, value, evaluator):
        self.left = evaluator.try_substitute(self.left, parameter, value)
        self.right = evaluator.try_substitute(self.right, parameter, value)
        return self

    def evaluate(self, evaluator):
        op = self.operator
        x = evaluator(self.left)
        self.left = x
        if evaluator.is_limit_reached():
            return self
        y = evaluator(self.right)
        self.right = y
        if evaluator.is_limit_reached():
            return self
        tx, ty = type(x), type(y)
        if op == '+' and tx is Integer and ty is Integer:
            evaluator.update(1, 0)
            return Integer(x.value + y.value)
        if op == '-' and tx is Integer and ty is Integer:
            evaluator.update(1, 0)
            return Integer(x.value - y.value)
        if op == '*' and tx is Integer and ty is Integer:
            evaluator.update(1, 0)
            return Integer(x.value * y.value)
        if op == '/' and tx is Integer and ty is Integer:
            q = abs(x.value) // abs(y.value)
            if x.value * y.value < 0:
                q = -q
            evaluator.update(1, 0)
            return Integer(q)
        if op == '%' and tx is Integer and ty is Integer:
            x, y = x.value, y.value
            q = abs(x) // abs(y)
            if x * y < 0:
                q = -q
            r = x - q * y
            evaluator.update(1, 0)
            return Integer(r)
        if op == '<' and tx is Integer and ty is Integer:
            evaluator.update(1, 0)
            return Boolean(x.value < y.value)
        if op == '>' and tx is Integer and ty is Integer:
            evaluator.update(1, 0)
            return Boolean(x.value > y.value)
        if op == '<' and tx is Integer and ty is Integer:
            evaluator.update(1, 0)
            return Boolean(x.value < y.value)
        if op == '=' and tx is Integer and ty is Integer:
            evaluator.update(1, 0)
            return Boolean(x.value == y.value)
        if op == '=' and tx is Boolean and ty is Boolean:
            evaluator.update(1, 0)
            return Boolean(x.value == y.value)
        if op == '=' and tx is String and ty is String:
            evaluator.update(1, 0)
            return Boolean(x.value == y.value)
        if op == '|' and tx is Boolean and ty is Boolean:
            evaluator.update(1, 0)
            return Boolean(x.value or y.value)
        if op == '&' and tx is Boolean and ty is Boolean:
            evaluator.update(1, 0)
            return Boolean(x.value and y.value)
        if op == '.' and tx is String and ty is String:
            evaluator.update(1, 0)
            return String(x.value + y.value)
        if op == 'T' and tx is Integer and ty is String:
            evaluator.update(1, 0)
            return String(y.value[:x.value])
        if op == 'D' and tx is Integer and ty is String:
            evaluator.update(1, 0)
            return String(y.value[x.value:])
        if op == '$':
            assert isinstance(x, LambdaArg), f'{x} is not LambdaArg'
            x.setArgument(y)
            return evaluator(x)
        return self

class If(object):
    def __init__(self, condition, true_branch, false_branch):
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch

    def __str__(self):
        return f"IF {self.condition}:\nTHEN:\n{self.true_branch}\nELSE:\n{self.false_branch}"

    def substitute(self, parameter, value, evaluator):
        self.condition = evaluator.try_substitute(self.condition, parameter, value)
        self.true_branch = evaluator.try_substitute(self.true_branch, parameter, value)
        self.false_branch = evaluator.try_substitute(self.false_branch, parameter, value)
        return self

    def evaluate(self, evaluator):
        c = evaluator(self.condition)
        if type(c) is Boolean:
            if c.value:
                return evaluator(self.true_branch)
            else:
                return evaluator(self.false_branch)
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

    def substitute(self, parameter, value, evaluator):
        self.definition = evaluator.try_substitute(self.definition, parameter, value)
        return self

    def evaluate(self, evaluator):
        if self.argument is None:
            # unresolved
            return self
        else:
            return evaluator(self.definition.substitute(self.parameter, self.argument, evaluator))

class LambdaUse(object):
    def __init__(self, parameter):
        self.parameter = parameter

    def __str__(self):
        return f"v({self.parameter})"

    def substitute(self, parameter, value, evaluator):
        return self

    def evaluate(self, evaluator):
        return self

def icfp2ascii(response):
    limit = Evaluator()
    tokens = deque(response.split(' '))
    ast = parse(tokens)
    ast = ast.evaluate(limit)
    return str(ast.evaluate(limit))

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
            ("? T I! I#", "0"),
            ("? F I! I#", "2"),
        ]
        for icfp, expect in data:
            actual = icfp2ascii(icfp)

            self.assertEqual(actual, expect)

    def test_icfp_eval(self):
        icfp = 'B$ L# B$ L" B+ v" v" B* I$ I# v8'
        actual = icfp2ascii(icfp)
        self.assertEqual(actual, "12") # I-

    def test_icfp_eval_reduction(self):
        icfp = "B$ L! B+ v! B$ L# U- v# I$ I% "
        tokens = deque(icfp.split(' '))
        ast = parse(tokens)
        i = 1
        while True:
            print(f'AST at step {i:3d}:')
            print('  ' + str(ast))
            limit = Evaluator(max_any_step=1)
            ast = ast.evaluate(limit)
            if is_value_term(ast):
                break
            i += 1
        print('Result:')
        print('  ' + str(ast))
        self.assertEqual(i, 4) # U-, B$, B+, B$

if __name__ == '__main__':
    unittest.main()