import sqlite3 as lite
from flask import session, request

DATABASE = "/var/www/FlaskApp/FlaskApp/database_example/database_example.db"
#input_data = "bananas"
#output_data = "cookies"

def create_table(input_data,output_data):
    con = lite.connect(DATABASE)
    c = con.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS input_log(id INTEGER PRIMARY KEY AUTOINCREMENT, input TEXT, output TEXT)")
    c.execute("INSERT INTO input_log (input,output) VALUES (?,?)",(input_data, output_data,))
    con.commit()
    c.close()
    return

#create_table()

def database_contents():
    con = lite.connect(DATABASE)
    c = con.cursor()
    c.execute("SELECT * FROM input_log")
    rows = c.fetchall() #there is also fetchone()
    for row in rows:
        print(row)
    con.close()
    return

database_contents()
    