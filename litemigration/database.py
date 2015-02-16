#!/usr/bin/python3

import sqlite3
import datetime as dt

class Database(object):
    "Create migration control"
    def __init__(self, db):
        self.connect = sqlite3.connect(db)
        self.db = self.connect.cursor()

    def initialise(self):
        "Create new database on new start"
        try:
            self.connect.execute("CREATE TABLE migration("\
                             'id INTEGER PRIMARY KEY NOT NULL,'\
                             'version INTEGER UNIQUE NOT NULL,'\
                             'date TIMESTAMP NOT NULL)')
            self.db.execute("INSERT INTO migration(version,date) VALUES(0,?)", (dt.datetime.now(),))
            self.connect.commit()
            self.connect.close()
        except sqlite3.OperationalError as e:
            print(e)
            exit()

    def add_schema(self, change_list):
        "Add new schema changes"
        for (change_id, sql_statement) in change_list:
            self.db.execute('SELECT max(version) from migration')
            (max_id,) = self.db.fetchone()
            self.db.execute("SELECT id from migration where version=?", (change_id,))
            if max_id > change_id:
                print("schema change {} is smaller the lastest schema change {}".format(change_id,max_id))
            elif self.db.fetchone():
                print("change id has already been applied")
            else:
                try:
                    self.connect.execute(sql_statement)
                    self.connect.execute("INSERT INTO migration(version,date) VALUES(?,?)",
                                         (change_id, dt.datetime.now(),))
                    self.connect.commit()
                    print("complete")
                except sqlite3.IntegrityError:
                    print("Schema change for {} has already been applied")
                except sqlite3.OperationalError as e:
                    print("Unable to add schema {}".format(change_id))
                    print(e)
                    exit()
