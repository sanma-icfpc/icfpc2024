
#!/usr/bin/env python3
import argparse
import colorama
import icfp

try:
    import readline
except ImportError:
    # pip install pyreadline3 (do not forget the 3!)
    import pyreadline3 as readline


def repl(verbose=False):
    while True:
        print(colorama.Back.BLUE + colorama.Fore.WHITE + 'ICFP> ', end="")
        try:
            command = input()
        except KeyboardInterrupt:
            break
        except EOFError:
            break
        finally:
            print(colorama.Style.RESET_ALL, end="")
        try:
            response = icfp.icfp2ascii(command, verbose)
        except:
            print('ERROR.')
            continue
        print('EVALUATED> ' + response)


if __name__ == '__main__':
    colorama.init(autoreset=False)
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', action='store_true', default=False)
    args = parser.parse_args()
    repl(args.verbose)

