#!/usr/bin/python3
#Author: Darryl Beckham

import sqlite3
import subprocess
import os

log_db_path = "/home/darrylb/darrylbckhm/logMonitor/log.db"

def connect_db():
    return sqlite3.connect('logs.db')

conn = connect_db()
c = conn.cursor()

def save_db():
    conn.commit()

def clear_db():
    c.execute('DELETE FROM logs')
    save_db()

def close_db():
    c.close()
    conn.close()

def create_table():
    global c
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS logs(file TEXT, error TEXT)')

def insert_db(log_map):
    global c
    c = conn.cursor()
    #considering the trade offs between storing errors as single entries in db, as an array, and/or incrementing a variable to keep track of dups
    for key in log_map:
        for value in log_map[key]:
            c.execute("INSERT INTO logs VALUES (?, ?)", (key, value))
    save_db()

def print_db():
    global c
    c = conn.cursor()
    for row in c.execute('SELECT * FROM logs'):
        print(row)

def delete_db():
    if os.path.isfile(log_db_path):
        os.remove(log_db_path)

log_paths = "/home/darrylb/darrylbckhm/logMonitor/log_paths.txt"
log_contents = "/home/darrylb/darrylbckhm/logMonitor/log_contents.txt"
create_table()

def log_clean():
    if os.path.isfile(log_paths):
        os.remove(log_paths)
    if os.path.isfile(log_contents):
        os.remove(log_contents)

def get_paths():
    #opens file for writing
    logs = open('/home/darrylb/darrylbckhm/logMonitor/log_paths.txt', 'w')

    #calls find searching from / looking for files that end in .log, ignoring directories in my home which don't begin with '.'
    #changed to account for auto mounted filesystems in /run/media, as well as a wildcard added to match ALL home directories
    subprocess.call(['find','/','-name','*\.log','-not','-path','/home/*/[A-Za-z0-9]*', '-not', '-path', '/run/media/*'], stdout=logs)
    logs.close()

def get_log_contents():
    log_map={}
    #opens file containing log paths
    with open(log_paths, 'r+') as f:
        #reads path ignoring any newline characters
        paths = f.read().splitlines()
        with open(log_contents,'w+') as g:
            #for every log file
            for path in paths:
                #FIX ME: quotation marks print with output - maybe not. They actually serve as a good indicator of beginning and end of record
                subprocess.call(['printf', path+'\n'], stdout=g)
                #search for terms that indicate problems
                subprocess.call(['grep','-i','-E','error|fail|unable|fatal|broken', '%s' % path], stdout=g)
                subprocess.call(['printf','\n'], stdout=g)
                #FIX ME: The idea is to use a dictionary with the path as the key and the contents of the log file in a list of entries corresponding to the number of lines in the log file
                log_map[path]=open(path,'r').readlines()
                log_map[path]=[line.strip() for line in log_map[path]]
                insert_db(log_map)
                #print(log_map[path])
                #print()
            g.close()
        f.close()

log_clean()
get_paths()
get_log_contents()
print_db()
delete_db()

'''
createTable()
insertDB()
saveDB()
clearDB()
closeDB()
'''
