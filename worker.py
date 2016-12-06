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
import new_background
import argparse
import test_site

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
bg_folder = os.path.join(repo_dir, 'img', 'bg')

# change these to pull different tags for isntagram
insta_url = 'https://www.instagram.com/explore/tags/'

tags = [
    'lovestarbicyclebags',
    'lovestarfactoryteam',
    'lovestarraceclub'
]

# test items
page_urls = []
test_urls = []
start_url = 'http://lovestarrace.club/'
bad_urls = []


# python arguments parsing
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--force', help="force html recreation", action="store_true", default=False)
parser.add_argument('--debug', help="debug logging level", action="store_true", default=False)
parser.add_argument('--bg', type=int, help="add new background image based on image number", nargs='+')
parser.add_argument('--rmbg', type=int, help="remove background images based on image number", nargs='+')
parser.add_argument('--rmig', type=int, help="remove instagram photos based on image number", nargs='+')
parser.add_argument('--test', help="run img tests", action="store_true", default=False)
args = parser.parse_args()


# logging
logger = logging.getLogger()
handler = logging.StreamHandler(open(log_file, 'w'))
formatter = logging.Formatter('%(asctime)-26s %(funcName)-20s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)
if args.debug:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
logging.getLogger("requests").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)


# nuclear option: this will completely remove an entire directory
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


# if you need to test your git pushes, this will check for test_file,
# and either create it or delete it so you have something to commit
def test_file_create():
    test_file = os.path.join(repo_dir, 'test_file')
    if os.path.isfile(test_file):
        os.unlink(test_file)
    else:
        with open(test_file, 'w') as f:
            f.write('test')


# pull the repo specified above
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


# prints the repository config file
def print_config():
    git_config = os.path.join(repo_dir, '.git', 'config')
    with open(git_config, 'r') as f:
        print f.read()


def run_tests():
    page_urls.append(start_url)
    s = test_site.get_bs(start_url)
    u = test_site.get_page_urls(s)
    global test_urls
    test_urls += test_site.get_test_urls(s)
    while u:
        u = start_url + u
        page_urls.append(u)
        s = test_site.get_bs(u)
        u = test_site.get_page_urls(s)
        test_urls += test_site.get_test_urls(s)
    for i in test_urls:
        t = test_site.check_url_status(i)
        if t:
            bad_urls.append(t)
    if not bad_urls:
        logger.info('no bad urls')
    else:
        for i in bad_urls:
            logger.warn('bad url: ' + i)


# make any commits that have been staged
def make_commits(repo, commit_message):
    email = os.getenv('email_address')
    name = os.getenv('my_name')
    config = repo.config_writer()
    config.set_value('user', 'email', email)
    config.set_value('user', 'name', name)
    message = commit_message
    status = repo.git.status()
    logger.debug(status)
    status = repo.git.add(all=True)
    logger.info(status)
    status = repo.git.status()
    logger.debug(status)
    try:
        status = repo.git.commit(m=message)
        logger.info(status)
        logger.info('commit success!')
    except Exception as e:
        logger.info(e)
        send_logs(log_file)
        sys.exit('Nothing to commit')


# pushes the repository (using SSH)
def push_repo(repo):
    repo.remotes.origin.set_url(repo_ssh)
    ssh_cmd = 'ssh -i $HOME/.ssh/id_rsa'
    with repo.git.custom_environment(GIT_SSH_COMMAND=ssh_cmd):
        repo.remotes.origin.push()
    logger.info('repo pushed')


def git_stash():
    local_repo = get_repo()
    local_repo.git.stash()


# send logs via SparkPost
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


# Runs the python from Strava, Instagram, and Create HTML
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
    if args.force:
        local_repo = get_repo()
        create_html.reset_instapages(repo_dir)
        create_html.iterate_json(repo_dir, ls_json)
        today = datetime.date.today()
        cm = "reseting html"
        make_commits(local_repo, cm)
        push_repo(local_repo)
        time.sleep(30)
        run_tests()
        send_logs(log_file)
    elif args.bg:
        img_num = args.bg
        local_repo = get_repo()
        old_bg_contents = os.listdir(bg_folder)
        for i in img_num:
            new_background.add_background_img(bg_folder, i, ls_json)
        new_bg_contents = os.listdir(bg_folder)
        if sorted(old_bg_contents) == sorted(new_bg_contents):
            logger.info('no new backgrounds')
            pass
        else:
            create_html.reset_instapages(repo_dir)
            create_html.iterate_json(repo_dir, ls_json)
            cm = "new background image"
            make_commits(local_repo, cm)
            push_repo(local_repo)
            time.sleep(30)
            run_tests
            send_logs(log_file)
    elif args.rmbg:
        img_num = args.rmbg
        local_repo = get_repo()
        old_bg_contents = os.listdir(bg_folder)
        for i in img_num:
            new_background.remove_background_img(bg_folder, i)
        new_bg_contents = os.listdir(bg_folder)
        if sorted(old_bg_contents) == sorted(new_bg_contents):
            logger.info('no backgrounds to remove')
            pass
        else:
            create_html.reset_instapages(repo_dir)
            create_html.iterate_json(repo_dir, ls_json)
            cm = "removing background images"
            make_commits(local_repo, cm)
            push_repo(local_repo)
            time.sleep(30)
            run_tests()
            send_logs(log_file)
    elif args.rmig:
        img_num = args.rmig
        local_repo = get_repo()
        with open(ls_json, 'r') as f:
            old_ig_contents = json.loads(f.read())
        for i in img_num:
            instagram.remove_ig_photo(ls_json, i)
        with open(ls_json, 'r') as f:
            new_ig_contents = json.loads(f.read())
        if old_ig_contents == new_ig_contents:
            logger.info('no instagram photos removed')
            pass
        else:
            create_html.reset_instapages(repo_dir)
            create_html.iterate_json(repo_dir, ls_json)
            cm = "removing instagram images " + str(img_num)
            make_commits(local_repo, cm)
            push_repo(local_repo)
            time.sleep(30)
            run_tests()
            send_logs(log_file)
    elif args.test:
        open(log_file, 'w')
        run_tests()
        send_logs(log_file)
    else:
        open(log_file, 'w')
        res = requests.get("https://nosnch.in/87c0ca5bfc")
        logger.info('snitch status ' + str(res.status_code))
        logger.info('snitch text ' + str(res.text))
        local_repo = get_repo()
        run_python()
        today = datetime.date.today()
        cm = "instagram and strava updates from " + str(today)
        make_commits(local_repo, cm)
        push_repo(local_repo)
        time.sleep(30)
        run_tests()
        send_logs(log_file)
