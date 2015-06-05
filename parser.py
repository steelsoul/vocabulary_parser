# -*- coding: utf-8 -*-

import re, sqlite3

def checkPart(buffer, newLine):
    temp = buffer + newLine
    if (temp.count('=') - temp.count('(=') > 1): return True
    else: return False 

'''
    Parse string formatted as 'word = description'
    Returns tuple containing two words: word and translation; 
'''
def parsePart(data):    
    template = r"\n?(.*)\s[=]\s(.*)\b"
    part = None
    m = re.search(template, data)
    if m is not None:
        word = m.group(1).replace('|','')
        word = word.replace('I','')
        word = word.replace(' ', '')
        if len(word) < 2: return None
        pos = word.find(',')
        if pos != -1:
            word = word[0:pos]
        translation = ""
        meanings = re.split(r"\d\.\s*([\w\(\)\s-]*)", m.group(2))
        meanings = [x.replace('(','') for x in meanings]
        meanings = [x.replace(')','') for x in meanings]
        meanings = [x.replace('pl','') for x in meanings]
        meanings = [x.replace('.','') for x in meanings]
        meanings = [x.replace('smth','') for x in meanings]
        meanings = [x.replace('smb','') for x in meanings]
        
        for temp in meanings:
            m1 = re.search(r"\s?(\w+-?\s?\s?\s?\/?)\)?(\w+-?\s?)?(\w+\s?)?(\w+)?", temp, re.ASCII)
            if m1 is not None:
                translation = m1.group(1)
                if m1.group(2) is not None:
                    translation += m1.group(2)
                    if m1.group(3) is not None:
                        translation += m1.group(3)
                        if m1.group(4) is not None:
                            translation += m1.group(4)
                break
        #print("%s: %s" % (word, translation))
        word = word.replace(',','')
        translation = translation.replace('III','')
        transltaion = translation.replace('II','')
        transltaion = translation.replace('c ','')
        part = (word, translation)
        if word.count(' ') == len(word) or translation.count(' ') == len(translation):
            part = None
        if word.count('I') == len(word) or translation.count('I') == len(translation):
            part = None
        if len(word) <= 2 or len(translation) <= 2:
            part = None
        try:
            int(word)
            return None
        except ValueError:
            None

        try:
            int(translation)
            return None
        except ValueError:
            None
            
    else:
        print("NONE: " + data)
    return part

print('START')
id = 0
buffer = ["",""]
with open('kre-ru-en.txt', 'r', encoding='cp1251') as fo:
#with open('kre-ru-en-tst.txt', 'r', encoding='utf-8') as fo:
    with open('re.txt', 'w', encoding='utf-8') as fw:
        for line in fo:
            if not checkPart(buffer[id], line):
                buffer[id] += line
            else:
                newID = (id + 1) % 2
                buffer[newID] = ""
                buffer[newID] += line                
                result = parsePart(buffer[id])                
                if result is not None and len(result) > 1:
                    (w, t) = result
                    fw.write(w + ' : ' + t + '\n')
                buffer[id] = ""
                id = newID
        result = parsePart(buffer[id])
        if result is not None and len(result) > 1:
            (w, t) = result
            fw.write(w + ' : ' + t + '\n')
fw.close()
fo.close()
print('END')
