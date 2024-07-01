#!/usr/bin/env python3

import re
import z3
import sys

def efficient8():
    solver = z3.Solver()

    terms = []
    for line in sys.stdin:
        if line.strip() == "":
            break
        vs = [re.sub('[^!|x0123456789]', '', x.strip()) for x in line.split(' & ')]
        terms.extend(vs)
    # print(terms)

    xs = []
    for t in terms:
        vs = re.sub('!', '', t).split('|')
        xs.extend(vs)
    xs = list(set(xs))
    xs.sort(key=lambda x: int(x[1:]))
    xs = [z3.Bool(x) for x in xs]
    # print(xs)

    def find(x):
        for v in xs:
            if x == str(v):
                return v
        return None

    def convert(x):
        name = x[1:] if x[0] == '!' else x
        v = find(name)
        return v == (x[0] == 'x')

    for t in terms:
        vs = list(map(convert , t.split('|')))
        ps = z3.Or(vs)
        print(ps)
        solver.add(ps)

    if solver.check() == z3.unsat:
        print("UNSAT")
        return

    print("Guarantee to have a solution!")

    assign = {}
    for x in reversed(xs):
        a = None
        for v in (False, True):
            solver.push()
            solver.add(x == v)
            if solver.check() == z3.sat:
                a = v
                solver.pop(1)
                break
            solver.pop(1)
        if a is None:
            print(f"Error for {x}")
            return
        solver.add(x == a)
        assign[str(x)] = 1 if a else 0

    print(assign)

    value = 0
    for x in reversed(xs):
        v = assign[str(x)]
        print(v, end='')
        value = value * 2 + v
    print()
    print(value)


def efficient9():
    reverse = True
    solver = z3.Solver()

    terms = []
    for line in sys.stdin:
        if line.strip() == "":
            break
        vs = [re.sub('[^!=x0123456789]', '', x.strip()) for x in line.split(' & ')]
        terms.extend(vs)
    # print(terms)

    xs = []
    for t in terms:
        x, y = re.sub('!', '', t).split('=')
        if 'x' in x:
            xs.append(x)
        if 'x' in y:
            xs.append(y)
    xs = list(set(xs))
    xs.sort(reverse=reverse, key=lambda x: int(x[1:]))
    xs = [z3.Int(x) for x in xs]
    for x in xs:
        ps = z3.Or([x == v for v in range(10)])
        # print(ps)
        solver.add(ps)
    # print(xs)

    def find(x):
        for v in xs:
            if x == str(v):
                return v
        return int(x) - 1

    assigned = {}
    for t in terms:
        x, y = re.sub('!', '', t).split('=')
        x = find(x)
        y = find(y)
        if '!' in t:
            solver.add(x != y)
        else:
            solver.add(x == y)
        if type(y) is int and '!' not in t:
            assigned[str(x)] = y

    if solver.check() == z3.unsat:
        print("UNSAT")
        return

    print("Guarantee to have a solution!")

    assign = assigned.copy()
    i = len(xs) - 1
    di = -1
    while i >= 0:
        x = xs[i]
        name = str(x)
        if name in assigned:
            i += di
            continue

        a = None
        for v in range(assign.get(name, -1) + 1, 9):
            solver.push()
            solver.add(x == v)
            if solver.check() == z3.sat:
                a = v
                break
            solver.pop(1)
        if a is None:
            # print(f"No valid solution for {name}")
            solver.pop(1)
            if name in assign:
                del assign[name]
            i += 1
            di = 1
            continue
        assign[name] = a
        i -= 1
        di = -1
        # print(assign)

    print(assign)

    value = 0
    for x in reversed(xs):
        v = assign[str(x)]
        print(v, end='')
        value = value * 9 + v
    print()
    print(value)
    n = value
    icfp = ''
    while n > 0:
        icfp = chr(n % 94 + 33) + icfp
        n //= 94
    print(icfp)

def main():
    # efficient8()
    efficient9()

if __name__ == '__main__':
    main()
