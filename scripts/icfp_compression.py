import unittest
from icfp import icfp2ascii, reduce_extended_icfp
from icfp_peria import encrypt, int2icfp

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

def my_int2icfp(i):
    result = []
    while i > 0:
        result.append(chr(i % 94 + 33))
        i //= 94
    return ''.join(reversed(result))

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
        arg = 'I' + my_int2icfp(encoded_int)
        print(f'ENCODED PATH(LENGTH={len(arg)}): {arg}')
        print()
        print(arg.count('\n'))
        print()
        preamble = encrypt(f'solve lambdaman{problem_num} ')
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
        decodegen := L# L$ L% B. ( $single_base4_decode_0to3 B% v" I% ) ( ? B= v$ I" ( S ) ( B$ ( B$ v# B- v$ I" ) ( B/ v% I% )

        # Z = lambda f: (lambda x: f (lambda y: x(x)(y)))(lambda x: f (lambda y: x(x)(y)))
        # using
        #   vf
        #   vx
        #   vy
        Z := Lf Lx B$ vf Ly B$ B$ vx vx vy Lx B$ vf Ly B$ B$ vx vx vy
        main := $Z $decodegen
        '''
        func = reduce_extended_icfp(program)
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
        decodegen := L# L$ L% B. ( $single_base4_decode_0to3 B% v" I% ) ( ? B= v$ I" ( S ) ( B$ ( B$ v# B- v$ I" ) ( B/ v% I% )

        # Z = lambda f: (lambda x: f (lambda y: x(x)(y)))(lambda x: f (lambda y: x(x)(y)))
        # using
        #   vf
        #   vx
        #   vy
        Z := Lf Lx B$ vf Ly B$ B$ vx vx vy Lx B$ vf Ly B$ B$ vx vx vy
        decode := $Z $decodegen
        main := B$ $decode IcO
        '''
        program_icfp = reduce_extended_icfp(program)
        icfp2ascii(program_icfp)


    def test_base4_python_lambda(self):
        '''PythonでZコンビネータを使ってbase4 decode'''
        Z = lambda f: (lambda x: f (lambda y: x(x)(y)))(lambda x: f (lambda y: x(x)(y)))
        decodegen = lambda f: (lambda n: (lambda i: 'LRUD'[i % 4] + ('' if n == 1 else f(n - 1)(i // 4))))
        decode = Z(decodegen)

        encoded_int = base4_decode('LRUD')
        self.assertEqual(decode(4)(encoded_int), 'LRUD')


if __name__ == '__main__':
    #unittest.main()

    lambdaman17 = "DDDDDDDDDDDUUULUUUUUUUUULUUUUUUULLLLLDDDDDDDDDDDDDDUUURUUUUUURDDDDDDURUUUUUUULLLLDDDLUUDLDDDDDLLLUUUURRRDDDDRRRRRRRURDRRDDDDRRUUDDDDDULLLUUUUUUUUULUUUULRRUUUUUUUULLLUUUUUUUUUUUUUUUUUUUUUULUUUUULUUUUUUUUUUUUUUDDDDDLLLLUUUUUUUUULUULLLUUUUUUULLLLLDDDDDDDDDDDDDDDLLLUUUUUUUDRRRRRRRRDDDDDDDDUUUUUULLLLLUUUURURDRURDRRRRDDDDDRDDDDDDRRRRRLDDDDLDDDDDDDDDDDDDDDDDDDDLUUUUUUUUUUUULUUUUUUUUUDDLDDDLUUUULDDDDDLUULDDDDDDLUUUUUUULDDDDDDDDDDRUULULUUUULLUUUUUDDLDDDDDDDLRRUUUDRDDDDDDDDDDDLLLLLUUUULDLULUUUUUUUUULUUUUUULDDDDDDRRDRDURRRRLLLLLDLLLLDDDLLLDDDDDDDDDDDDDDDDLLLLDLLLLDDDDDDDDDUUUUUUUUULLLLLLLLDDDDULLLLLDDDLLLLUUUUUURRRRRUUUUUURUUULLUUUUULLRRRRRRDDDDDDDDLURRRRRDDRRRRRURRRRRRUUULLUURRRRRRDDDDDDRUUUUUUUUULRRDDRUURDDDDDDDDDLUULUURRRRRRDDDLULDDDDLLLLLUURULLLULDLLDDDLLLLLLRRRRRRRRRRRUURRRRUURRDDURRURDRURRRRRUUUUUUUURRRUUUUULDDDRRUUUUUDRRRRRDDDDDRDDDDDDDDDDDDDDDDDDDLUUUUUUUUUUUUUUUUULLLUUUULUDDDDDDDDDDDDDDLLUUUURRRUUUULLUUULDDRDDLLLLLLLLLLLLLLLLLLLDLDDLLLDRDRRRRRRRRDDDDRRRRRUUDDDDRRRRRUUUUUURRRRRRURRRRRRUUUUUURDDDDDDDDDDLUUURRUUUUUUURUUULLLUUUUUUULLUUULLDDLDRRDDRRRRUURDDRUURDDDUURRRRURDDDDDLUUURRUUUURURDDLRRUURDDDDDDDDLLLUULDDRDDDDDDDDDDDDDDDDDUUUUUULLUUUUUUUUUDLDDDDDDDDULULUUUUUUUUULRRLDDDDDLLULDDDDDDDDDDLUDDDDDDLDLULUURULLLLULDDDDDDDDDDDDDLLLLUUUUULLRRRRUUUUUURRRLDDRDDDDDDRUUDRRDDUUUURLLLLLULLLLRRDDDURRRRURRUURRURUUUUURRLUUUURUUURDDDRUUUUURRRURURRDRURDDDRRRRRUUUULDDLUUDLDLUUUUUUUUUUUUDRRRDDDDDRUUUUUUUUUUUUUUUULLLLDDRRRRRDRURDDDDDDDDDDDDDDLUULDDRRRURUUUUUUUUUUUUULRRRRRLLLLLLDDDDLLRRDDDDRDRDDDRDDLRUURRRRRRDDDDDDDDDDDRRRRRRUUUURUUUURRRRDDDDDDDDDDUUUUUULLLLDDDDDDDDDDLLLLLDDDDDDDDDRDDDDDDDDDDLLLLULULDDLUULDDDDDDDDDLLLLLDDDDDDLLLLLDDDDDRRRRRRRRRRDDDDDDLLLLLRRRRRRRRRRRDDDDDDUUURUUUUULLLLLLLLLLLLLLLLLLDDDDDDDDDDUUULLLLLLLLUUUULLLLLLLLDLULDDDDDDDULLLLLLUUULLDDDDDDDDDDDDDDDDDDDDLRRRUUUULRDDDDRRDDDDDDDDDDLUUUUUUULLLLRRRRRRRRRRRDDDDDDDDDLLUUUUUULLLLDDRDDRUURDDDDDDDDDRRRUURRRDDDDDDDUUULLLUURRRUURRRUUUUUUUUUUUULLLUUUDLRRRRRDDDRRRUULLRRRRLLLLLDLDDDDDDDDDDDDDDDDLLLLLLUULLLUUUUURUUUURUULLLLLUUUUUURRLLLLLLUUUUUUUUURURUUUUUUDDLLLLLRRRDDDDLRRRDRRRLLLUUUUUUUUUUURLLLLLRRRRDDDRRRRRRUUUUULURRRRRRRRRRRDDDDRRRRRRRRRLUUUUUUURRRRRRRRRRRUUUURRRUUUUUUDDDDDDRRRLLLLLLDDDDRRRRRRRRDRURDRURDLLLLLDDDRRRRLLLLLUULLLLLLUUUUUULLLLLLLLLLUUUUURRRRRUUUUUURRRRRUUUUUUULLLUUUURRRLLLDDRRLLDDDDDDUUUURRRRRRRRRRRUUUUURRRLLLUUUUULUUUUUUUUURRRRRUUUUUULLLLLLLUUUUUUUUUUULLLLLLLDLLLLLLUUUULLLDDDDDRLLLLRRRDDRRRRRRRRRRRRDDLLLLDDLLLLUURRRLLLLLDLLLLLLDDDDDRRRRRRLLLLLLDDDLLLULLLLLLLLLLLLLLLLLDDDDDLULDLLULDLURRRUUUUUUUUUULUUUUUUUUUULLLLDDDDLLLLLLULLUUUUULLUUUUUUUUUURRRRRRRLLLLLLLDDDDDRLUUUUURRRRRRRRUUURRRUURRRRRUUUUUUURRRRRDDRRUUURUUUUUDDDDDDDDRUUURDDDRUUURDDDDDDDDDRRUULUUUUUUUUUUUDDDDDDRRRRDDDLLLLDDRDDRRDDDDDRRRRUUULLUULRRRRLLLDDRRDDRDRURDRURDLLLLLLLLLUUUUULLLLUUUUUULLLLLUULLLLLLLLLLLLDDDDDDDDDLLLDDDLLLLLLLLDDDDDDDDDDRRRDDDDDRDDLLLLDDDLLLDDDDDDDDLLDDDLLLLLLDLLLLLUULLLLUUL"
    with open('lambdaman17_compress.txt', 'w') as fo:
        fo.write(compress_lambdaman_base4(17, lambdaman17))