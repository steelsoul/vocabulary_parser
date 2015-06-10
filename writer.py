# -*- coding: utf-8 -*-

import sqlite3

def parseLine(line):
    pos = line.find(' : ')
    if pos < 0: return None
    apart = line[:pos]
    bpart = line[pos+3:-1]
    #print('pos = %d, a = %s, b = %s' % (pos, apart, bpart))
    return (apart, bpart)

def parseFile(fileName, dbName):
    langTable = '''CREATE TABLE LANGUAGES
    (_id INTEGER PRIMARY KEY AUTOINCREMENT,
    LANGUAGE TEXT);'''
    presTable = '''CREATE TABLE PRESENTATION
    (pid INTEGER PRIMARY KEY AUTOINCREMENT,
    WORD_ID INT,
    TRANSLATION_ID INT);'''
    wordTable = '''CREATE TABLE WORDSTABLE
    (wid INTEGER PRIMARY KEY AUTOINCREMENT,
    LANG_ID INT,
    TYPE_ID INT,
    WORD_DATA TEXT);'''

    conn = sqlite3.connect(dbName)
    conn.execute(langTable)
    conn.execute(presTable)
    conn.execute(wordTable)

    conn.execute("INSERT INTO LANGUAGES (LANGUAGE) VALUES ('en')")
    conn.execute("INSERT INTO LANGUAGES (LANGUAGE) VALUES ('ru')")
    conn.execute("INSERT INTO LANGUAGES (LANGUAGE) VALUES ('de')")
    
    with open(fileName, 'r', encoding='utf-8') as fr:
        for line in fr:
            result = parseLine(line)
            if result is not None:
                (word, translation) = result
                first = "INSERT INTO WORDSTABLE (LANG_ID, TYPE_ID, WORD_DATA) \
    VALUES (2, 0, '%s')" % (word)
                second = "INSERT INTO WORDSTABLE (LANG_ID, TYPE_ID, WORD_DATA) \
    VALUES (1, 0, '%s')" % (translation)
                #print(first)
                #print(second)
                conn.execute(first)
                conn.execute(second)
    conn.commit()
    conn.close()

dbFileName = 'temp'
importFileName = 'test.txt'
parseFile(importFileName, dbFileName)


                
