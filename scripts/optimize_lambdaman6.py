import sys
import icfp

def generate_shortest_for_repeat(char, min_repeat, fixed_initial=None):
    enc_char = icfp.encrypt(char)

    def length(recursive, multiply, initial):
        program = 'B$ Lf ' + 'B$ vf ' * recursive + 'S' + enc_char * initial + ' Lx ' + 'B. ' * (multiply - 1) + 'vx ' * multiply
        return len(program), initial * multiply ** recursive, program

    best = None
    for r in range(1, 10):
        for m in range(2, 20):
            if fixed_initial:
                ilist = [fixed_initial]
            else:
                ilist = range(1, 50)
            for i in ilist:
                program_size, answer_length, program = length(r, m, i)
                if answer_length >= min_repeat:
                    if best is None or best[0] > program_size:
                        best = program_size, r, m, i, program

    program_size, r, m, i, program = best
    print(f'best (program size {program_size}), r={r}, m={m}, i={i}')
    return program, program_size, r, m, i

if int(sys.argv[1]) == 6:
    program, program_size, r, m, i = generate_shortest_for_repeat('R', 199)
    print(program)

if int(sys.argv[1]) == 9:
    print(generate_shortest_for_repeat('L', 50, fixed_initial=1))

    program = f'''
repeat6_to_50 := Ly B$ Lf B$ vf B$ vf vy Lx B. B. vx vx vx 
repeat_50 := Ly B$ Lf B$ vf B$ vf B$ vf vy Lx B. B. B. vx vx vx vx
cell_gen := Lr B. B. B$ vr S{icfp.encrypt('R')} B$ vr S{icfp.encrypt('L')} S{icfp.encrypt('D')}
cell := B$ $cell_gen $repeat_50
all := B$ ( La B$ va B$ $cell_gen va ) $repeat_50
'''
    main = icfp.reduce_extended_icfp(program, 'all')
    print(len(main))
    print(main)