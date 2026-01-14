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
from jl95.pytools.envlib.vars.git  import GIT
from jl95.pytools.envlib.vars.java import MAVEN
from jl95.batteries import *
from jl95.batteries import os

DEPSMAP_FILENAME_STANDARD = 'depsmap.json'

class DepInfo:

    def __init__(self,x):

        self.url    :str = x['url']
        self.version:typing.Callable[[str],str] \
                         = eval(x['version']) if 'version' in x else lambda vn: f'v{vn}'

class DepsInstaller:

    def __init__(self, project_dir:str|None=None):

        self._project_dir = project_dir if project_dir is not None else os.getcwd()
        self._pom = maven.Pom.from_project_dir(self._project_dir)

    def install_deps_by_map(self, deps_map:dict[tuple[str,str],dict[str,typing.Any]],force=False):

        dependencies = list(self._pom.dependencies())
        print(f'Dependencies:\n{'\n'.join(f'  {repr(dep)}' for dep in dependencies)}')
        for dep in dependencies:

            is_installed = maven.is_installed(dep)
            to_install = force or not is_installed
            dep_key = (dep.group_id,dep.artifact_id)
            dep_key_str = ':'.join(dep_key)
            if dep_key not in deps_map: # not to look up
                
                print(f'{dep_key_str} NOT found in dependencies map - continue')
                continue

            print(f'{dep_key_str} found in dependencies map')
            dep_info = DepInfo(deps_map[dep_key])
            temp_dir_name = os.path.join(os.TEMP_DIR, f'_dep-{dep.group_id}-{dep.artifact_id}-{str(uuid.uuid4())}')
            git = GIT  .get()
            mvn = MAVEN.get()
            os.makedirs(temp_dir_name)
            wd = os.getcwd()
            try:

                subprocess.run([git,'clone',dep_info.url,temp_dir_name,
                                '--branch',dep_info.version(dep.version),
                                '--depth','1',
                                '--quiet'],
                            shell=True)
                os.chdir(temp_dir_name)
                if DEPSMAP_FILENAME_STANDARD in os.listdir():

                    print(f'Dependency map file found for {dep_key_str} - installing its dependencies recursively')
                    DepsInstaller(os.getcwd()).install_deps(force=force)
                    os.chdir(temp_dir_name) # ensure in the right dir

                if to_install:
                    
                    print('Installing dependency:', dep_key_str)
                    print('Current working dir:', os.getcwd())
                    subprocess.run([mvn,'install',
                                    '-Dmaven.test.skip=true'],
                                   shell=True)
                    
                elif is_installed:

                    print(f'{repr(dep)} already installed')

            finally:

                os.chdir(temp_dir_name) # ensure in the right dir
                subprocess.run([git,'clean',
                                '-ff'],shell=True)
                os.chdir(wd)

    def install_deps_by_mapfile_path(self, depsmap_path, force=False):

        with open(depsmap_path, mode='r') as fr:

            deps_map_raw:dict[str,typing.Any] = json.load(fr)
            deps_map = dict((tuple(k.split(':')[:2]),v) for k,v in deps_map_raw.items())

        self.install_deps_by_map(deps_map,force=force)

    def install_deps(self, force=False):

        self.install_deps_by_mapfile_path(os.path.join(self._project_dir, DEPSMAP_FILENAME_STANDARD),force=force)

def main():

    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description='Download and build Maven dependencies from their corresponding Github projects')
    class A:
        DEPS_MAPFILE  = 'mapfile'
        PROJECT_DIR   = 'wd'
        FORCE_INSTALL = 'force'
    class Defaults:
        DEPS_MAPFILE = DEPSMAP_FILENAME_STANDARD
    p.add_argument(f'--{A.PROJECT_DIR}',
                   help=f'Project / working dir\nDefault: current directory')
    p.add_argument(f'--{A.DEPS_MAPFILE}',
                   help=f'Path of dependencies map file to consider, relative to working directory, if different from the standard ({Defaults.DEPS_MAPFILE})',
                   default=Defaults.DEPS_MAPFILE)
    p.add_argument(f'--{A.FORCE_INSTALL}',
                   help=f'Force install dependencies that appear to be installed already',
                   action='store_true')
    # parse
    get = p.parse_args().__getattribute__
    project_dir       = get(A.PROJECT_DIR)
    deps_mapfile_path = get(A.DEPS_MAPFILE)
    force             = get(A.FORCE_INSTALL)
    # do it
    DepsInstaller(project_dir).install_deps_by_mapfile_path(depsmap_path=deps_mapfile_path,force=force)

if __name__ == '__main__': main()