# TODO: switch to gitpython
# import git
import os
from subprocess import call
import sys

import utils

def config_error():
    cfg_err_str = 'config.py not properly configured.\nSee config.py.example.\nAborting.'
    print utils.red(cfg_err_str)
    sys.exit(1)

try:
    from config import main_repo_url, sub_repos
except ImportError:
    config_error()

home_dir = os.path.expanduser('~')
merger_dir = os.path.join(home_dir, 'repo-merger-tmp')

def main():
    if main_repo_url is None or sub_repos is None:
        config_error()

    old_wd = os.getcwd()
    utils.remove_dir(merger_dir)
    utils.ensure_dir(merger_dir)
    os.chdir(merger_dir)

    main_repo_name = utils.get_repo_name(main_repo_url)
    main_repo_dir = os.path.join(merger_dir, main_repo_name)
    print utils.blue('\nCloning main repo ' + main_repo_name)
    call(['git', 'clone', main_repo_url])
    print ''
    for sub_repo in sub_repos:
        sub_repo_name = utils.get_repo_name(sub_repo['url'])
        sub_repo_dir = os.path.join(merger_dir, sub_repo_name)

        print utils.blue('Merging sub-repo ' + sub_repo_name + ' into main repo ' + main_repo_name)
        call(['git', 'clone', sub_repo['url']])

        utils.remove_file(os.path.join(sub_repo_dir, '.gitignore'))
        utils.remove_file(os.path.join(sub_repo_dir, 'README.md'))

        os.chdir(sub_repo_dir)
        files = os.listdir(sub_repo_dir)
        files.remove('.git')
        destination_dir = os.path.join(sub_repo_dir, sub_repo['dir'])
        utils.ensure_dir(destination_dir)
        for f in files:
            call(['git', 'mv', f, sub_repo['dir']])

        call(['git', 'add', '-A'])
        call(['git', 'commit', '-m', 'Merging '+sub_repo_name+' into '+main_repo_name])

        os.chdir(main_repo_dir)
        remote = 'sub-repo'
        call(['git', 'remote', 'add', remote, sub_repo_dir])
        call(['git', 'fetch', remote])
        call(['git', 'merge', '--allow-unrelated-histories', '--no-edit', remote+'/master'])
        call(['git', 'remote', 'remove', remote])

        os.chdir(merger_dir)
        print ''

    os.chdir(old_wd)
    # utils.remove_dir(merger_dir)

if __name__ == '__main__':
    main()
