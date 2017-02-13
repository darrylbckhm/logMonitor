#!/usr/bin/python3
#Author: Darryl Beckham

import sqlite3
import subprocess
import os
import threading
import socket
import time
from flask import Flask, render_template

log_db_path = "/home/darrylb/darrylbckhm/logMonitor/logs.db"
log_paths = "/home/darrylb/darrylbckhm/logMonitor/log_paths.txt"
log_contents = "/home/darrylb/darrylbckhm/logMonitor/log_contents.txt"

app = Flask(__name__)

def connect_db():
    return sqlite3.connect('/home/darrylb/darrylbckhm/logMonitor/logs.db')

def save_db(conn):
    conn.commit()

def clear_db():
    conn = connect_db()
    c = conn.cursor()
    c.execute('DELETE FROM logs')
    save_db()

def create_table():
    conn = connect_db()
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS logs(file TEXT, error TEXT)')
    c.close()
    conn.close()

def insert_db(path, contents):
    conn = connect_db()
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS files(file TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS entries(entry TEXT)')
    c.execute('INSERT INTO files VALUES(?)', [path])
#    print("Working on: ", path)
    for line in contents:
        c.execute('INSERT INTO entries VALUES(?)', [line])
#        print(line)
    save_db(conn)
    c.close()
    conn.close()

def print_db():
    conn = connect_db()
    c = conn.cursor()
    for row in c.execute('SELECT * FROM files'):
        print(row)
        for row2 in c.execute('SELECT * FROM entries'):
            print(row2)
    c.close()
    conn.close()

def delete_db():
    if os.path.isfile(log_db_path):
        os.remove(log_db_path)

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
    subprocess.call(['find','/', '-type', 'f', '-name','*[^a-zA-Z0-9]log','-not','-path','/home/*/[A-Za-z0-9]*', '-not', '-path', '/run/media/*', '-not','-path','/proc/*','-not','-path','*/bin/*', '-not', '-path', '*/sbin/*'], stdout=logs)
    logs.close()

def find_errors(path):
    with open(log_contents,'a') as f:
        subprocess.call(['printf', path+'\n'], stdout=f)
        subprocess.call(['grep','-i','-E','error|fail|unable|fatal|broken', '%s' % path], stdout=f)
        subprocess.call(['printf','\n'], stdout=f)
    f.close()
    get_log_contents(path)

def get_log_contents(path):
    with open(path) as f:
        contents = f.read().splitlines()
        insert_db(path,contents)
    f.close()

def create_path_threads():
    #opens file containing log paths
    with open(log_paths, 'r+') as f:
        #reads path ignoring any newline characters
        paths = f.read().splitlines()
        #for every log file
        threads = []
        for path in paths:
            if os.path.isfile(path):
                #need to add a mutex for the database to stop database is locked error
                t = threading.Thread(target=find_errors, args=[path])
                threads.append(t)
        for x in threads:
            x.start()
#            print("Started one")
        thread_i = len(threads)-1
        for i in range(thread_i):
            if(i <= thread_i-1):
                threads[i+1].join()
    f.close()

'''
delete_db()
create_table()
log_clean()
c.close()
conn.close()
'''
def create_html():
    conn = connect_db()
    if os.path.isfile("templates/logs.html"):
        os.remove("templates/logs.html")
    logs_html = open("templates/logs.html", "w")
    logs_html.write("<body>\n<h1>Log Contents</h1>\n")
    logs_html.write("<div>\n")
#    conn = connect_db()
    c = conn.cursor()
    with open(log_contents) as f:
        contents = f.read().splitlines()
        for line in contents:
            #adds another possible memory read which sucks
            if os.path.isfile(line):
                logs_html.write("<h4>") 
                logs_html.write(line)
                logs_html.write("</h4>\n")
            else:
                logs_html.write("<p>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp")
                logs_html.write(line)
                logs_html.write("\n</p>")
    logs_html.write("</div></body>")
    logs_html.close()
    c.close()
    conn.close()

def get_logs():
    #log_clean()
    #get_paths()
    create_path_threads()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/logs', methods=['GET'])
def logs():
    t = threading.Thread(target=get_logs)
    t.start()
    while t.isAlive():
        pass
    create_html()
    #should be able to update paths and contents without reloading everything
    return render_template("logs.html")

if __name__ == "__main__":
    app.run()
