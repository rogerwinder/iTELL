#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from flask import Flask, current_app, g
from collections import defaultdict as dd
from os import path

def qs(ll):
    """return len(l) ?s sepeated by ','  to use in queries"""
    return ','.join('?' for l  in ll)

app = Flask(__name__)
with app.app_context():

    ROOT  = path.dirname(path.realpath(__file__))
    ADMINDB = 'db/admin.db'
    CALLIGDB = 'db/callig.db'
    LCCDB = 'db/lcc.db'


    ############################################################################
    # SET UP CONNECTIONS
    ############################################################################
    def connect_admin():
        return sqlite3.connect(path.join(ROOT, ADMINDB))

    def connect_callig():
        return sqlite3.connect(path.join(ROOT, CALLIGDB))
    
    def connect_lcc():
        return sqlite3.connect(path.join(ROOT, LCCDB))

    def query_admin(query, args=(), one=False):
        cur = g.admin.execute(query, args)
        rv = [dict((cur.description[idx][0], value)
                   for idx, value in enumerate(row)) for row in cur.fetchall()]
        return (rv[0] if rv else None) if one else rv

    def query_callig(query, args=(), one=False):
        cur = g.callig.execute(query, args)
        rv = [dict((cur.description[idx][0], value)
                   for idx, value in enumerate(row)) for row in cur.fetchall()]
        return (rv[0] if rv else None) if one else rv

    def query_lcc(query, args=(), one=False):
        cur = g.lcc.execute(query, args)
        rv = [dict((cur.description[idx][0], value)
                   for idx, value in enumerate(row)) for row in cur.fetchall()]
        return (rv[0] if rv else None) if one else rv
    
    def write_admin(query, args=(), one=False):
        cur = g.admin.cursor()
        cur.execute(query, args)
        lastid = cur.lastrowid
        g.admin.commit()
        return lastid

    def write_callig(query, args=(), one=False):
        cur = g.callig.cursor()
        cur.execute(query, args)
        lastid = cur.lastrowid
        g.callig.commit()
        return lastid

    def write_lcc(query, args=(), one=False):
        cur = g.lcc.cursor()
        cur.execute(query, args)
        lastid = cur.lastrowid
        g.lcc.commit()
        return lastid

    ############################################################################
    # ADMIN SQL
    ############################################################################

    def fetch_userid(userID):
        user = None
        for r in query_admin("""SELECT userID, password, 
                                       access_level, access_group, full_name
                                FROM users
                                WHERE userID = ?""", [userID]):
            if r['userID']:
                user = (r['userID'], r['password'], 
                        r['access_level'], r['access_group'], r['full_name'])
        return user


    def fetch_id_from_userid(userID):
        for r in query_admin("""SELECT id 
                                FROM users
                                WHERE userID = ?""", [userID]):
            return r['id']


    def fetch_allusers():
        users = dd()
        for r in query_admin("""SELECT * FROM users"""):
            users[r['id']] = r

        return users


    ############################################################################
    # CALLIG SQL
    ############################################################################


    ############################################################################
    # SEX WITH ME
    ############################################################################
    def write_sexwithme(prompt, answer, seconds, language, username, timestamp):
        """
        Returns the ID of the recently added entry.
        """
        return write_callig("""INSERT INTO sex_with_me (prompt, answer, 
                                                      seconds, language, 
                                                      username, timestamp)
                               VALUES (?,?,?,?,?,?)""",
                            [prompt, answer, seconds,
                             language, username, timestamp])

    def write_sexwithme_feedback(answer, sex_with_me_id, feedback,
                                 seconds, language, username, timestamp):
        """
        Returns the ID of the recently added entry.
        """
        return write_callig("""INSERT INTO sex_with_me_feedback
                                           (answer, sex_with_me_id, feedback,
                                            seconds, language, username, timestamp)
                               VALUES (?,?,?,?,?,?,?)""",
                            [answer, sex_with_me_id, feedback,
                             seconds, language, username, timestamp])

    
    def fetch_sexwithme_30():
        result = dd()
        for r in query_callig("""SELECT * FROM sex_with_me WHERE answer IS NOT NULL
                                 ORDER BY timestamp DESC LIMIT 30"""):
            result[r['id']] = [r['prompt'], r['answer'], r['seconds'], r['language'],
                               r['username'], r['timestamp']]
        return result


    

    ############################################################################
    # WICKED PROVERBS
    ############################################################################
    def write_wickedproverbs(frame, w1, w2, proverb, explanation, seconds,
                             language, username, timestamp):
        """
        Returns the ID of the recently added entry.
        """
        return write_callig("""INSERT INTO wicked_proverbs
                               (frame, w1, w2, proverb, explanation, seconds,
                                language, username, timestamp)
                               VALUES (?,?,?,?,?,?,?,?,?)""",
                            [frame, w1, w2, proverb, explanation, seconds,
                             language, username, timestamp])


    def fetch_wickedproverbs_30():
        result = dd()
        for r in query_callig("""SELECT * FROM wicked_proverbs
                                 WHERE proverb IS NOT NULL
                                 AND explanation IS NOT NULL
                                 ORDER BY timestamp DESC LIMIT 30"""):
            result[r['id']] = [r['frame'], r['proverb'],r['explanation'],
                               r['seconds'], r['language'],
                               r['username'], r['timestamp']]
        return result


    
    
    ############################################################################
    # HAIKU ON DEMAND
    ############################################################################
    def write_haikuondemand(title, l1, l2, l3,
                            seconds, language, username, timestamp):
        """
        Returns the ID of the recently added entry.
        """
        return write_callig("""
                            INSERT INTO haiku_on_demand 
                            (title, l1, l2, l3,
                             seconds, language, username, timestamp)
                            VALUES (?,?,?,?,?,?,?,?)
                            """, [title, l1, l2, l3,
                                  seconds, language, username, timestamp])

    def write_haikuondemand_feedback(title, feedback, l1, l2, l3, s1, s2, s3,
                                     seconds, language, username, timestamp):
        """
        Returns the ID of the recently added entry.
        """
        return write_callig("""
                            INSERT INTO haiku_on_demand_feedback
                            (title, feedback, l1, l2, l3, s1, s2, s3,
                             seconds, language, username, timestamp)
                            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                            """, [title, feedback, l1, l2, l3, s1, s2, s3,
                                  seconds, language, username, timestamp])

    
    def fetch_haikuondemand_30():
        result = dd()
        for r in query_callig("""
                              SELECT * FROM haiku_on_demand
                              WHERE l1 IS NOT NULL
                              AND l2 IS NOT NULL
                              AND l3 IS NOT NULL
                              ORDER BY timestamp DESC LIMIT 30
                              """):
            result[r['id']] = [r['title'], r['l1'], r['l2'], r['l3'],
                               r['username'], r['timestamp'], r['seconds']]
        return result
    


    ############################################################################
    # LCC SQL
    ############################################################################

    def fetch_max_doc_id():
        for r in query_lcc("""SELECT MAX(docid) from doc"""):
            if r['MAX(docid)']:
                return r['MAX(docid)']
            else:
                return 0

    def fetch_max_sid():
        for r in query_lcc("""SELECT MAX(sid) from sent"""):
            if r['MAX(sid)']:
                return r['MAX(sid)']
            else:
                return 0

    def fetch_sents_by_docid(docid):
        sents = dd()
        for r in query_lcc("""SELECT sid, sent from sent
                              WHERE docid = ?
                           """, [docid]):
            sents[r['sid']] = r['sent']
        return sents

    def fetch_words_by_sid(sid_min, sid_max):
        words = dd(lambda: dd())
        for r in query_lcc("""SELECT sid, wid, word, pos, lemma from word
                              WHERE sid >= ? AND sid <= ?
                           """, [sid_min, sid_max]):
                words[r['sid']][r['wid']]=[r['word'], r['pos'],r['lemma']]
        return words

    def fetch_max_wid(sid):
        for r in query_lcc("""SELECT MAX(wid) from word WHERE sid = ?""", [sid]):

            if r['MAX(wid)']:
                return r['MAX(wid)']
            else:
                return 0

    def insert_into_doc(docid, docname):
        return write_lcc("""INSERT INTO doc (docid, title)
                               VALUES (?,?)
                            """, [docid, docname])

    def update_html_into_doc(docid, html):
        return write_lcc("""UPDATE doc SET doc = ? 
                               WHERE docid = ?
                            """, [html, docid])

    def insert_into_sent(sid, docid, pid, sent):
        return write_lcc("""INSERT INTO sent (sid, docID, pid, sent)
                               VALUES (?,?,?,?)
                            """, [sid, docid, pid, sent])

    def insert_into_word(sid, wid, word, pos, lemma):
        return write_lcc("""INSERT INTO word (sid, wid, word, pos, lemma)
                               VALUES (?,?,?,?,?)
                            """, [sid, wid, word, pos, lemma])

    def insert_into_error(sid, eid, label, comment):
        return write_lcc("""INSERT INTO error (sid, eid, label, comment)
                               VALUES (?,?,?,?)
                            """, [sid, eid, label, comment])

