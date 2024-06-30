import os
import re
import sys
import unittest
from icfp import icfp2ascii, reduce_extended_icfp
from icfp_peria import encrypt, I_encode

def find_max_run_length(path):
    i = 0
    run_length = 0
    max_run_length = 0
    path = path[::-1] + '$' # sentinel
    while i < len(path):
        if i == 0 or path[i - 1] == path[i]:
            # continue
            run_length += 1
        else:
            # emit. note that the sentinel path[i] == '$' also comes here.
            max_run_length = max(max_run_length, run_length)
            run_length = 1
        i += 1
    return max_run_length

def rle_encode(path):
    '''RRRRLLUUDDのようなpathをRLEエンコードする。方向は2ビット、ラン長さは盤面から決める固定ビット。
    (固定ビット長, ラン数, 圧縮後数値) を返す
    下位ビットがpath[0]に対応する'''
    k = find_max_run_length(path)
    run_bits = 1
    while k >= 2**run_bits:
        run_bits += 1
    result = 0
    i = 0
    run_length = 0
    num_runs = 0
    path = path[::-1] + '$' # sentinel
    while i < len(path):
        if i == 0 or path[i - 1] == path[i]:
            # continue
            run_length += 1
        else:
            # emit. note that the sentinel path[i] == '$' also comes here.
            c = {'L':0, 'R': 1, 'U': 2, 'D': 3}[path[i - 1]]
            result = result * (2**(run_bits + 2)) + run_length * 4 + c
            num_runs += 1
            run_length = 1
        i += 1
    return run_bits, num_runs, result

    #result = result * (2 + run_bits) + {'L':0, 'R': 1, 'U': 2, 'D': 3}[c] + 2 * (run)

def rle_decode(run_bits, num_runs, rle_int):
    '''RLE化された巨大整数rle_intをデコードしてLRUD文字列のパスを返す
    あとでこの関数をICFP化する'''
    result = ''
    SIZE_RUN_LENGTH = 2**run_bits
    SIZE_RUN = 2**(2 + run_bits)
    for i in range(num_runs):
        idx = rle_int % 4
        run_length = (rle_int // 4) % SIZE_RUN_LENGTH
        rle_int //= SIZE_RUN
        result += 'LRUD'[idx] * run_length
    return result

def rle_decode_recursive(run_bits, num_runs, rle_int):
    '''RLE化された巨大整数rle_intをデコードしてLRUD文字列のパスを返す
    あとでこの関数をICFP化する'''
    SIZE_RUN_LENGTH = 2**run_bits
    SIZE_RUN = 2**(2 + run_bits)
    if num_runs == 0:
        return ''
    else:
        idx = rle_int % 4
        run_length = (rle_int // 4) % SIZE_RUN_LENGTH
        return 'LRUD'[idx] * run_length + rle_decode_recursive(run_bits, num_runs - 1, rle_int // SIZE_RUN)

def repeat_recursive(c, num):
    if num == 0:
        return ''
    else: 
        return c + repeat_recursive(c, num - 1)

def base4_encode(n_chars, path_int):
    '''L:0, R:1, U:2, D:3 のアルファベットのBASE4でpath_intをエンコードする'''
    result = ''
    for i in range(n_chars):
        idx = path_int % 4
        path_int //= 4
        result += 'LRUD'[idx]
    return result

def base4_encode_recursive(n_chars, path_int):
    if n_chars == 1:
        return 'LRUD'[path_int]
    else:
        return 'LRUD'[path_int % 4] + base4_encode_recursive(n_chars - 1, path_int // 4)

def base4_decode(base4_str):
    result = 0
    for c in base4_str[::-1]:
        result = result * 4 + {'L':0, 'R': 1, 'U': 2, 'D': 3}[c]
    return result

program = '''
# 'LRUD'[i % 4]
# using
#   v! : i or i % 4
single_base4_decode := L! ? B= I! B% v! I% SF ? B= I" B% v! I% SL ? B= I# B% v! I% SO S>
single_base4_decode_0to3_switch := L! ? B= I! v! SF ? B= I" v! SL ? B= I# v! SO S>
single_base4_decode_0to3 := L! BT I" BD v! SFLO>

# decodegen = lambda f: (lambda n: (lambda i: 'LRUD'[i % 4] + ('' if n == 1 else f(n - 1)(i // 4))))
# using
#   v# -> f
#   v$ -> n
#   v% -> i
#decodegen := L# ( L$ ( L% B. ( B$ $single_base4_decode_0to3 B% v% I% ) ( ? ( B= v$ I" ) ( S ) ( B$ ( B$ v# B- v$ I" ) ( B/ v% I% ) ) )
decodegen := L# ( L$ ( L% B. ( BT I" BD B% v% I% SFLO> ) ( ? ( B= v$ I" ) ( S ) ( B$ ( B$ v# B- v$ I" ) ( B/ v% I% ) ) )


# repeatgen = lambda h: (lambda c: (lambda m: '' if m == 0 else c + h(c)(m - 1)))
# using
#   vh
#   vc
#   vm
repeatgen := Lh ( Lc ( Lm ? B= I! vm S B. vc B$ B$ vh vc B- vm I" ) )
repeat := B$ $Z $repeatgen

# RLE
# rle_decodegen = lambda g: (lambda n: (lambda i: '' if n == 0 else repeat('LRUD'[i % 4], i // 4 % SIZE_RUN_LENGTH) + g(n - 1, i // SIZE_RUN))))
# using
#   vg
#   vn
#   vi
rle_decodegen := Lg ( Ln ( Li ? ( B= I! vn ) ( S ) ( B. ( B$ B$ $repeat ( BT I" BD B% vi I% SFLO> ) ( B% B/ vi I% $SIZE_RUN_LENGTH ) ) ( B$ B$ vg B- vn I" B/ vi $SIZE_RUN ) ) )
rle_decode := B$ $Z $rle_decodegen

# using
#  vc -> f
#  vd -> n
factgen := Lc Ld ? B= I! vd I" B* vd B$ vc B- vd I"

# 常に停止する再帰
stopgen := Lc Ld I"

# Y combinator
Y := B$ ( Lf ( Lx B$ vf B$ vx vx ) ) ( Lx B$ vf B$ vx vx ) 

# Z = lambda f: (lambda x: f (lambda y: x(x)(y))) (lambda x: f (lambda y: x(x)(y)))
# def Z(f):
#     def Zx(x):
#         def Zy(y):
#             return x(x)(y)
#         return f(Zy)
#     return Zx(Zx)
# using
#   vf
#   vx
#   vy
#   va
#   vb
Z := Lf B$ ( Lx B$ vf ( Ly B$ ( B$ vx vx ) vy ) ) ( Lx B$ vf ( Ly B$ ( B$ vx vx ) vy ) ) 

factorial := B$ $Z $factgen
decode := B$ $Z $decodegen
#main := $Y $factgen
#main := $Z $stopgen
'''

def compress_lambdaman_base4(problem_num, path):
    '''lambdamanの回答であるpath(RRRUUDLD..みたいなやつ)に評価されるような短いICFPを生成する
    path: RULDで構成された文字列
    returns: ICFPの式で、評価するとpathになる
    '''
    encoded_int = base4_decode(path)
    print(f'[BASE4]ORIGINAL PATH LENGTH: {len(path)}')
    print()
    arg = 'I' + I_encode(encoded_int)
    print(f'[BASE4]ENCODED PATH(LENGTH={len(arg)}): {arg}')
    print()
    preamble = encrypt(f'solve lambdaman{problem_num} ')
    if False:
        func = reduce_extended_icfp(program, 'factorial')
        print('FACTORIAL 5:')
        print(f'B$ {func} I&')
        print()
    func = reduce_extended_icfp(program, 'decode')
    result = f'B. S{preamble} B$ B$ {func} I{I_encode(len(path))} {arg}'
    print(f'[BASE4]COMPRESSED({len(result)}):', result)
    return result

def compress_lambdaman_rle(problem_num, path):
    '''lambdamanの回答であるpath(RRRUUDLD..みたいなやつ)に評価されるような短いICFPを生成する
    path: RULDで構成された文字列
    returns: ICFPの式で、評価するとpathになる
    '''
    run_bits, num_runs, encoded_int = rle_encode(path)
    print(f'[RLE]ORIGINAL PATH LENGTH: {len(path)}')
    print()
    arg = 'I' + I_encode(encoded_int)
    print(f'[RLE]ENCODED PATH(LENGTH={len(arg)}): {arg}')
    print()
    preamble = encrypt(f'solve lambdaman{problem_num} ')
    SIZE_RUN_LENGTH = 2**run_bits
    SIZE_RUN = 2**(2 + run_bits)
    header = f'''
    SIZE_RUN_LENGTH := I{I_encode(SIZE_RUN_LENGTH)}
    SIZE_RUN := I{I_encode(SIZE_RUN)}
    '''
    print(f'[RLE] SIZE_RUN_LENGTH = {SIZE_RUN_LENGTH}')
    print(f'[RLE] SIZE_RUN = {SIZE_RUN}')
    func = reduce_extended_icfp(header + program, 'rle_decode')
    result = f'B. S{preamble} B$ B$ {func} I{I_encode(num_runs)} {arg}'
    print(f'[RLE]COMPRESSED({len(result)}):', result)
    return result

class TestICFPCompression(unittest.TestCase):
    def test_rle(self):
        self.assertEqual(rle_encode('RRUU'), (2, 2, 0b1010_1001))
        self.assertEqual(rle_encode('RRUU'), (2, 2, 0b1010_1001))
        self.assertEqual(rle_decode(2, 2, 0b1010_1001), 'RRUU')
        self.assertEqual(rle_decode_recursive(2, 2, 0b1010_1001), 'RRUU')

        path = 'RRLLUDRRRRRRDULLLLURDUDU'
        num_bits, num_runs, rle_int = rle_encode(path)
        self.assertEqual(rle_decode_recursive(num_bits, num_runs, rle_int), path)

    def test_repeat_recursive(self):
        self.assertEqual(repeat_recursive('A', 5), 'AAAAA')

    def test_base4(self):
        self.assertEqual(base4_encode(4, 0b11100100), 'LRUD')
        self.assertEqual(base4_encode_recursive(4, 0b11100100), 'LRUD')
        self.assertEqual(base4_decode('LRUD'), 0b11100100)

    def test_simple_lambda(self):
        print(icfp2ascii('B$ L! v! I!'))
        pass

    def test_compress_lambdaman_base4(self):
        #compress_lambdaman_base4(1, 'RRRRRRRRRLLLLLLLLDDDDDDDDUUUUUU')
        pass

    def test_reduce_extended_icfp(self):
        reduced = reduce_extended_icfp('''
        myfunc := L! U- v!
        main := B$ $myfunc I#
        ''')
        self.assertEqual(reduced, 'B$ L! U- v! I#')

    def test_lrud(self):
        self.assertEqual(encrypt('LRUD'), 'FLO>')

    def test_base4_python_lambda(self):
        '''PythonでZコンビネータを使ってbase4 decode'''
        #Z = lambda f: (lambda x: f (lambda y: x(x)(y)))(lambda x: f (lambda y: x(x)(y)))
        def Z(f):
            def Zx(x):
                def Zy(y):
                    return x(x)(y)
                return f(Zy)
            return Zx(Zx)

        decodegen = lambda f: (lambda n: (lambda i: 'LRUD'[i % 4] + ('' if n == 1 else f(n - 1)(i // 4))))
        decode = Z(decodegen)

        encoded_int = base4_decode('LRUD')
        self.assertEqual(decode(4)(encoded_int), 'LRUD')


if __name__ == '__main__':
    if len(sys.argv) == 2:
        # python icfp_compression.py <sol>.txt
        # -> <sol>.base4.txt
        # -> <sol>.rle.txt
        # <sol>.text is like:
        # solve lambdaman1 UDLLLDURRRRRURR
        with open(sys.argv[1], 'r') as fi:
            org = fi.read().strip()
            mo = re.match(r'solve lambdaman(\d+) ([LRUD]+)', org)
            assert mo is not None
            num, path = mo.groups()
            num = int(num)
            compressed_base4 = compress_lambdaman_base4(num, path)
            compressed_rle = compress_lambdaman_rle(num, path)
            print(f'lambdaman{num} org={len(org)} base4={len(compressed_base4)} rle={len(compressed_rle)}')
            if len(org) > len(compressed_base4) and len(compressed_rle) > len(compressed_base4):
                print(f'lambdaman{num} BASE4 IMPROVES {len(org)}->{len(compressed_base4)}')
                with open(os.path.splitext(sys.argv[1])[0] + '.base4.txt', 'w') as fo:
                    fo.write(compressed_base4)
            elif len(org) > len(compressed_rle) and len(compressed_base4) > len(compressed_rle):
                print(f'lambdaman{num} RLE IMPROVES {len(org)}->{len(compressed_rle)}')
                with open(os.path.splitext(sys.argv[1])[0] + '.rle.txt', 'w') as fo:
                    fo.write(compressed_rle)
            else:
                print(f'lambdaman{num} NO IMPROVEMENT')
    else:
        #unittest.main()

        #lambdaman17 = "DDDDDDDDDDDUUULUUUUUUUUULUUUUUUULLLLLDDDDDDDDDDDDDDUUURUUUUUURDDDDDDURUUUUUUULLLLDDDLUUDLDDDDDLLLUUUURRRDDDDRRRRRRRURDRRDDDDRRUUDDDDDULLLUUUUUUUUULUUUULRRUUUUUUUULLLUUUUUUUUUUUUUUUUUUUUUULUUUUULUUUUUUUUUUUUUUDDDDDLLLLUUUUUUUUULUULLLUUUUUUULLLLLDDDDDDDDDDDDDDDLLLUUUUUUUDRRRRRRRRDDDDDDDDUUUUUULLLLLUUUURURDRURDRRRRDDDDDRDDDDDDRRRRRLDDDDLDDDDDDDDDDDDDDDDDDDDLUUUUUUUUUUUULUUUUUUUUUDDLDDDLUUUULDDDDDLUULDDDDDDLUUUUUUULDDDDDDDDDDRUULULUUUULLUUUUUDDLDDDDDDDLRRUUUDRDDDDDDDDDDDLLLLLUUUULDLULUUUUUUUUULUUUUUULDDDDDDRRDRDURRRRLLLLLDLLLLDDDLLLDDDDDDDDDDDDDDDDLLLLDLLLLDDDDDDDDDUUUUUUUUULLLLLLLLDDDDULLLLLDDDLLLLUUUUUURRRRRUUUUUURUUULLUUUUULLRRRRRRDDDDDDDDLURRRRRDDRRRRRURRRRRRUUULLUURRRRRRDDDDDDRUUUUUUUUULRRDDRUURDDDDDDDDDLUULUURRRRRRDDDLULDDDDLLLLLUURULLLULDLLDDDLLLLLLRRRRRRRRRRRUURRRRUURRDDURRURDRURRRRRUUUUUUUURRRUUUUULDDDRRUUUUUDRRRRRDDDDDRDDDDDDDDDDDDDDDDDDDLUUUUUUUUUUUUUUUUULLLUUUULUDDDDDDDDDDDDDDLLUUUURRRUUUULLUUULDDRDDLLLLLLLLLLLLLLLLLLLDLDDLLLDRDRRRRRRRRDDDDRRRRRUUDDDDRRRRRUUUUUURRRRRRURRRRRRUUUUUURDDDDDDDDDDLUUURRUUUUUUURUUULLLUUUUUUULLUUULLDDLDRRDDRRRRUURDDRUURDDDUURRRRURDDDDDLUUURRUUUURURDDLRRUURDDDDDDDDLLLUULDDRDDDDDDDDDDDDDDDDDUUUUUULLUUUUUUUUUDLDDDDDDDDULULUUUUUUUUULRRLDDDDDLLULDDDDDDDDDDLUDDDDDDLDLULUURULLLLULDDDDDDDDDDDDDLLLLUUUUULLRRRRUUUUUURRRLDDRDDDDDDRUUDRRDDUUUURLLLLLULLLLRRDDDURRRRURRUURRURUUUUURRLUUUURUUURDDDRUUUUURRRURURRDRURDDDRRRRRUUUULDDLUUDLDLUUUUUUUUUUUUDRRRDDDDDRUUUUUUUUUUUUUUUULLLLDDRRRRRDRURDDDDDDDDDDDDDDLUULDDRRRURUUUUUUUUUUUUULRRRRRLLLLLLDDDDLLRRDDDDRDRDDDRDDLRUURRRRRRDDDDDDDDDDDRRRRRRUUUURUUUURRRRDDDDDDDDDDUUUUUULLLLDDDDDDDDDDLLLLLDDDDDDDDDRDDDDDDDDDDLLLLULULDDLUULDDDDDDDDDLLLLLDDDDDDLLLLLDDDDDRRRRRRRRRRDDDDDDLLLLLRRRRRRRRRRRDDDDDDUUURUUUUULLLLLLLLLLLLLLLLLLDDDDDDDDDDUUULLLLLLLLUUUULLLLLLLLDLULDDDDDDDULLLLLLUUULLDDDDDDDDDDDDDDDDDDDDLRRRUUUULRDDDDRRDDDDDDDDDDLUUUUUUULLLLRRRRRRRRRRRDDDDDDDDDLLUUUUUULLLLDDRDDRUURDDDDDDDDDRRRUURRRDDDDDDDUUULLLUURRRUURRRUUUUUUUUUUUULLLUUUDLRRRRRDDDRRRUULLRRRRLLLLLDLDDDDDDDDDDDDDDDDLLLLLLUULLLUUUUURUUUURUULLLLLUUUUUURRLLLLLLUUUUUUUUURURUUUUUUDDLLLLLRRRDDDDLRRRDRRRLLLUUUUUUUUUUURLLLLLRRRRDDDRRRRRRUUUUULURRRRRRRRRRRDDDDRRRRRRRRRLUUUUUUURRRRRRRRRRRUUUURRRUUUUUUDDDDDDRRRLLLLLLDDDDRRRRRRRRDRURDRURDLLLLLDDDRRRRLLLLLUULLLLLLUUUUUULLLLLLLLLLUUUUURRRRRUUUUUURRRRRUUUUUUULLLUUUURRRLLLDDRRLLDDDDDDUUUURRRRRRRRRRRUUUUURRRLLLUUUUULUUUUUUUUURRRRRUUUUUULLLLLLLUUUUUUUUUUULLLLLLLDLLLLLLUUUULLLDDDDDRLLLLRRRDDRRRRRRRRRRRRDDLLLLDDLLLLUURRRLLLLLDLLLLLLDDDDDRRRRRRLLLLLLDDDLLLULLLLLLLLLLLLLLLLLDDDDDLULDLLULDLURRRUUUUUUUUUULUUUUUUUUUULLLLDDDDLLLLLLULLUUUUULLUUUUUUUUUURRRRRRRLLLLLLLDDDDDRLUUUUURRRRRRRRUUURRRUURRRRRUUUUUUURRRRRDDRRUUURUUUUUDDDDDDDDRUUURDDDRUUURDDDDDDDDDRRUULUUUUUUUUUUUDDDDDDRRRRDDDLLLLDDRDDRRDDDDDRRRRUUULLUULRRRRLLLDDRRDDRDRURDRURDLLLLLLLLLUUUUULLLLUUUUUULLLLLUULLLLLLLLLLLLDDDDDDDDDLLLDDDLLLLLLLLDDDDDDDDDDRRRDDDDDRDDLLLLDDDLLLDDDDDDDDLLDDDLLLLLLDLLLLLUULLLLUUL"
        #with open('lambdaman17_compress.txt', 'w') as fo:
        #    fo.write(compress_lambdaman_base4(17, lambdaman17))

        lambdaman1 = "UDLLLDURRRRRURR"
        #with open('lambdaman1_compress_base4.txt', 'w') as fo:
        #    fo.write(compress_lambdaman_base4(1, lambdaman1))
        with open('lambdaman1_compress_rle.txt', 'w') as fo:
            fo.write(compress_lambdaman_rle(1, lambdaman1))