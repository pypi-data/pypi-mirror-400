import os

def do_it(fn        :str,
          repo_id   :str,
          repo_url  :str,
          a_group_id:str,
          a_id      :str,
          a_version :str,
          packaging='jar'):

    os.system('mvn -X deploy:deploy-file {}'.format(' '.join((

        f'-Dfile={fn}',
        f'-Dpackaging={packaging}',
        f'-DrepositoryId={repo_id}',
        f'-Durl={repo_url}',
        f'-DgroupId={a_group_id}', 
        f'-DartifactId={a_id}',
        f'-Dversion={a_version}',

    ))))


def main():

    import argparse

    class A:

        FILE              = 'f'
        REPOSITORY_ID     = 'repoid'
        REPOSITORY_URL    = 'repourl'
        ARTIFACT_GROUP_ID = 'artgr'
        ARTIFACT_ID       = 'artid'
        ARTIFACT_VERSION  = 'artv'

    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description='Upload a jar to a Maven artifactory')
    p.add_argument(f'{A.FILE}',
                   help='file to deploy')
    p.add_argument(f'{A.REPOSITORY_ID}',
                   help='destination repository ID')
    p.add_argument(f'{A.REPOSITORY_URL}',
                   help='destination repository URL')
    p.add_argument(f'{A.ARTIFACT_GROUP_ID}',
                   help='file artifact group ID')
    p.add_argument(f'{A.ARTIFACT_ID}',
                   help='file artifact ID')
    p.add_argument(f'{A.ARTIFACT_VERSION}',
                   help='file artifact version')
    get = p.parse_args().__getattribute__
    do_it(fn       =get(A.FILE),
         repo_id   =get(A.REPOSITORY_ID),
         repo_url  =get(A.REPOSITORY_URL),
         a_group_id=get(A.ARTIFACT_GROUP_ID),
         a_id      =get(A.ARTIFACT_ID),
         a_version =get(A.ARTIFACT_VERSION))

if __name__ == '__main__': main()