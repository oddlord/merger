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
    from config import main_repo_url, sub_repos, files_to_delete
except ImportError:
    config_error()

home_dir = os.path.expanduser('~')
merger_dir = os.path.join(home_dir, 'repo-merger-ws')

def main():
    if main_repo_url is None or sub_repos is None:
        config_error()

    old_wd = os.getcwd()
    print utils.blue('Initialising merging dir '+merger_dir)
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
        print utils.blue('>Cloning sub-repo ' + sub_repo_name)
        call(['git', 'clone', sub_repo['url']])
        os.chdir(sub_repo_dir)

        print utils.blue('>Looking for files to delete')
        if files_to_delete is not None and files_to_delete:
            files = os.listdir(sub_repo_dir)
            for f in files:
                for ftd in files_to_delete:
                    if (ftd.startswith('*') and f.endswith(ftd.split('*')[1])) or (not ftd.startswith('*') and f == ftd):
                        file_path = os.path.join(sub_repo_dir, f)
                        utils.remove_file(file_path)
                        print utils.blue('>>File ' + file_path + ' deleted')

        files = os.listdir(sub_repo_dir)
        files.remove('.git')
        destination_dir = os.path.join(sub_repo_dir, sub_repo['dir'])
        print utils.blue('>Directory ' + destination_dir + ' created')
        utils.ensure_dir(destination_dir)
        for f in files:
            call(['git', 'mv', f, sub_repo['dir']])
            print utils.blue('>>File/dir ' + f + ' moved into ' + sub_repo['dir'])

        call(['git', 'add', '-A'])
        call(['git', 'commit', '-m', 'Merging '+sub_repo_name+' into '+main_repo_name])
        print utils.blue('>Changes committed in sub-repo')

        os.chdir(main_repo_dir)
        print utils.blue('>Adding remote '+sub_repo_name)
        call(['git', 'remote', 'add', sub_repo_name, sub_repo_dir])
        print utils.blue('>Fetching remote '+sub_repo_name)
        call(['git', 'fetch', sub_repo_name])
        print utils.blue('>Merging '+sub_repo_name+' into '+main_repo_name)
        call(['git', 'merge', '--allow-unrelated-histories', '--no-edit', sub_repo_name+'/master'])
        print utils.blue('>Removing remote '+sub_repo_name)
        call(['git', 'remote', 'remove', sub_repo_name])
        print utils.blue('>Sub-repo '+sub_repo_name+' merged into main repo '+main_repo_name)

        os.chdir(merger_dir)
        print ''

    os.chdir(main_repo_dir)
    push = None
    while push is None:
        push = utils.yes_no_input('Do you want to push the merged main repo '+main_repo_name+' to remote', 'y')
    if push:
        call(['git', 'push'])

    remote_delete = None
    while remote_delete is None:
        remote_delete = utils.yes_no_input('Do you want to delete the remote sub-repos', 'n')
    if remote_delete:
        for sub_repo in sub_repos:
            sub_repo_name = utils.get_repo_name(sub_repo['url'])
            print '\tTODO: delete here remote repo '+sub_repo_name+'. Not yet implemented, does nothing for now.'
            # TODO: see https://developer.github.com/v3/repos/#delete-a-repository

    clean = None
    while clean is None:
        clean = utils.yes_no_input('Do you want to delete the merging dir '+merger_dir+' and all its content', 'y')
    if clean:
        utils.remove_dir(merger_dir)

    os.chdir(old_wd)

if __name__ == '__main__':
    main()
