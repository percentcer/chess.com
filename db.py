__author__ = 'Spencer'

import pgn
import csv
import sqlite3
import os

def pgns2csv(dir):
    pgn_lists = [pgn.loads(open(os.path.join(dir, p)).read()) for p in os.listdir(dir) if p.endswith('.pgn')]
    games     = [game for sublist in pgn_lists for game in sublist]
    with open('games.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "event", "site", "date", "round", "white", "black", "result",
            "whiteelo", "blackelo", "annotator", "plycount", "timecontrol", "time", "termination", "mode", "fen"
        ])
        for g in games:
            writer.writerow([
                g.event,
                g.site,
                g.date,
                g.round,
                g.white,
                g.black,
                g.result,
                g.whiteelo,
                g.blackelo,
                g.annotator,
                g.plycount,
                g.timecontrol,
                g.time,
                g.termination,
                g.mode,
                g.fen
                ])

def pgns2sqlite(dir):
    pass