#!/usr/bin/python3

import sqlite3
import subprocess

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

logs = open('/home/darrylb/logMonitor/logs.txt', 'w')
subprocess.call(['find','/','-name','*\.log','-not','-path','/home/darrylb/[A-Za-z0-9]*'], stdout=logs)
logs.close()

with open('/home/darrylb/logMonitor/logs.txt', 'r') as f:
    paths = f.read().splitlines()
    for path in paths:
        print(path)
        subprocess.call(['grep','-i','-E','error', '%s' % path])
        print()

'''
createTable()
insertDB()
saveDB()
clearDB()
closeDB()
'''
