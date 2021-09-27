import sys

from compilador.lexicon.lexicon import Lexicon


if __name__ == '__main__':
    if len(sys.argv) < 2:
        filepath = 'dados/exemplo.lalg.txt'
    else:
        filepath = sys.argv[1]

    code = Lexicon(filepath).parse()

    print('Finished parsing!')
    print('Generated code:\n')
    print('\n'.join(f'{line:>5} | {code}' for line, code in enumerate(code)))
