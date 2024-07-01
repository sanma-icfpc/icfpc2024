import os
import re
import sys
import unittest
import collections
from icfp import icfp2ascii, reduce_extended_icfp
from icfp_peria import encrypt, I_encode

program = '''
# 'LRUD'[i % 4]
# using
#   v! : i or i % 4
single_base4_decode := L! ? B= I! B% v! I% SF ? B= I" B% v! I% SL ? B= I# B% v! I% SO S>
single_base4_decode_0to3_switch := L! ? B= I! v! SF ? B= I" v! SL ? B= I# v! SO S>
single_base4_decode_0to3 := L! BT I" BD v! SFLO>

# basex_decodegen = lambda f: (lambda n: (lambda i: 'LRUD'[i % 4] + ('' if n == 1 else f(n - 1)(i // 4))))
# using
#   v# -> f
#   v$ -> n
#   v% -> i
#basex_decodegen := L# ( L$ ( L% B. ( B$ $single_base4_decode_0to3 B% v% I% ) ( ? ( B= v$ I" ) ( S ) ( B$ ( B$ v# B- v$ I" ) ( B/ v% I% ) ) )
# require
#  $CHARS
#  $N_CHARS
basex_decodegen := L# ( L$ ( L% B. ( BT I" BD B% v% $N_CHARS $CHARS ) ( ? ( B= v$ I" ) ( S ) ( B$ ( B$ v# B- v$ I" ) ( B/ v% $N_CHARS ) ) )


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
# require
#   $CHARS
#   $2_POW_CHAR_BITS
rle_decodegen := Lg ( Ln ( Li ? ( B= I! vn ) ( S ) ( B. ( B$ B$ $repeat ( BT I" BD B% vi $2_POW_CHAR_BITS $CHARS ) ( B% B/ vi $2_POW_CHAR_BITS $SIZE_RUN_LENGTH ) ) ( B$ B$ vg B- vn I" B/ vi $SIZE_RUN ) ) )

# using
#  vc -> f
#  vd -> n
factgen := Lc Ld ? B= I! vd I" B* vd B$ vc B- vd I"

# 常に停止する再帰
stopgen := Lc Ld I"

# Y combinator. call-by-name の場合はこれでOK
# Y = (λf . (λx . f (x x)) (λx . f (x x)))
#Y := Lf B$ ( Lx B$ vf B$ vx vx ) ( Lx B$ vf B$ vx vx )
# 更に短くできる
Y := Lf B$ Lz B! vz vz ( Lx B$ vf B$ vx vx )

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
# long version
#Z := Lf B$ ( Lx B$ vf ( Ly B$ ( B$ vx vx ) vy ) ) ( Lx B$ vf ( Ly B$ ( B$ vx vx ) vy ) ) 
# this is also acceptable
Z := Lf B$ Lz B$ vz vz ( Lx B$ vf ( Ly B$ ( B$ vx vx ) vy ) )

# recursive functions
rle_decode := B$ $Y $rle_decodegen
factorial := B$ $Y $factgen
basex_decode := B$ $Y $basex_decodegen
'''

class LambdamanDangomushi(object):
    '''ダンゴムシのように右回り左回りを切り替えながら進む。それぞれの回り方は壁に当たることを前提に長めに歩く。
    右と左ないし右と左の切り替えをランレングス圧縮する。'''
    def __init__(self, stride):
        self.bits = 1 # 1文字を表現するのに必要なビット数
        self.chars = 'rl' # r: CW, l: CCW
        self.rev = dict((c, i) for i, c in enumerate(self.chars))
        self.stride = stride # stride=50のときCWはR50D50L50U50を基本単位とする

    def decode(self, run_bits, num_runs, rle_int):
        '''RLEされた整数値をLRUD..に展開する
        あとでこの関数をICFP化する'''
        result = ''
        SIZE_RUN_LENGTH = 2**run_bits
        SIZE_RUN = 2**(self.bits + run_bits)
        R = self.stride * 4
        t = 0
        previdx = 0
        for i in range(num_runs):
            idx = rle_int % (2**self.bits)
            run_length = (rle_int >> self.bits) % SIZE_RUN_LENGTH
            rle_int //= SIZE_RUN
            if previdx != idx:
                t = (R - 1 - t % R) - (R - 1 - t % R) % 4
            for j in range(run_length):
                k = t // self.stride % 4
                result += ['RDLU', 'LDRU'][idx][k]
                t += 1
            previdx = idx
        return result

class RLE(object):
    def __init__(self, bits, chars):
        self.bits = bits
        self.chars = chars
        assert '$' not in chars # to use as the sentinel
        self.rev = dict((c, i) for i, c in enumerate(chars))

    @staticmethod
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

    def rle_encode(self, path, run_bits=None):
        '''RRRRLLUUDDのようなpathをRLEエンコードする。方向は2ビット、ラン長さは盤面から決める固定ビット。
        (固定ビット長, ラン数, 圧縮後数値) を返す
        下位ビットがpath[0]に対応する'''
        if run_bits is None:
            max_run_length = RLE.find_max_run_length(path)
            run_bits = 1
            while max_run_length >= 2**run_bits:
                run_bits += 1
        max_possible_run_length = 2**run_bits - 1

        result = 0
        i = 0
        run_length = 0
        num_runs = 0
        path = path[::-1] + '$' # sentinel
        while i < len(path):
            if (i == 0 or path[i - 1] == path[i]) and run_length < max_possible_run_length:
                # continue
                run_length += 1
            else:
                # emit. note that the sentinel path[i] == '$' also comes here.
                c = self.rev[path[i - 1]]
                result = result * (2**(run_bits + self.bits)) + (run_length << self.bits) + c
                num_runs += 1
                run_length = 1
            i += 1
        return run_bits, num_runs, result

    def rle_encode_optimal(self, path):
        '''最短になるようなmax_run_lengthを探す'''
        max_run_length = RLE.find_max_run_length(path)
        max_run_bits = 1
        while max_run_length >= 2**max_run_bits:
            max_run_bits += 1
        results = []
        for run_bits in range(2, max_run_bits + 1):
            _, num_runs, result = self.rle_encode(path, run_bits=run_bits)
            results.append((result, num_runs, run_bits))
        results.sort() # smallest result = shortest.
        result, num_runs, run_bits = results[0]
        return run_bits, num_runs, result

    def rle_decode(self, run_bits, num_runs, rle_int):
        '''RLE化された巨大整数rle_intをデコードしてLRUD文字列のパスを返す
        あとでこの関数をICFP化する'''
        result = ''
        SIZE_RUN_LENGTH = 2**run_bits
        SIZE_RUN = 2**(self.bits + run_bits)
        for i in range(num_runs):
            idx = rle_int % (2**self.bits)
            run_length = (rle_int >> self.bits) % SIZE_RUN_LENGTH
            rle_int //= SIZE_RUN
            result += self.chars[idx] * run_length
        return result

    def rle_decode_recursive(self, run_bits, num_runs, rle_int):
        '''RLE化された巨大整数rle_intをデコードしてLRUD文字列のパスを返す
        あとでこの関数をICFP化する'''
        SIZE_RUN_LENGTH = 2**run_bits
        SIZE_RUN = 2**(self.bits + run_bits)
        if num_runs == 0:
            return ''
        else:
            idx = rle_int % (2**self.bits)
            run_length = (rle_int >> self.bits) % SIZE_RUN_LENGTH
            return self.chars[idx] * run_length + self.rle_decode_recursive(run_bits, num_runs - 1, rle_int // SIZE_RUN)

    @staticmethod
    def repeat_recursive(c, num):
        if num == 0:
            return ''
        else: 
            return c + RLE.repeat_recursive(c, num - 1)

    def compress_solution(self, problem, problem_num, path):
        '''lambdamanの回答であるpath(RRRUUDLD..みたいなやつ)に評価されるような短いICFPを生成する
        path: RULDで構成された文字列
        returns: ICFPの式で、評価するとpathになる
        '''
        run_bits, num_runs, encoded_int = self.rle_encode_optimal(path)
        print(f'[RLE]ORIGINAL PATH LENGTH: {len(path)}')
        print()
        arg = 'I' + I_encode(encoded_int)
        print(f'[RLE]ENCODED PATH(LENGTH={len(arg)}): {arg}')
        print()
        preamble = encrypt(f'solve {problem}{problem_num} ')
        SIZE_RUN_LENGTH = 2**run_bits
        SIZE_RUN = 2**(self.bits + run_bits)
        header = f'''
        CHARS := S{encrypt(self.chars)}
        2_POW_CHAR_BITS := I{I_encode(2 ** self.bits)}
        SIZE_RUN_LENGTH := I{I_encode(SIZE_RUN_LENGTH)}
        SIZE_RUN := I{I_encode(SIZE_RUN)}
        '''
        print(f'[RLE] CHARS = {self.chars}')
        print(f'[RLE] 2_POW_CHAR_BITS = {2 ** self.bits}')
        print(f'[RLE] SIZE_RUN_LENGTH = {SIZE_RUN_LENGTH}')
        print(f'[RLE] SIZE_RUN = {SIZE_RUN}')
        func = reduce_extended_icfp(header + program, 'rle_decode')
        result = f'B. S{preamble} B$ B$ {func} I{I_encode(num_runs)} {arg}'
        print(f'[RLE]COMPRESSED({len(result)}):', result)
        return result

lambdaman_rle = RLE(2, 'LRUD')
spaceship_rle = RLE(4, '123456789')

class BaseX(object):
    def __init__(self, chars):
        self.alphabets = len(chars)
        self.chars = chars
        self.rev = dict((c, i) for i, c in enumerate(chars))

    def encode(self, n_chars, path_int):
        '''L:0, R:1, U:2, D:3 のアルファベットのBASE4でpath_intをエンコードする'''
        result = ''
        for i in range(n_chars):
            idx = path_int % self.alphabets
            path_int //= self.alphabets
            result += self.chars[idx]
        return result

    def encode_recursive(self, n_chars, path_int):
        if n_chars == 1:
            return self.chars[path_int]
        else:
            return self.chars[path_int % self.alphabets] + self.encode_recursive(n_chars - 1, path_int // self.alphabets)

    def decode(self, base4_str):
        result = 0
        for c in base4_str[::-1]:
            result = result * self.alphabets + self.rev[c]
        return result

    def compress_solution(self, problem, problem_num, path):
        '''lambdamanの回答であるpath(RRRUUDLD..みたいなやつ)に評価されるような短いICFPを生成する
        path: RULDで構成された文字列
        returns: ICFPの式で、評価するとpathになる
        '''
        encoded_int = self.decode(path)
        print(f'[BASEX]ORIGINAL PATH LENGTH: {len(path)}')
        print()
        arg = 'I' + I_encode(encoded_int)
        print(f'[BASEX]ENCODED PATH(LENGTH={len(arg)}): {arg}')
        print()
        preamble = encrypt(f'solve {problem}{problem_num} ')
        header = f'''
        CHARS := S{encrypt(self.chars)}
        N_CHARS := I{I_encode(self.alphabets)}
        '''
        print(f'[BASEX] CHARS = {self.chars}')
        print(f'[BASEX] N_CHARS = {self.alphabets}')
        func = reduce_extended_icfp(header + program, 'basex_decode')
        result = f'B. S{preamble} B$ B$ {func} I{I_encode(len(path))} {arg}'
        print(f'[BASEX]COMPRESSED({len(result)}):', result)
        return result

lambdaman_base4 = BaseX('LRUD')
spaceship_base9 = BaseX('123456789')

class TestLambdamanDangomushi(unittest.TestCase):
    def test_decode(self):
        dangomushi = LambdamanDangomushi(4)
        self.assertEqual(dangomushi.decode(run_bits=5, num_runs=1, rle_int=0b10001_0), 'RRRRDDDDLLLLUUUUR') # CW17
        self.assertEqual(dangomushi.decode(run_bits=5, num_runs=2, rle_int=0b10000_1_10010_0), 'RRRRDDDDLLLLUUUURR' + 'UUUULLLLDDDDRRRR') # CW18 + CCW16, CW R-> CCW U
        self.assertEqual(dangomushi.decode(run_bits=5, num_runs=2, rle_int=0b00010_1_00110_0), 'RRRRDD' + 'RR') # CW D->CCW R
        self.assertEqual(dangomushi.decode(run_bits=5, num_runs=2, rle_int=0b00010_1_01010_0), 'RRRRDDDDLL' + 'DD') # CW L->CCW D
        self.assertEqual(dangomushi.decode(run_bits=5, num_runs=2, rle_int=0b00010_1_01110_0), 'RRRRDDDDLLLLUU' + 'LL') # CW U->CCW L

class TestICFPCompression(unittest.TestCase):
    def test_rle(self):
        self.assertEqual(lambdaman_rle.rle_encode('RRUU'), (2, 2, 0b1010_1001))
        self.assertEqual(lambdaman_rle.rle_encode('RRUU'), (2, 2, 0b1010_1001))
        self.assertEqual(lambdaman_rle.rle_decode(2, 2, 0b1010_1001), 'RRUU')
        self.assertEqual(lambdaman_rle.rle_decode_recursive(2, 2, 0b1010_1001), 'RRUU')

        path = 'RRLLUDRRRRRRDULLLLURDUDU'
        num_bits, num_runs, rle_int = lambdaman_rle.rle_encode(path)
        self.assertEqual(lambdaman_rle.rle_decode_recursive(num_bits, num_runs, rle_int), path)

    def test_repeat_recursive(self):
        self.assertEqual(RLE.repeat_recursive('A', 5), 'AAAAA')

    def test_base4(self):
        self.assertEqual(lambdaman_base4.encode(4, 0b11100100), 'LRUD')
        self.assertEqual(lambdaman_base4.encode_recursive(4, 0b11100100), 'LRUD')
        self.assertEqual(lambdaman_base4.decode('LRUD'), 0b11100100)

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

        encoded_int = lambdaman_base4.decode('LRUD')
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
            if org.startswith('solve'):
                mo = re.match(r'solve (lambdaman|spaceship)(\d+)\s+(.+)', org)
                assert mo is not None
                problem, num, path = mo.groups()
            else:
                # solve .. がない場合は内容から判定
                mo = re.search(r'(lambdaman|spaceship)(\d+)', os.path.basename(sys.argv[1]))
                assert mo is not None
                _, num = mo.groups()
                if any([c in lambdaman_rle.chars for c in org]):
                    problem = 'lambdaman'
                    path = org
                    org = f'solve lambdaman{num}' + path
                elif any([c in spaceship_rle.chars for c in org]):
                    problem = 'spaceship'
                    path = org
                    org = f'solve spaceship{num}' + path
                else:
                    raise ValueError('failed to detect the problem type.')
            if problem == 'lambdaman':
                problem = 'lambdaman'
                rle = lambdaman_rle
                basex = lambdaman_base4
                base = 4
            elif problem == 'spaceship':
                problem = 'spaceship'
                rle = spaceship_rle
                basex = spaceship_base9
                base = 9
            else:
                raise ValueError('could not detect the problem type')
            num = int(num)
            print(f'PROBLEM: {problem}{num}')
            compressed_basex = basex.compress_solution(problem, num, path)
            compressed_rle = rle.compress_solution(problem, num, path)
            print(f'{problem}{num} org={len(org)} basex={len(compressed_basex)} rle={len(compressed_rle)}')
            if len(org) > len(compressed_basex) and len(compressed_rle) > len(compressed_basex):
                print(f'{problem}{num} BASEX IMPROVES {len(org)}->{len(compressed_basex)}')
                with open(os.path.splitext(sys.argv[1])[0] + f'.base{base}.txt', 'w') as fo:
                    fo.write(compressed_basex)
            elif len(org) > len(compressed_rle) and len(compressed_basex) > len(compressed_rle):
                print(f'{problem}{num} RLE IMPROVES {len(org)}->{len(compressed_rle)}')
                with open(os.path.splitext(sys.argv[1])[0] + '.rle.txt', 'w') as fo:
                    fo.write(compressed_rle)
            else:
                print(f'{problem}{num} NO IMPROVEMENT')
    else:
        unittest.main()

        #lambdaman17 = "DDDDDDDDDDDUUULUUUUUUUUULUUUUUUULLLLLDDDDDDDDDDDDDDUUURUUUUUURDDDDDDURUUUUUUULLLLDDDLUUDLDDDDDLLLUUUURRRDDDDRRRRRRRURDRRDDDDRRUUDDDDDULLLUUUUUUUUULUUUULRRUUUUUUUULLLUUUUUUUUUUUUUUUUUUUUUULUUUUULUUUUUUUUUUUUUUDDDDDLLLLUUUUUUUUULUULLLUUUUUUULLLLLDDDDDDDDDDDDDDDLLLUUUUUUUDRRRRRRRRDDDDDDDDUUUUUULLLLLUUUURURDRURDRRRRDDDDDRDDDDDDRRRRRLDDDDLDDDDDDDDDDDDDDDDDDDDLUUUUUUUUUUUULUUUUUUUUUDDLDDDLUUUULDDDDDLUULDDDDDDLUUUUUUULDDDDDDDDDDRUULULUUUULLUUUUUDDLDDDDDDDLRRUUUDRDDDDDDDDDDDLLLLLUUUULDLULUUUUUUUUULUUUUUULDDDDDDRRDRDURRRRLLLLLDLLLLDDDLLLDDDDDDDDDDDDDDDDLLLLDLLLLDDDDDDDDDUUUUUUUUULLLLLLLLDDDDULLLLLDDDLLLLUUUUUURRRRRUUUUUURUUULLUUUUULLRRRRRRDDDDDDDDLURRRRRDDRRRRRURRRRRRUUULLUURRRRRRDDDDDDRUUUUUUUUULRRDDRUURDDDDDDDDDLUULUURRRRRRDDDLULDDDDLLLLLUURULLLULDLLDDDLLLLLLRRRRRRRRRRRUURRRRUURRDDURRURDRURRRRRUUUUUUUURRRUUUUULDDDRRUUUUUDRRRRRDDDDDRDDDDDDDDDDDDDDDDDDDLUUUUUUUUUUUUUUUUULLLUUUULUDDDDDDDDDDDDDDLLUUUURRRUUUULLUUULDDRDDLLLLLLLLLLLLLLLLLLLDLDDLLLDRDRRRRRRRRDDDDRRRRRUUDDDDRRRRRUUUUUURRRRRRURRRRRRUUUUUURDDDDDDDDDDLUUURRUUUUUUURUUULLLUUUUUUULLUUULLDDLDRRDDRRRRUURDDRUURDDDUURRRRURDDDDDLUUURRUUUURURDDLRRUURDDDDDDDDLLLUULDDRDDDDDDDDDDDDDDDDDUUUUUULLUUUUUUUUUDLDDDDDDDDULULUUUUUUUUULRRLDDDDDLLULDDDDDDDDDDLUDDDDDDLDLULUURULLLLULDDDDDDDDDDDDDLLLLUUUUULLRRRRUUUUUURRRLDDRDDDDDDRUUDRRDDUUUURLLLLLULLLLRRDDDURRRRURRUURRURUUUUURRLUUUURUUURDDDRUUUUURRRURURRDRURDDDRRRRRUUUULDDLUUDLDLUUUUUUUUUUUUDRRRDDDDDRUUUUUUUUUUUUUUUULLLLDDRRRRRDRURDDDDDDDDDDDDDDLUULDDRRRURUUUUUUUUUUUUULRRRRRLLLLLLDDDDLLRRDDDDRDRDDDRDDLRUURRRRRRDDDDDDDDDDDRRRRRRUUUURUUUURRRRDDDDDDDDDDUUUUUULLLLDDDDDDDDDDLLLLLDDDDDDDDDRDDDDDDDDDDLLLLULULDDLUULDDDDDDDDDLLLLLDDDDDDLLLLLDDDDDRRRRRRRRRRDDDDDDLLLLLRRRRRRRRRRRDDDDDDUUURUUUUULLLLLLLLLLLLLLLLLLDDDDDDDDDDUUULLLLLLLLUUUULLLLLLLLDLULDDDDDDDULLLLLLUUULLDDDDDDDDDDDDDDDDDDDDLRRRUUUULRDDDDRRDDDDDDDDDDLUUUUUUULLLLRRRRRRRRRRRDDDDDDDDDLLUUUUUULLLLDDRDDRUURDDDDDDDDDRRRUURRRDDDDDDDUUULLLUURRRUURRRUUUUUUUUUUUULLLUUUDLRRRRRDDDRRRUULLRRRRLLLLLDLDDDDDDDDDDDDDDDDLLLLLLUULLLUUUUURUUUURUULLLLLUUUUUURRLLLLLLUUUUUUUUURURUUUUUUDDLLLLLRRRDDDDLRRRDRRRLLLUUUUUUUUUUURLLLLLRRRRDDDRRRRRRUUUUULURRRRRRRRRRRDDDDRRRRRRRRRLUUUUUUURRRRRRRRRRRUUUURRRUUUUUUDDDDDDRRRLLLLLLDDDDRRRRRRRRDRURDRURDLLLLLDDDRRRRLLLLLUULLLLLLUUUUUULLLLLLLLLLUUUUURRRRRUUUUUURRRRRUUUUUUULLLUUUURRRLLLDDRRLLDDDDDDUUUURRRRRRRRRRRUUUUURRRLLLUUUUULUUUUUUUUURRRRRUUUUUULLLLLLLUUUUUUUUUUULLLLLLLDLLLLLLUUUULLLDDDDDRLLLLRRRDDRRRRRRRRRRRRDDLLLLDDLLLLUURRRLLLLLDLLLLLLDDDDDRRRRRRLLLLLLDDDLLLULLLLLLLLLLLLLLLLLDDDDDLULDLLULDLURRRUUUUUUUUUULUUUUUUUUUULLLLDDDDLLLLLLULLUUUUULLUUUUUUUUUURRRRRRRLLLLLLLDDDDDRLUUUUURRRRRRRRUUURRRUURRRRRUUUUUUURRRRRDDRRUUURUUUUUDDDDDDDDRUUURDDDRUUURDDDDDDDDDRRUULUUUUUUUUUUUDDDDDDRRRRDDDLLLLDDRDDRRDDDDDRRRRUUULLUULRRRRLLLDDRRDDRDRURDRURDLLLLLLLLLUUUUULLLLUUUUUULLLLLUULLLLLLLLLLLLDDDDDDDDDLLLDDDLLLLLLLLDDDDDDDDDDRRRDDDDDRDDLLLLDDDLLLDDDDDDDDLLDDDLLLLLLDLLLLLUULLLLUUL"
        #with open('lambdaman17_compress.txt', 'w') as fo:
        #    fo.write(compress_lambdaman_base4(17, lambdaman17))

        lambdaman1 = "UDLLLDURRRRRURR"
        #with open('lambdaman1_compress_base4.txt', 'w') as fo:
        #    fo.write(compress_lambdaman_base4(1, lambdaman1))
        with open('lambdaman1_compress_rle.txt', 'w') as fo:
            fo.write(compress_lambdaman_rle(1, lambdaman1))