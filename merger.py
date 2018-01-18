import sys

def config_error():
    cfg_err_str = 'config.py not configured.\nAborting.'
    print cfg_err_str
    sys.exit(1)

try:
    from config import main_repo, sub_repos
except ImportError:
    config_error()

def main():

    if main_repo is None or sub_repos is None:
        config_error()
    print 'lol'

if __name__ == '__main__':
    main()
