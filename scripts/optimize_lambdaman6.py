def length(recursive, multiply, initial):
    program = 'B$ Lf ' + 'B$ vf ' * recursive + 'S' + 'L' * initial + ' Lx ' + 'B. ' * (multiply - 1) + 'vx ' * multiply
    return len(program), initial * multiply ** recursive

best = None
for r in range(1, 10):
    for m in range(2, 20):
        for i in range(1, 50):
            program_size, answer_length = length(r, m, i)
            if answer_length >= 199:
                if best is None or best[0] > program_size:
                    print(f'update best (program size {program_size}), r={r}, m={m}, i={i}')
                    best = program_size, r, m, i

program_size, r, m, i = best
print(f'best (program size {program_size}), r={r}, m={m}, i={i}')