import argparse
import json
import os
import os.path
import shutil
import subprocess
import typing
import uuid
import xml.etree.ElementTree as et

from jl95.pytools import maven
from jl95.batteries import *

DEFAULT_DEST_RELATIVE = 'target'

class ErrorHandlers:

    def __init__(self):

        self.on_fail_to_open_pom    :typing.Callable[[str,                 Exception],None] = lambda pom_path, ex: None
        self.on_fail_to_det_jar_path:typing.Callable[[maven.PomDependency, Exception],None] = lambda dep     , ex: None
        self.on_fail_to_copy_jar    :typing.Callable[[str,                 Exception],None] = lambda jar_path, ex: None
        self.on_fail_to_det_pom_path:typing.Callable[[maven.PomDependency, Exception],None] = lambda dep     , ex: None

def do_it(pom_path:str,
          dest:str,
          error_handlers:ErrorHandlers|None=None):
    
    if error_handlers is None:
        error_handlers = ErrorHandlers()
    os.makedirs(dest, exist_ok=True)
    try:
        pom = maven.Pom(pom_path)
    except Exception as ex:
        error_handlers.on_fail_to_open_pom(pom_path, ex)
        return
    for dep in pom.dependencies():
        try:
            jar_path = pom.eval(maven.get_local_jar_path(dep))
        except Exception as ex:
            error_handlers.on_fail_to_det_jar_path(dep, ex)
        else:
            try:
                shutil.copy(jar_path, dest)
            except Exception as ex: 
                error_handlers.on_fail_to_copy_jar(jar_path, ex)
        try:
            pom_path = pom.eval(maven.get_local_pom_path(dep))
        except Exception as ex:
            error_handlers.on_fail_to_det_pom_path(dep, ex)
        else:
            do_it(pom_path, dest, error_handlers=error_handlers)

def main():

    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description='Download and build Maven dependencies from their corresponding Github projects')
    class A:

        PROJECT_DIR  = 'wd'
        DESTINATION_DIR = 'dest'
        SHUSH = 'shush'
    
    p.add_argument(f'--{A.PROJECT_DIR}',
                   help=f'project / working dir\nDefault: current directory')
    p.add_argument(f'--{A.DESTINATION_DIR}',
                   help=f'directory to which to copy the dependencies (Java jar files)\nIf omitted, it is assumed as {DEFAULT_DEST_RELATIVE} under the project directory.')
    p.add_argument(f'--{A.SHUSH}',
                   help=f'do not print errors',
                   action='store_true')

    # parse args
    get = p.parse_args().__getattribute__
    proj_dir    = get(A.PROJECT_DIR) if get(A.PROJECT_DIR) is not None else os.getcwd()
    pom_path    = maven.get_pom_path_by_project_dir(proj_dir)
    target_path = get(A.DESTINATION_DIR) if get(A.DESTINATION_DIR) is not None else os.path.join(proj_dir, DEFAULT_DEST_RELATIVE)
    shush       = get(A.SHUSH)

    # do it
    error_handlers = ErrorHandlers()
    if not shush:
        error_handlers.on_fail_to_open_pom     = lambda pom_path, ex: print(f'Failed to open POM at {pom_path}: {ex}')
        error_handlers.on_fail_to_det_jar_path = lambda dep,      ex: print(f'Failed to determine JAR path for {dep}: {ex}')
        error_handlers.on_fail_to_copy_jar     = lambda jar_path, ex: print(f'Failed to copy JAR for {jar_path}: {ex}')
        error_handlers.on_fail_to_det_pom_path = lambda dep,      ex: print(f'Failed to determine POM path for {dep}: {ex}')
    do_it(pom_path,
          target_path,
          error_handlers=error_handlers)

if __name__ == '__main__': main()