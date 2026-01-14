import enum
import os
import os.path
import typing

from jl95.pytools import ppjava

GUIDE_FILE_NAME = '__pp__.py'

def do_it(wd:str):

    if not os.path.exists(os.path.join(wd,'pom.xml')):

        print('The given directory does not look like maven - no pom.xml found\nStop')
        return

    for dp,rdnn,rfnn in os.walk(wd):

        for fn in map(lambda rfn: os.path.join(dp,rfn), rfnn):

            if not fn.endswith('.java'): continue
            try:
            
                ppjava.do_it(fn)
            
            except Exception as ex:

                print(f'Error on preprocessing file {repr(fn)}: {ex}')
                continue
    
if __name__ == '__main__':

    import argparse

    p = argparse.ArgumentParser(description='pre-processor for Maven project directories\nAll Java source files in there will be processed.\n(EXPERIMENTAL)')
    p.add_argument('--wd',
                   help   ='working directory - default to current',
                   default='.')
    args = p.parse_args()
    do_it(fn=args.wd)
