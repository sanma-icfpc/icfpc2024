import unittest
from icfp import icfp2ascii, reduce_extended_icfp
from icfp_peria import encrypt, I_encode

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
single_base4_decode_0to3 := L! ? B= I! v! SF ? B= I" v! SL ? B= I# v! SO S>

# using
#   v# -> f
#   v$ -> n
#   v% -> i
decodegen := L# L$ L% B. ( $single_base4_decode_0to3 B% v% I% ) ( ? B= v$ I" ( S ) ( B$ ( B$ v# B- v$ I" ) ( B/ v% I% )

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

# 何もしない
main := B$ $Z $decodegen
factorial := B$ $Z $factgen
#main := $Y $factgen
#main := $Z $stopgen
'''

def compress_lambdaman_base4(problem_num, path):
    '''lambdamanの回答であるpath(RRRUUDLD..みたいなやつ)に評価されるような短いICFPを生成する
    path: RULDで構成された文字列
    returns: ICFPの式で、評価するとpathになる
    '''
    if False:
        # 自明な解
        result = 'S' + encrypt(path)
    else:
        encoded_int = base4_decode(path)
        print(f'ORIGINAL PATH LENGTH: {len(path)}')
        print()
        arg = 'I' + I_encode(encoded_int)
        print(f'ENCODED PATH(LENGTH={len(arg)}): {arg}')
        print()
        print(arg.count('\n'))
        print()
        preamble = encrypt(f'solve lambdaman{problem_num} ')
        func = reduce_extended_icfp(program, 'factorial')
        print('FACTORIAL 5:')
        print(f'B$ {func} I&')
        print()
        result = f'B. S{preamble} B$ {func} {arg}'
    print(f'COMPRESSED({len(result)}):', result)
    #print('EVALUATE:', icfp2ascii(result))

    #assert icfp2ascii(result) == path, "compression failed!"
    return result

class TestICFPCompression(unittest.TestCase):
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

    def test_icfp_decodegen(self):
        program_icfp = reduce_extended_icfp(program)
        #icfp2ascii(program_icfp)


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
    #unittest.main()

    lambdaman17 = "DDDDDDDDDDDUUULUUUUUUUUULUUUUUUULLLLLDDDDDDDDDDDDDDUUURUUUUUURDDDDDDURUUUUUUULLLLDDDLUUDLDDDDDLLLUUUURRRDDDDRRRRRRRURDRRDDDDRRUUDDDDDULLLUUUUUUUUULUUUULRRUUUUUUUULLLUUUUUUUUUUUUUUUUUUUUUULUUUUULUUUUUUUUUUUUUUDDDDDLLLLUUUUUUUUULUULLLUUUUUUULLLLLDDDDDDDDDDDDDDDLLLUUUUUUUDRRRRRRRRDDDDDDDDUUUUUULLLLLUUUURURDRURDRRRRDDDDDRDDDDDDRRRRRLDDDDLDDDDDDDDDDDDDDDDDDDDLUUUUUUUUUUUULUUUUUUUUUDDLDDDLUUUULDDDDDLUULDDDDDDLUUUUUUULDDDDDDDDDDRUULULUUUULLUUUUUDDLDDDDDDDLRRUUUDRDDDDDDDDDDDLLLLLUUUULDLULUUUUUUUUULUUUUUULDDDDDDRRDRDURRRRLLLLLDLLLLDDDLLLDDDDDDDDDDDDDDDDLLLLDLLLLDDDDDDDDDUUUUUUUUULLLLLLLLDDDDULLLLLDDDLLLLUUUUUURRRRRUUUUUURUUULLUUUUULLRRRRRRDDDDDDDDLURRRRRDDRRRRRURRRRRRUUULLUURRRRRRDDDDDDRUUUUUUUUULRRDDRUURDDDDDDDDDLUULUURRRRRRDDDLULDDDDLLLLLUURULLLULDLLDDDLLLLLLRRRRRRRRRRRUURRRRUURRDDURRURDRURRRRRUUUUUUUURRRUUUUULDDDRRUUUUUDRRRRRDDDDDRDDDDDDDDDDDDDDDDDDDLUUUUUUUUUUUUUUUUULLLUUUULUDDDDDDDDDDDDDDLLUUUURRRUUUULLUUULDDRDDLLLLLLLLLLLLLLLLLLLDLDDLLLDRDRRRRRRRRDDDDRRRRRUUDDDDRRRRRUUUUUURRRRRRURRRRRRUUUUUURDDDDDDDDDDLUUURRUUUUUUURUUULLLUUUUUUULLUUULLDDLDRRDDRRRRUURDDRUURDDDUURRRRURDDDDDLUUURRUUUURURDDLRRUURDDDDDDDDLLLUULDDRDDDDDDDDDDDDDDDDDUUUUUULLUUUUUUUUUDLDDDDDDDDULULUUUUUUUUULRRLDDDDDLLULDDDDDDDDDDLUDDDDDDLDLULUURULLLLULDDDDDDDDDDDDDLLLLUUUUULLRRRRUUUUUURRRLDDRDDDDDDRUUDRRDDUUUURLLLLLULLLLRRDDDURRRRURRUURRURUUUUURRLUUUURUUURDDDRUUUUURRRURURRDRURDDDRRRRRUUUULDDLUUDLDLUUUUUUUUUUUUDRRRDDDDDRUUUUUUUUUUUUUUUULLLLDDRRRRRDRURDDDDDDDDDDDDDDLUULDDRRRURUUUUUUUUUUUUULRRRRRLLLLLLDDDDLLRRDDDDRDRDDDRDDLRUURRRRRRDDDDDDDDDDDRRRRRRUUUURUUUURRRRDDDDDDDDDDUUUUUULLLLDDDDDDDDDDLLLLLDDDDDDDDDRDDDDDDDDDDLLLLULULDDLUULDDDDDDDDDLLLLLDDDDDDLLLLLDDDDDRRRRRRRRRRDDDDDDLLLLLRRRRRRRRRRRDDDDDDUUURUUUUULLLLLLLLLLLLLLLLLLDDDDDDDDDDUUULLLLLLLLUUUULLLLLLLLDLULDDDDDDDULLLLLLUUULLDDDDDDDDDDDDDDDDDDDDLRRRUUUULRDDDDRRDDDDDDDDDDLUUUUUUULLLLRRRRRRRRRRRDDDDDDDDDLLUUUUUULLLLDDRDDRUURDDDDDDDDDRRRUURRRDDDDDDDUUULLLUURRRUURRRUUUUUUUUUUUULLLUUUDLRRRRRDDDRRRUULLRRRRLLLLLDLDDDDDDDDDDDDDDDDLLLLLLUULLLUUUUURUUUURUULLLLLUUUUUURRLLLLLLUUUUUUUUURURUUUUUUDDLLLLLRRRDDDDLRRRDRRRLLLUUUUUUUUUUURLLLLLRRRRDDDRRRRRRUUUUULURRRRRRRRRRRDDDDRRRRRRRRRLUUUUUUURRRRRRRRRRRUUUURRRUUUUUUDDDDDDRRRLLLLLLDDDDRRRRRRRRDRURDRURDLLLLLDDDRRRRLLLLLUULLLLLLUUUUUULLLLLLLLLLUUUUURRRRRUUUUUURRRRRUUUUUUULLLUUUURRRLLLDDRRLLDDDDDDUUUURRRRRRRRRRRUUUUURRRLLLUUUUULUUUUUUUUURRRRRUUUUUULLLLLLLUUUUUUUUUUULLLLLLLDLLLLLLUUUULLLDDDDDRLLLLRRRDDRRRRRRRRRRRRDDLLLLDDLLLLUURRRLLLLLDLLLLLLDDDDDRRRRRRLLLLLLDDDLLLULLLLLLLLLLLLLLLLLDDDDDLULDLLULDLURRRUUUUUUUUUULUUUUUUUUUULLLLDDDDLLLLLLULLUUUUULLUUUUUUUUUURRRRRRRLLLLLLLDDDDDRLUUUUURRRRRRRRUUURRRUURRRRRUUUUUUURRRRRDDRRUUURUUUUUDDDDDDDDRUUURDDDRUUURDDDDDDDDDRRUULUUUUUUUUUUUDDDDDDRRRRDDDLLLLDDRDDRRDDDDDRRRRUUULLUULRRRRLLLDDRRDDRDRURDRURDLLLLLLLLLUUUUULLLLUUUUUULLLLLUULLLLLLLLLLLLDDDDDDDDDLLLDDDLLLLLLLLDDDDDDDDDDRRRDDDDDRDDLLLLDDDLLLDDDDDDDDLLDDDLLLLLLDLLLLLUULLLLUUL"
    with open('lambdaman17_compress.txt', 'w') as fo:
        fo.write(compress_lambdaman_base4(17, lambdaman17))