# -*- coding: utf-8 -*-

import sqlite3

def parseLine(line):
    pos = line.find(' : ')
    if pos < 0: return None
    apart = line[:pos]
    bpart = line[pos+3:-1]
    #print('pos = %d, a = %s, b = %s' % (pos, apart, bpart))
    return (apart, bpart)

def makeDB(filename, conn):
    with open(filename, 'r') as fr:
        sentence = ''
        for line in fr:
            if ';' not in line: 
                sentence += line[:-1]
                sentence += ' '
            else:
                sentence += line[:-1]
                print("Executing: %s" % sentence)
                conn.execute(sentence)
                sentence = ''

def parseFile(fileName, dbName):
    conn = sqlite3.connect(dbName)
    makeDB('createBD.sql', conn)
   
    with open(fileName, 'r', encoding='utf-8') as fr:
        for line in fr:
            result = parseLine(line)
            if result is not None:
                (word, translation) = result
                first = "INSERT INTO WORDSTABLE (ID_LANG, ID_TYPE, WORD_DATA) \
    VALUES (2, 0, '%s')" % (word)
                second = "INSERT INTO WORDSTABLE (ID_LANG, ID_TYPE, WORD_DATA) \
    VALUES (1, 0, '%s')" % (translation)
                #print(first)
                #print(second)
                conn.execute(first)
                conn.execute(second)
    conn.commit()
    conn.close()

dbFileName = 'temp.db'
importFileName = 'res.txt'
parseFile(importFileName, dbFileName)
