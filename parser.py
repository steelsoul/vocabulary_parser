# -*- coding: utf-8 -*-

import re, sqlite3

def checkPart(buffer, newLine):
    temp = buffer + newLine
    if (temp.count('=') > 1): return True
    else: return False 

'''
    Parse string formatted as 'word = description'
    Returns tuple containing two words: word and translation; 
'''
def parsePart(str):    
    template = r"\n?(.*)\s[=]\s(.*)\b"
    patr = None
    m = re.search(template, str)
    if m is not None:
        word = m.group(1).replace('|','')
        word = word.replace('I','')
        word = word.replace(' ', '')
        if len(word) < 2: return ''
        translation = ""
        meanings = re.split(r"\d\.\s*([\w\(\)\s-]*)", m.group(2))
        meanings = [x.replace('(','') for x in meanings]
        meanings = [x.replace(')','') for x in meanings]
        for temp in meanings:
            m1 = re.search(r"\s?(\w+-?)\)?(\w+-?)?(\w+)?", temp, re.ASCII)
            if m1 is not None:
                translation = m1.group(1)
                if m1.group(2) is not None:
                    translation += m1.group(2)
                    if m1.group(3) is not None:
                        translation += m1.group(3)
                break
#        print("%s: %s" % (word, translation))
        part = (word, translation)
    return part

print('START')
fo = open('kre-ru-en-tst.txt', 'r', encoding='utf-8')
conn = connect('temp.db')
#fo = open('kre-ru-en-tst.txt', 'r', encoding='cp1251')
id = 0
buffer = ["",""]
for line in fo:
    if not checkPart(buffer[id], line):
        buffer[id] += line
    else:
        newID = (id + 1) % 2
        buffer[newID] = ""
        buffer[newID] += line
        pair = parsePart(buffer[id])
        print(pair)
        buffer[id] = ""
        id = newID
parsePart(buffer[id])
conn.close()
fo.close()
