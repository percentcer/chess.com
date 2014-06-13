#!/usr/bin/env python
import requests
from bs4 import BeautifulSoup
import re
from multiprocessing import Process
from sys import stdout


class User(object):
    name     = 'your_username'
    password = 'your_password'


class URL(object):
    login = 'https://www.chess.com/login'
    games = 'https://www.chess.com/home/my_archive?show=live&page={0}'
    pgn   = 'https://www.chess.com/echess/download_pgn?lid={0}'
    id_pattern = re.compile(r'/livechess/game\?id=(\d+)')


def is_last_page(html):
    return bool(BeautifulSoup(html).findAll('li', class_="next-off"))


def extract_games(html):
    soup = BeautifulSoup(html)
    matches  = [URL.id_pattern.search(g.get('href')) for g in soup.findAll('a', class_="games")]
    game_ids = [m.groups()[0] for m in matches if m]
    return set(game_ids)


def start_session():
    with requests.Session() as s:

        auth_params = {
            'c1' : User.name,
            'loginpassword' : User.password,
            'Qform__FormControl':'btnLogin',
            'Qform__FormEvent':'QClickEvent',
            'Qform__FormParameter':'',
            'Qform__FormCallType':'Server',
            'Qform__FormUpdates':'',
            'Qform__FormCheckableControls':'rememberme',
            'Qform__FormId':'LoginForm'
        }

        # get the base login_url to generate a valid FormState
        r = s.get(URL.login)

        # pass the mess to soup and extract that value
        soup = BeautifulSoup(r.text)
        form_state = soup.find(id="Qform__FormState")
        auth_params['Qform__FormState'] = form_state.get('value')

        # finish our login request
        s.post(URL.login, data=auth_params)

        return s


def compose_games(s):
    # start parsing the game lists
    page_id = 0
    last_page_id = -1
    ids = set()

    while True:
        page_id += 1

        games = s.get(URL.games.format(page_id))
        ids |= extract_games(games.text)

        stdout.write('\r{0} games found...'.format(len(ids)))
        stdout.flush()

        if is_last_page(games.text):
            return ids

def run():
    s   = start_session()
    ids = compose_games(s)


if __name__ == '__main__':
    run()
