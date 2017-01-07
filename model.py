__author__ = 'user'
import sqlite3
from flask import g

DATABASE = 'ZeeSlip.sqlite'
class DBConn:
    def __int__(self):
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect(DATABASE)
        return db
