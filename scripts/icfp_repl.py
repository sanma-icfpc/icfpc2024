
#!/usr/bin/env python3
import argparse
import colorama
import icfp
import icfp_peria

try:
    import readline
except ImportError:
    # pip install pyreadline3 (do not forget the 3!)
    import pyreadline3 as readline

def print_system(s, end='\n'):
    print(colorama.Back.BLUE + colorama.Fore.WHITE + s + colorama.Style.RESET_ALL, end=end)

def S(s):
    return 'S' + icfp.encrypt(s)

def trim_message(s):
    s = s.replace('\n\nYou scored some points for using the echo service!\n', '')
    return s

def repl(verbose=False):
    while True:
        print(colorama.Back.GREEN + colorama.Fore.WHITE + '!encstr <string>, !decstr <S-body>, !encint <int>, !decint <I-body>, !remB <boolean expr to evaluate on the remote server>, !remS, !remI as well.' + colorama.Style.RESET_ALL)
        print(colorama.Back.BLUE + colorama.Fore.WHITE + '> ', end='')
        try:
            command = input()
        except KeyboardInterrupt:
            break
        except EOFError:
            break
        finally:
            print(colorama.Style.RESET_ALL, end="")

        if command.startswith('!encstr '):
            print_system('ENCRYPTED STRING:')
            print(icfp.encrypt(command[len('!encstr '):]))
        elif command.startswith('!decstr '):
            print_system('DECRYPTED STRING:')
            print(icfp.decrypt(command[len('!decstr '):]))
        elif command.startswith('!encint '):
            print_system('ENCRYPTED INTERGER:')
            print(icfp_peria.I_encode(command[len('!encint '):]))
        elif command.startswith('!decint '):
            print_system('DECRYPTED INTEGER:')
            print(icfp_peria.I_decode(command[len('!decint '):]))
        elif command.startswith('!remB '):
            print_system('REMOTE EVAL(Boolean):')
            cmd = command[len('!remB '):]
            expr = f'B. {S("echo ")} ? {cmd} {S("true")} {S("false")}'
            print(trim_message(icfp.communicate(expr, verbose=False, send_translate=False, recv_translate=True)))
        elif command.startswith('!remS '):
            print_system('REMOTE EVAL(String):')
            cmd = command[len('!remS '):]
            expr = f'B. {S("echo ")} {cmd}'
            print(trim_message(icfp.communicate(expr, verbose=False, send_translate=False, recv_translate=True)))
        elif command.startswith('!remI '):
            print_system('REMOTE EVAL(Integer):')
            cmd = command[len('!remI '):]
            expr = f'B. {S("echo ")} U$ {cmd}'
            print(icfp_peria.icfp2int(trim_message(icfp.communicate(expr, verbose=False, send_translate=False, recv_translate=True))))
        else:
            # local evaluation
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

