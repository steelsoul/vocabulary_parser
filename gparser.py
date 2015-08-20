# -*- coding: utf-8 -*-

#
#   Use python 3 for running this !! 
#

import functools
import re

DEBUG = False

def grammar(description, whitespace = r'\s*'):
    """
    Convert a description to a grammar. Each line is a rule for a
    non-terminal symbol; it looks like this:

        Symbol => A1 A2 ... | B1 B2 ... | C1 C2 ...

    where the right-hand side is one or more alternatives, separated by
    the '|' sign. Each alternative is a sequence of atoms, separated by
    spaces.  An atom is either a symbol on syme left-hand side, or it is a
    regular expression that will be passed to re.match to match a token.

    Notation for *, +, or ? not allowed in a rule alternative (but ok within a
    token). Use '\' to continue long lines. You must include spaces or tabs
    around '=>' and '|'. That's within the grammar description itself(...?). The
    grammar that gets defined allows whitespace between tokens by default or
    specify '' as the second argument to grammar() to disallow this (or supply
    any regular expression to describe allowable whitespace between
    tokens)."""
    G = {' ': whitespace}
    description = description.replace('\t', ' ') # no tabs!
    for line in split(description, '\n'):
        lhs, rhs = split(line, ' => ', 1)
        #print("A: |%s|%s|" % (lhs, rhs))
        alternatives = split(rhs, ' | ')
        #print("A: alt (", alternatives, ")")
        G[lhs] = tuple(map(split, alternatives))
    return G

def split(text, sep = None, maxsplit = -1):
    "Like str.split applied to text, but strips whitespace from each piece."
    return [t.strip() for t in text.strip().split(sep, maxsplit) if t]

def parse(start_symbol, text, grammar):
    """Example call: parse('Exp', '3*x + b', G).
    Returns a (tree, remainder) pair. If remainder is '', it parsed the whole
    string. Failure iff remainder is None. This is a deterministic PEG parser,
    so rule order (left-to-right) matters. Do 'E => T op E | T', putting the
    longest parse first; don't do 'E => T | T op E'
    Also, no left recursion allowed: don't do 'E => E op T'

    See: http://en.wikipedia.org/wiki/Parsing_expression_grammar
    """

    tokenizer = grammar[' '] + '(%s)'

    def parse_sequence(sequence, text):
        """
        Try to match the sequence of atoms against text.

        Parameters:
        sequence : an iterable of atoms
        text : a string

        Returns:
        Fail : if any atom in sequence does not match
        (tree, remainder) : the tree and remainder if the entire sequence matches text
        """
        result = []
        for atom in sequence:
            tree, text = parse_atom(atom, text)
            if text is None: return Fail
            result.append(tree)
        return result, text

    @memo
    def parse_atom(atom, text):
        global DEBUG
        """
        Parameters:
        atom : either a key in grammar or a regular expression
        text : a string

        Returns:
        Fail : if no match can be found
        (tree, remainder) : if a match is found
            tree is the parse tree of the first match found
            remainder is the text that was not matched
        """
        if atom in grammar:  # Non-Terminal: tuple of alternatives
            for alternative in grammar[atom]:
                tree, rem = parse_sequence(alternative, text)
                #print("Parse atom 1 - rem: %s" % rem)
                if rem is not None: return [atom]+tree, rem
            return Fail
        else:  # Terminal: match characters against start of text
            if DEBUG: 
                print("D: |%s|%s|" % (atom, text))
            m = re.match(tokenizer % atom, text, re.UNICODE | re.MULTILINE)
            if DEBUG:
                if m: print("E: |%s|%s|" % (m.group(1), text[m.end():]))
            return Fail if (not m) else (m.group(1), text[m.end():])

    return parse_atom(start_symbol, text)

Fail = (None, None)

def decorator(d):
    "Make function d a decorator: d wraps a function fn."
    def _d(fn):
        return functools.update_wrapper(d(fn), fn)
    functools.update_wrapper(_d, d)
    return _d

@decorator
def memo(f):
    """Decorator that caches the return value for each call to f(args).
    Then when called again with same args, we can just look it up."""
    cache = {}
    def _f(*args):
        try:
            return cache[args]
        except KeyError:
            cache[args] = result = f(*args)
            return result
        except TypeError:
            # some element of args can't be a dict key
            return f(*args)
    _f.cache = cache
    return _f

G = grammar(r"""
Exp => Term [+-] Exp | Term
Term => Factor [*/] Term | Factor
Factor => Funcall | Var | Num | [(] Exp [)]
Funcall => Var [(] Exps [)]
Exps => Exp [,] Exps | Exp
Var => [a-zA-Z_]\w*
Num => [-+]?[0-9]+([.][0-9]*)?
""")

## Parsing URLs
## See http://www.w3.org/Addressing/URL/5_BNF.html

#URL = grammar("""
#url => httpaddress | ftpaddress | mailtoaddress
#httpaddress => http:// hostport /path? ?search?
#ftpaddress => ftp:// login / path ; ftptype | ftp:// login / path
#/path? => / path | ()
#?search? => [?] search | ()
#mailtoaddress => mailto: xalphas @ hostname
#hostport => host : port | host
#host => hostname | hostnumber
#hostname => ialpha . hostname | ialpha
#hostnumber => digits . digits . digits . digits
#ftptype => A formcode | E formcode | I | L digits
#formcode => [NTC]
#port => digits | path
#path => void | segment / path | segment
#segment => xalphas
#search => xalphas + search | xalphas
#login => userpassword hostport | hostport
#userpassword => user : password @ | user @
#user => alphanum2 user | alphanum2
#password => alphanum2 password | password
#path => void | segment / path | segment
#void => ()
#digits => digit digits | digit
#digit => [0-9]
#alpha => [a-zA-Z]
#safe => [-alpha | digit | safe | extra | escape
#""", whitespace = '()')$_@.&+]
#extra => [()!*''""]
#escape => % hex hex
#hex => [0-9a-fA-F]
#alphanum => alpha | digit
#alphanums => alphanum alphanums | alphanum
#alphanum2 => alpha | digit | [-_.+]
#ialpha => alpha xalphas | alpha
#xalphas => xalpha xalphas | xalpha
#xalpha => alpha | digit | safe | extra | escape
#""", whitespace = '()')

#~ 
#~ ящик = м. 1.  box; (упаковочный) packing-case;   почтовый ~ 
#~ letter-box, pillar-box; 2. (выдвижной) drawer; чёрный ~ black box;   
#~ откладывать в долгий ~ shelve, put* off.    
#~ ящур = м. мед. foot-and-mouth disease м. мед. foot-and-mouth 
#~ disease 

def verify(G):
    lhstokens = set(G) - set([' '])
    print(G.values())
    rhstokens = set(t for alts in G.values() for alt in alts for t in alt)
    def show(title, tokens): print( title, '=', ' '.join(map(repr, sorted(tokens))))
    show('Non-Terms', G)
    show('Terminals', rhstokens - lhstokens)
    show('Suspects', [t for t in (rhstokens-lhstokens) if t.isalnum()])
    show('Orphans ', lhstokens-rhstokens)

def check_result(res):
    if res == None: return False
    for x in range(len(res)):
        if res[x] != ' ': return False
    return True


RUEN = grammar("""
ru_word => plural gramtype_male gramtype_female oldest qualword descriptions
gramtype_male => (м\.)?
gramtype_female => (ж\.)?
qualword => (мед\.)?
plural => (мн\.)?
military => (воен\.)?
oldest => (уст\.)?
descriptions =>  description descriptions | description
description => digit translation additionals | digit additionals | digit translation | translation
digit => ([0-9].)? military | ([0-9].)?
en_words => en_word en_surrogate en_words | en_word \s en_words | en_word
en_word => en_letters
en_letters => ([a-zA-Z\-'`\(\)0-9]*)
translation => en_words separator | en_words comma | en_words end
comma => [,]
separator => [;]
end => [.]
translations => en_words comma translations | en_words separator | en_words end | end_words
additionals => additional surogate translations additionals | additional separator additionals | additional surrogate translations | surrogate translations | additional
additional => [(] meaning [)] translation surrogate translations | [(] meaning [)] translation | surrogate translation
surrogate => meaning [~] meaning | [~] meaning | meaning [~]
meaning => ru_letters
ru_letters => ([а-яА-Яё\-\s]*)
en_surrogate => en_word\* | \*
""")

def do_test(text):
    print("==== Text: %s" % text)
    result = parse('ru_word', text, RUEN)
    assert(check_result(result[-1]))
    print(result)

if __name__ == '__main__':
#    verify(G)
#    verify(RUEN)
    text =  '''м. 1.  box; (упаковочный)  packing-case; почтовый ~ 
letter-box, pillar-box; 2. (выдвижной) drawer; чёрный ~ black box; откладывать в долгий ~ shelve, put* off.''' 
    do_test(text)

    text = '''м. мед. foot-and-mouth disease.'''
    do_test(text)   
    
    text = '''мн. feast sg , viands, victuals. '''
    do_test(text)
    
    text = '''м. hawk; следить как ~ watch like a hawk. '''
    do_test(text)
    
    text = '''1. hawk`s; hawk attr. ; 2. (как у ястреба) hawklike; ~ взгляд   piercing glance; ~ нос hawk nose.  '''
    do_test(text)

    text = '''ж. 1.  cell; 2. воен. foxhole.'''
    do_test(text)

    text = '''barley attr. ; ~ое зерно grain of barley, barley-corn; 
~ая крупа barley; ~ая каша barley-milk. '''
    do_test(text)
    
    text = '''м. (на глазу) sty.'''
    do_test(text)
    
    text = '''м. (злак) barley. '''
    do_test(text)
    
    text = '''м. уст. 1.  (рубин) ruby; 2. (сапфир) sapphire.'''
    do_test(text)
    
    text = '''м. yat (name of old Russian letter replaced by in 1918) ;
на ~ разг. first class, splendid(ly). '''
    do_test(text)
    
    text = '''ж. adventure; (рискованное дело тж.) hazardous affair, 
gamble, venture; разг. shady enterprise; военная ~ military 
adventure/gamble; ~изм м. adventurism; ~ист м. adventurer; ~истка 
ж. adventuress; ~ный 1. (рискованный) risky, hazardous;   
(неблаговидный) shady, doubtful; 2. (приключенческий) adventure 
attr. ; ~ный   роман novel of adventure; (литературный   жанр) 
picaresque novel.'''
    print("==== Text: %s" % text)
    result = parse('ru_word', text, RUEN)
    print(result)
