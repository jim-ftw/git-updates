import logging
import sys
import time
import random
import git
import os
import datetime
import shutil
import requests
import json
from sparkpost import SparkPost
import create_html
import instagram
import strava

# Repo locations
repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'lovestarraceclub.github.io'))
repo_url = 'https://github.com/lovestarraceclub/lovestarraceclub.github.io.git'
repo_ssh = 'git@github.com:lovestarraceclub/lovestarraceclub.github.io.git'
log_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'log_file.txt'))


# File locations
ig_folder = os.path.join(repo_dir, 'instagram')
media_file_folder = os.path.join(repo_dir, 'lsphotos')
ls_json = os.path.join(repo_dir, 'lsphotos', 'lsphotos.json')
strava_dir = os.path.join(repo_dir, 'strava')
strava_json = os.path.join(strava_dir, 'strava.json')

insta_url = 'https://www.instagram.com/explore/tags/'

tags = [
    'lovestarbicyclebags',
    'lovestarraceclub',
    'lovestarfactoryteam'
]

logger = logging.getLogger()
handler = logging.StreamHandler(open(log_file, 'w'))
formatter = logging.Formatter('%(asctime)-26s %(funcName)-16s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)
logger.setLevel(logging.DEBUG)
logging.getLogger("requests").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)


def clear_directory(directory):
    if os.path.isdir(directory):
        for the_file in os.listdir(directory):
            file_path = os.path.join(directory, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                logger.info(e)
                pass
    logger.info('removed ' + str(directory))


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
        local_repo.git.pull()
        logger.info('pulled newest commit')
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
    config = repo.config_writer()
    config.set_value('user', 'email', email)
    config.set_value('user', 'name', name)
    print_config()
    today = datetime.date.today()
    message = "instagram and strava updates from " + str(today)
    status = repo.git.status()
    logger.info(status)
    status = repo.git.add(all=True)
    logger.info(status)
    status = repo.git.status()
    logger.info(status)
    try:
        status = repo.git.commit(m=message)
        logger.info(status)
        logger.info('commit success!')
    except Exception as e:
        logger.info(e)
        send_logs(log_file)
        sys.exit('Nothing to commit')


def push_repo(repo):
    repo.remotes.origin.set_url(repo_ssh)
    print repo.remotes.origin.url
    ssh_cmd = 'ssh -i $HOME/.ssh/id_rsa'
    with repo.git.custom_environment(GIT_SSH_COMMAND=ssh_cmd):
        repo.remotes.origin.push()
    logger.info('repo pushed')


def send_logs(logs):
    sparky = SparkPost()
    today = datetime.date.today()
    from_email = 'logs@' + os.getenv('SPARKPOST_SANDBOX_DOMAIN')
    with open(logs, 'r') as f:
        log_text = f.read()
    response = sparky.transmission.send(
        recipients=[os.getenv('email_address')],
        text=str(log_text),
        from_email=from_email,
        subject='Lovestar Logs for ' + str(today)
    )
    print response


def run_python():
    strava.reset_strava_json(strava_dir, strava_json)
    strava.get_json('102393', strava_dir, strava_json)
    logger.info('strava complete')
    with open(ls_json, 'r') as f:
        original_ls_json = json.load(f)
    for item in tags:
        tagged_url = insta_url + item
        while tagged_url:
            logging.debug('new_url: ' + tagged_url)
            tagged_url = instagram.get_json(ls_json, tagged_url, item, media_file_folder)
            time.sleep(random.randint(1, 10))
    instagram.get_photo_info(ls_json)
    with open(ls_json, 'r') as f:
        new_ls_json = json.load(f)
    if original_ls_json == new_ls_json:
        logger.info('no new instagram pictures')
        pass
    else:
        create_html.reset_instapages(repo_dir)
        create_html.iterate_json(repo_dir, ls_json)


if __name__ == '__main__':
    open(log_file, 'w')
    res = requests.get("https://nosnch.in/87c0ca5bfc")
    logger.info('snitch status ' + str(res.status_code))
    logger.info('snitch text ' + str(res.text))
    local_repo = get_repo()
    run_python()
    make_commits(local_repo)
    push_repo(local_repo)
    send_logs(log_file)
