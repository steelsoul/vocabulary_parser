# -*- coding: utf-8 -*-

import sqlite3, sys, getopt

def connect(sqlite3database):
    conn = sqlite3.connect(sqlite3database)
    c = conn.cursor()
    return conn, c

def parseLine(line):
    pos = line.find(' : ')
    if pos < 0: return None
    apart = line[:pos]
    bpart = line[pos+3:-1]
    #print('pos = %d, a = %s, b = %s' % (pos, apart, bpart))
    return (apart, bpart)

def makeDB(filename, conn):
    # TODO : use cur = conn.cursor() cur.executescript()
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
    def findPosition(c, tableName, columnName, value):
        request = "SELECT ID FROM %s WHERE %s = '%s'" % (tableName, columnName, value)
        c.execute(request)
        idd = c.fetchone()
        if idd == None: 
            return None
        else:
#            print("idd (%s): %d" % (value, idd[0]))
            return idd[0]
            
    conn, c = connect(dbName)
    makeDB('createBD.sql', conn)
   
    with open(fileName, 'r', encoding='utf-8') as fr:
        count = 0
        for line in fr:
            count = count + 1
            if count == 100: 
                sys.stdout.write('.')
                sys.stdout.flush()
                count = 0
            result = parseLine(line)
            if result is not None:
                (word, translation) = result
                (res1, res2) = (True, True)
                first = "INSERT INTO WORDSTABLE (ID_LANG, ID_TYPE, WORD_DATA) \
    VALUES (2, 0, '%s')" % (word)
                second = "INSERT INTO WORDSTABLE (ID_LANG, ID_TYPE, WORD_DATA) \
    VALUES (1, 0, '%s')" % (translation)
#                print(first)
#                print(second)                
                
                (id_direct, id_word, id_transl) = (1, -1, -1)
                try:
                    c.execute(first)
                    id_word = c.lastrowid
                except sqlite3.IntegrityError as e:
                    res1 = False
#                    print("Error in first insertment: %s" % (e.args[0]))
                
                try:
                    c.execute(second)
                    id_transl = c.lastrowid
                except sqlite3.IntegrityError as e:
                    res2 = False
#                    print("Error in second insertment: %s" % (e.args[0]))
                
    
                if (res1, res2) == (False, False):
#                    print("Skipping entirely record (%s : %s)" % (word, translation))
                    continue
                elif res1 == False:
                    pos = findPosition(c, "WORDSTABLE", "WORD_DATA", word)
                    if pos is None:
                        print("Unrecoverable error (1)!")
                        sys.exit(2)
                    #print("word %s is known at %d" % (word, pos))
                    id_word = pos
                elif res2 == False:
                    pos = findPosition(c, "WORDSTABLE", "WORD_DATA", translation)
                    if pos is None:
                        print("Unrecoverable error(2)!")
                        sys.exit(2)
                    #print("word %s is known at %d" % (translation, pos))
                    id_transl = pos
                presQuery = "INSERT INTO PRESENTATION (ID_DIRECT, ID_WORD, ID_TRANSL) \
 VALUES (%d, %d, %d)" % (id_direct, id_word, id_transl)
#                print(presQuery)  
                c.execute(presQuery)
    print('')                
    conn.commit()
    conn.close()

def printhelp():
    print("Usage: writter.py -i <input> -o <db name>");

if __name__ == "__main__":
    dbFileName = 'temp.db'
    importFileName = 'res.txt'
    
    if len(sys.argv) < 3:
        printhelp()
        sys.exit(2)
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        printhelp()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            printhelp()
        elif opt in ("-i", "--ifile"):
            importFileName = arg
        elif opt in ("-o", "--ofile"):
            dbFileName = arg

    print("Parsing %s to %s" % (importFileName, dbFileName))
    parseFile(importFileName, dbFileName)
    print("Complete.")
