#!/usr/bin/python3

import sqlite3
import subprocess
import os

def connectDB():
    return sqlite3.connect('logs.db')

conn = connectDB()
c = conn.cursor()

def saveDB():
    conn.commit()

def clearDB():
    c.execute('DELETE FROM logs')
    saveDB()

def closeDB():
    c.close()
    conn.close()

def createTable():
    global c
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS logs(unix REAL, datestamp TEXT, process TEXT, file TEXT, error TEXT)')

def insertDB():
    global c
    c = conn.cursor()
    c.execute("INSERT INTO logs VALUES('12345', '2016-01-01', 'Skype','/var/log/skype','Exit: 2')")

def printDB():
    global c
    c = conn.cursor()
    for row in c.execute('SELECT * FROM logs'):
        print(row)

log_paths = "/home/darrylb/logMonitor/log_paths.txt"
log_contents = "/home/darrylb/logMonitor/log_contents.txt"

if os.path.isfile(log_paths):
    os.remove(log_paths)
if os.path.isfile(log_contents):
    os.remove(log_contents)

#opens file for writing
logs = open('/home/darrylb/logMonitor/log_paths.txt', 'w')

#calls find searching from / looking for files that end in .log, ignoring directories in my home which don't begin with '.'
subprocess.call(['find','/','-name','*\.log','-not','-path','/home/darrylb/[A-Za-z0-9]*'], stdout=logs)
logs.close()

#opens file containing log paths
with open(log_paths, 'r+') as f:
    #reads path ignoring any newline characters
    paths = f.read().splitlines()
    with open(log_contents,'w+') as g:
    #for every log file
        for path in paths:
            subprocess.call(['printf', path+'\n'], stdout=g)
            #search for terms that indicate problems
            subprocess.call(['grep','-i','-E','error|fail|unable|fatal|broken', '%s' % path], stdout=g)
            subprocess.call(['printf',"'\n\n'"], stdout=g)
        g.close()
    f.close()

'''
createTable()
insertDB()
saveDB()
clearDB()
closeDB()
'''
