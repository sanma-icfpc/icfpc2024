import os
import re
import sys
import tty
import termios
import colorama
from icfp_peria import encrypt, I_encode
import icfp_compression

def clear_screen():
    if os.name == 'nt':  # Windowsの場合
        os.system('cls')
    else:  # Unix/Linux/Macの場合
        os.system('clear')

def move_cursor_top_left():
    sys.stdout.write('\033[H')

def move_cursor_up_left(lines=1):
    sys.stdout.write(f'\x1b[{lines}A')
    sys.stdout.write(f'\x1b[G')

def getch():
    # 標準入力のファイルディスクリプタを取得
    fd = sys.stdin.fileno()
    
    # 現在の端末設定を取得し、保存
    old_settings = termios.tcgetattr(fd)
    
    try:
        # ttyモードをrawに設定
        tty.setraw(sys.stdin.fileno())
        
        # 1文字だけ読み込む
        ch = sys.stdin.read(1)
        if ch == '\x1b':  # エスケープシーケンスの開始
            ch += sys.stdin.read(2)  # 矢印キーは3文字から成るため、残り2文字を読む
    
    finally:
        # 端末設定を元に戻す
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    return ch

def editor(problem_file):
    board = []
    cx, cy = 0, 0
    with open(problem_file, 'r') as fi:
        for line in fi.readlines():
            line = line.strip()
            if line:
                board.append(list(line))
                L = line.find('L')
                if L >= 0:
                    cx, cy = L, len(board) - 1
    H, W = len(board), len(board[0])
    
    def print_board(board):
        for row in board:
            print(''.join(row)
                  .replace('L', colorama.Back.GREEN + colorama.Fore.WHITE + 'L' + colorama.Style.RESET_ALL)
                  .replace('.', colorama.Back.BLUE + colorama.Fore.WHITE + '.' + colorama.Style.RESET_ALL)
                  .replace('#', colorama.Back.WHITE + colorama.Fore.WHITE + '#' + colorama.Style.RESET_ALL)
                  )

    t = 0
    force_emit = False
    sequence = []
    undo_list = []
    redo_list = []
    def move(dx, dy, direction):
        if 0 <= cx + dx < W and 0 <= cy + dy < H:
            src = board[cy][cx]
            dst = board[cy + dy][cx + dx]
            if force_emit or dst != '#':
                def undo_move():
                    nonlocal cx, cy
                    sequence.pop(-1)
                    if dst != '#':
                        cx -= dx
                        cy -= dy
                        board[cy][cx] = src
                        board[cy + dy][cx + dx] = dst
                def redo_move():
                    nonlocal cx, cy, direction
                    sequence.append(direction)
                    if dst != '#':
                        board[cy][cx] = ' '
                        board[cy + dy][cx + dx] = 'L'
                        cx += dx
                        cy += dy
                redo_move()
                undo_list.append((t, undo_move, redo_move))
                redo_list.clear()
                return 1 # step time
        return 0 # stop time

    def undo():
        nonlocal t
        if len(undo_list) > 0:
            t, fundo, fredo = undo_list.pop(-1)
            redo_list.append((t, fundo, fredo))
            fundo()
    def redo():
        nonlocal t
        if len(redo_list) > 0:
            t, fundo, fredo = redo_list.pop(-1)
            undo_list.append((t, fundo, fredo))
            fredo()

    rotation = 'CW'
    clear_screen()
    while True:
        move_cursor_top_left()
        print_board(board)

        # clear below the board
        info_area_size = 20
        for i in range(info_area_size):
            print(' '*120)
        move_cursor_up_left(info_area_size)

        print(f'Time: {t}, Direction: {rotation}')
        print('Move: WASD  Undo/Redo: <>  Toggle force emit: T')
        print(f'Sequence({len(sequence):3d}): {"".join(sequence)}')
        if force_emit:
            print(colorama.Back.BLUE + colorama.Fore.WHITE + f'Force emit regardless of the walls')
        if '.' in ''.join(''.join(line) for line in board):
            print(colorama.Back.RED + colorama.Fore.WHITE + 'INCOMPLETE')
        ch = getch()
        if ch == '\x03': # Ctrl-C
            break
        if ch == '\x04': # Ctrl-D
            break
        if ch.lower() == 't':
            force_emit = not force_emit
        if ch.lower() == 'w' or ch == '\x1b[A': t += move( 0, -1, 'U')
        if ch.lower() == 'a' or ch == '\x1b[D': t += move(-1,  0, 'L')
        if ch.lower() == 's' or ch == '\x1b[B': t += move( 0,  1, 'D')
        if ch.lower() == 'd' or ch == '\x1b[C': t += move( 1,  0, 'R')
        if ch.lower() == '<': undo()
        if ch.lower() == '>': redo()
    
    mo = re.search('(\d+)', os.path.basename(problem_file))
    if mo:
        num = mo.groups()[0]
    else:
        num = ''

    path = ''.join(sequence)
    out_file = f'lambdaman{num}.manual.txt'
    with open(out_file, 'w') as fo:
        fo.write('solve lambdaman{num} {path}')

    problem = 'lambdaman'
    base = 4
    org = 'S' + encrypt(f'solve lambdaman{num} {path}')
    compressed_basex = icfp_compression.lambdaman_base4.compress_solution('lambdaman', num, path)
    compressed_rle = icfp_compression.lambdaman_rle.compress_solution('lambdaman', num, path)
    print(f'{problem}{num} org={len(org)} basex={len(compressed_basex)} rle={len(compressed_rle)}')
    if len(org) > len(compressed_basex) and len(compressed_rle) > len(compressed_basex):
        print(f'{problem}{num} BASEX IMPROVES {len(org)}->{len(compressed_basex)}')
        with open(os.path.splitext(out_file)[0] + f'.base{base}.txt', 'w') as fo:
            fo.write(compressed_basex)
    elif len(org) > len(compressed_rle) and len(compressed_basex) > len(compressed_rle):
        print(f'{problem}{num} RLE IMPROVES {len(org)}->{len(compressed_rle)}')
        with open(os.path.splitext(out_file)[0] + '.rle.txt', 'w') as fo:
            fo.write(compressed_rle)

if __name__ == '__main__':
    colorama.init(True)
    editor(sys.argv[1])