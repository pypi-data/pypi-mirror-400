import os
import os.path
import typing

from jl95.pytools import swjava
from jl95.pytools import swxml

def do_it(wd     :str,
          enable :typing.Callable[[str],bool],
          disable:typing.Callable[[str],bool]):

    pom_path = os.path.join(wd,'pom.xml')
    src_path = os.path.join(wd,'src')
    for path,emsg in (
        (pom_path,'no project \'pom.xml\''  ,),
        (src_path,'no source folder \'src\'',),
    ):
        if not os.path.exists(path):

            raise Exception(f'not a valid Maven project directory{emsg}')

    swxml.do_it(fn     =pom_path,
                enable =enable,
                disable=disable)
    for dp,rdnn,rfnn in os.walk(top=src_path):

        for rfn in rfnn:

            if not rfn.endswith('.java'): continue
            fn = os.path.join(dp,rfn)
            fb = swjava.do_it(fn     =fn,
                              enable =enable,
                              disable=disable)
            if fb.enabled:

                print(f'{repr(os.path.relpath(fn,start=wd))} - enabled {repr(fb.enabled)}')

            if fb.disabled:
                  
                  print(f'{repr(os.path.relpath(fn,start=wd))} - disabled {repr(fb.disabled)}')

if __name__ == '__main__':

    import argparse

    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, 
                                description    =f'Switch code blocks ON or OFF in all Java source files inside a Maven project directory\nThis tool is meant to help maintain cross-JDK projects.\nSee the help for \'swjava\'.')
    p.add_argument('--wd',
                   help   ='working directory - default to current',
                   default='.')
    p.add_argument('--on',
                   help   ='blocks to enable (switch ON)',
                   nargs  ='+',
                   default=[])
    p.add_argument('--off',
                   help   ='blocks to disable (switch OFF)',
                   nargs  ='+',
                   default=[])
    args = p.parse_args()
    do_it(wd     =args.wd,
          enable =set(args.on) .__contains__,
          disable=set(args.off).__contains__)