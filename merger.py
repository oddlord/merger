import git
import os
from subprocess import call
import sys

def config_error():
    cfg_err_str = 'config.py not configured.\nAborting.'
    print cfg_err_str
    sys.exit(1)

try:
    from config import main_repo, sub_repos
except ImportError:
    config_error()

home_dir = os.path.expanduser('~') + '/'
base_dir = home_dir + 'test/'

def ensure_dir(dir_path):
    directory = os.path.dirname(dir_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def main():
    if main_repo is None or sub_repos is None:
        config_error()

    ensure_dir(base_dir)

if __name__ == '__main__':
    main()
