#!/usr/bin/env python
from requests_futures.sessions import FuturesSession
from bs4 import BeautifulSoup
import re
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
    """
    Checks to see if the "next page" button is grayed out.  If so, then we've reached the last page.

    @param html: The html (as a string) of the games list page
    @return: True if we've reached the last page
    """
    return bool(BeautifulSoup(html).findAll('li', class_="next-off"))


def extract_games(html):
    """
    Given some html, extracts the game ids from the links

    @param html: The html (as a string) of the games list page
    @return: A set of all game ids as strings
    """
    soup = BeautifulSoup(html)
    matches  = [URL.id_pattern.search(g.get('href')) for g in soup.findAll('a', class_="games")]
    game_ids = [m.groups()[0] for m in matches if m]
    return set(game_ids)


def start_session():
    """
    Using the credentials in User, attempts to log in to chess.com

    @return: A requests Session object
    """
    with FuturesSession() as s:

        auth_params = {
            'c1': User.name,
            'loginpassword': User.password,
            'Qform__FormControl': 'btnLogin',
            'Qform__FormEvent': 'QClickEvent',
            'Qform__FormParameter': '',
            'Qform__FormCallType': 'Server',
            'Qform__FormUpdates': '',
            'Qform__FormCheckableControls': 'rememberme',
            'Qform__FormId': 'LoginForm'
        }

        # get the base login_url to generate a valid FormState
        r = s.get(URL.login).result()

        # pass the mess to soup and extract that value
        soup = BeautifulSoup(r.text)
        form_state = soup.find(id="Qform__FormState")
        auth_params['Qform__FormState'] = form_state.get('value')

        # finish our login request
        s.post(URL.login, data=auth_params).result()

        return s


def compose_games(s):
    """
    Given a session instance, extracts all game IDs from the chess.com games list pages

    @param s: requests Session instance (must be logged in)
    @return: set of all game ids as strings
    """
    # start parsing the game lists
    page_id = 0
    last_page_id = -1
    ids = set()

    while True:
        page_id += 1

        games = s.get(URL.games.format(page_id)).result()
        ids |= extract_games(games.text)

        stdout.write('\r{0} games found...'.format(len(ids)))
        stdout.flush()

        if is_last_page(games.text):
            print('\n')
            return ids


def fetch_pgn(s, game_id):
    return s.get(URL.pgn.format(game_id), background_callback=write_pgn)


def write_pgn(_, r):
    content_disposition = r.headers['Content-Disposition']
    filename = re.findall(r'filename="([^"]+)"', content_disposition)[0]
    with open(filename, 'wb') as f:
        f.write(bytes(r.text, 'UTF-8'))


def run():
    s   = start_session()
    ids = compose_games(s)
    for i in ids:
        # write out the games!
        fetch_pgn(s, i)


if __name__ == '__main__':
    run()
