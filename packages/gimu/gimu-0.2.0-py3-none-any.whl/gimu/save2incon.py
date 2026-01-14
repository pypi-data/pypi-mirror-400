""" use: save2incon a.save b.incon [-reset_kcyc] """

from sys import *
from t2incons import *

def main():
    if len(argv) < 2:
        print('use: save2incon a.save b.incon [-reset_kcyc] [-reset_porosity]')
        exit(1)

    readFrom = argv[1]
    saveTo = argv[2]

    if len(argv) > 3:
        opts = argv[3:]
    else:
        opts = []
    inc = t2incon(readFrom)

    for opt in opts:
        if opt == '-reset_kcyc':
            inc.timing['kcyc'] = 1
            inc.timing['iter'] = 1
        if opt == '-reset_porosity':
            inc.porosity = None

    inc.write(saveTo)

if __name__ == '__main__':
    main()
