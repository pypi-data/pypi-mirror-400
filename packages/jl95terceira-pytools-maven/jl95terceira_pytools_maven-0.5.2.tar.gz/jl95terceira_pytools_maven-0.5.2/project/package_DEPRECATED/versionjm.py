import os
import os.path
import xml.etree.ElementTree as et

from jl95terceira.pytools import version as version_
from jl95terceira.pytools import maven

def _get_version(wd:str):

    return maven.Pom(os.path.join(wd,'pom.xml')).version()

def _get_version_and_print(wd:str):

    version = _get_version(wd)
    print('Java Maven project version: '+version)
    #sha256={path: hashf.Hasher(hashlib.sha256).of(os.path.join(wd,path)) for path in ('pom.xml','src')}
    return version

def main():

    version_.main_given_version(description='Version a Java Maven project with a git tag\nThe version number will be read from the project file (pom.xml).',
                                version_getter=lambda wd,agetter: _get_version_and_print(wd))

if __name__ == '__main__': main()
