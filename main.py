import logging
import sys
import time
import random
import git
import os
import datetime
import shutil


repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'lovestar'))
repo_url = 'https://github.com/jim-ftw/lovestar.git'
repo_ssh = 'git@github.com:jim-ftw/lovestar.git'


insta_url = 'https://www.instagram.com/explore/tags/'

tags = [
    'lovestarbicyclebags',
    'lovestarraceclub',
    'lovestarfactoryteam'
]

logger = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
logging.getLogger("requests").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)


def clear_repo():
    if os.path.isdir(repo_dir):
        for the_file in os.listdir(repo_dir):
            file_path = os.path.join(repo_dir, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(e)
                pass
    if os.path.isdir(repo_dir):
        shutil.rmtree(repo_dir)
        logger.info('removed repo')


def test_file_create():
    test_file = os.path.join(repo_dir, 'test_file')
    if os.path.isfile(test_file):
        os.unlink(test_file)
    else:
        with open(test_file, 'w') as f:
            f.write('test')
    

def get_repo():
    if os.path.isdir(os.path.join(repo_dir, '.git')):
        local_repo = git.Repo(repo_dir)
        logger.info('repo exists')
    else:
        local_repo = git.Repo.clone_from(repo_url, repo_dir)
        logger.info('repo cloned')
    return local_repo
    # local_repo = remote_repo.clone(repo_dir)

def print_config():
    git_config = os.path.join(repo_dir, '.git', 'config')
    with open(git_config, 'r') as f:
        print f.read()

def make_commits(repo):
    print_config()
    email = os.getenv('email_address')
    name = os.getenv('my_name')
    #repo.remotes.origin.config_writer.set('user.email', email)
    #repo.remotes.origin.config_writer.set('user.name', name)
    print_config()
    today = datetime.date.today()
    message = "instagram and strava updates from " + str(today)
    print repo.git.status()
    print repo.git.add(all=True)
    print repo.git.status()
    try:
        print repo.git.commit(m=message)
    except Exception as e:
        print e


def push_repo(repo):
    repo.remotes.origin.set_url(repo_ssh)
    print repo.remotes.origin.url
    ssh_cmd = 'ssh -i $HOME/.ssh/id_rsa'
    with repo.git.custom_environment(GIT_SSH_COMMAND=ssh_cmd):
        repo.remotes.origin.push()


def run_python():
    py_path = os.path.join(repo_dir, 'python')
    sys.path.insert(0, py_path)
    import create_html
    import instagram
    import strava
    strava.reset_strava_json()
    strava.get_json('102393')
    logger.info('strava complete')
    for item in tags:
        tagged_url = insta_url + item
        while tagged_url:
            tagged_url = instagram.get_json(tagged_url, item)
            time.sleep(random.randint(1, 10))
    instagram.get_photo_info()
    instagram.create_thumbnail()
    create_html.reset_dir()
    create_html.iterate_json()

# clear_repo()
local_repo = get_repo()
#run_python()
test_file_create()
make_commits(local_repo)
push_repo(local_repo)
time.sleep(30)
clear_repo()
time.sleep(30)
clear_repo()
