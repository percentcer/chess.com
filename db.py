__author__ = 'Spencer'

import pgn
import csv
import sqlite3
import os


class PGNWriter(object):
    HEADERS = [
            "event", "site", "date", "round", "white", "black", "result",
            "whiteelo", "blackelo", "annotator", "plycount", "timecontrol", "time", "termination", "mode", "fen"
    ]

    @staticmethod
    def _pgn2row(g):
        return [getattr(g, tag, None) for tag in PGNWriter.HEADERS]

    def __init__(self, *args, **kwargs):
        self.writer = csv.writer(*args, **kwargs)
        self.writer.writerow(PGNWriter.HEADERS)

    def writegame(self, game):
        self.writer.writerow(PGNWriter._pgn2row(game))


def pgns2csv(dir, name='games.csv'):
    """
    Reads all pgns in a given directory and compiles them into a csv
    @param dir: directory that houses the pgns
    """
    pgn_lists = [pgn.loads(open(os.path.join(dir, p)).read()) for p in os.listdir(dir) if p.endswith('.pgn')]
    games     = [game for sublist in pgn_lists for game in sublist]
    with open(name, 'w', newline='') as csvfile:
        writer = PGNWriter(csvfile)
        for game in games:
            writer.writegame(game)

def pgns2sqlite(dir):
    pass