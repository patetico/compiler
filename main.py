import sys

from compilador.lexicon.object_lexicon import ObjectLexicon


if __name__ == '__main__':
    if len(sys.argv) < 2:
        filepath = 'dados/exemplo.lalg.txt'
    else:
        filepath = sys.argv[1]

    code = ObjectLexicon(filepath).parse()

    print('Finished parsing!')
    print('Generated code:\n')
    print('\n'.join(f'{line:>5} | {code}' for line, code in enumerate(code)))

    print('\nExecuting...\n')
    Interpreter(code, '> ').run()
