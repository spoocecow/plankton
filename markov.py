#!/usr/bin/python
# Really simple Markov chain-based text generator.
import json
import sys
import random
import re
import os

N = 4
STOP = "\n"
TABLE = {}
BY_WORD = False

def levenshtein_distance(first, second):
    """Find the Levenshtein distance between two strings.
    Taken from http://www.korokithakis.net/node/87"""
    if len(first) > len(second):
        first, second = second, first
    if len(second) == 0:
        return len(first)
    first_length = len(first) + 1
    second_length = len(second) + 1
    distance_matrix = [[0] * second_length for _ in range(first_length)]
    for i in range(first_length):
       distance_matrix[i][0] = i
    for j in range(second_length):
       distance_matrix[0][j]=j
    for i in range(1, first_length):
        for j in range(1, second_length):
            deletion = distance_matrix[i-1][j] + 1
            insertion = distance_matrix[i][j-1] + 1
            substitution = distance_matrix[i-1][j-1]
            if first[i-1] != second[j-1]:
                substitution += 1
            distance_matrix[i][j] = min(insertion, deletion, substitution)
    return distance_matrix[first_length-1][second_length-1]

class Record(object):
    def __init__(self, start:str):
        self.start = start # ex. 'qua'
        self.__hash = hash(start.lower())
        self.count = 1
        self.goto = {} # ex. 'qua'.goto = { 'ck ': 3, 'rk ': 2, 'int': 1 }

    def add(self, entry):
        if entry not in self.goto:
            self.goto[entry] = 0
        self.goto[entry] += 1
        self.count += 1
            
    def build(self, target_length=100):
        if self.start == STOP:
            return self.start
        n = self.pick()
        if not n or target_length<random.randint(-5,5 ):
            return self.start
        else:
            if BY_WORD:
                return self.start + " " + n.build(target_length-len(self.start)-1)
            else:
                return self.start + n.build(target_length-len(self.start))

    def next(self, hint=None):
        if not hint:
            return self.pick( self.start )

        if hint in self.goto:
            return self.pick(hint)
        else:
            distances = [(levenshtein_distance(hint,x),x) for x in list(self.goto.keys())]
            # ex. [(1,'ck '), (2, 'rk '), (3, 'int')]
            return self.pick( min(distances)[1] )

    def pick(self, e_text=None):
        if not e_text:
            e_text = self.start
        entry = TABLE[e_text]
        t = entry.count
        n = random.uniform(0, t)
        for txt in entry.goto:
            count = entry.goto[txt]
            if n < count:
                return txt
            n = n - count
        return None

    def __hash__(self):
        return self.__hash

    def __str__(self):
        return "record("+self.start+")"
        

def read_file(filename:str, mode='r'):
    global TABLE
    if 'b' in mode:
        """
        f = open(filename, mode, errors='ignore')
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        ValueError: binary mode doesn't take an errors argument
        """
        # why the FUCK doesn't python just take care of this for me. shut the fuck up man
        f = open(filename, mode)
    else:
        f = open(filename, mode, errors='ignore')
    if not f:
        return

    text = f.read()
    f.close()

    if BY_WORD:
        text = text.replace("\n"," ")
        text = text.replace("\f", " ")
        text = text.replace("\r", " ")
        text = text.split()
        word = None

        for follow in text:
            if follow not in TABLE:
                TABLE[follow] = Record( follow )
            if word:
                TABLE[word].add( TABLE[follow] )
            word = follow
        return
    else:
        # byte fer byte, gad damn right
        i = 0
        base = text[i:i+N]
        while i+N < len(text):
            if base not in TABLE:
                TABLE[base] = Record(base)
            follow = text[i+N:i+N+N]
            if follow not in TABLE:
                TABLE[follow] = Record(follow)
            TABLE[base].add( TABLE[follow] )
            i += 1
            base = text[i:i+N]

def sanitize(line):
    import string
    return ''.join([c for c in line if c in string.printable])

def log_nick_ok(line):
    blacklist = ['Klungo', 'ChanServ']
    for dont_copy in blacklist:
        if dont_copy in line:
            return False
    return True

def read_log(filename):
    with open(filename, encoding='ansi') as f:
        log = f.readlines()

    if BY_WORD:
        text = []
        for line in log:
            line = sanitize(line.strip())
            nick,junk,l = line.partition(">")
            if l and log_nick_ok(nick):
                text.extend(l.split())
                text.append("\n")

        word = None
        for follow in text:
            if follow not in TABLE:
                TABLE[follow] = Record( follow )
            if word:
                TABLE[word].add( TABLE[follow] )
            word = follow
    else:
        text = ''
        for line in log:
            line = sanitize(line.strip())
            nick,junk,l = line.partition(">")
            if l and log_nick_ok(nick):
                text += l + '\n'
        i = 0
        base = text[i:i+N]
        while i+N < len(text):
            if base not in TABLE:
                TABLE[base] = Record(base)
            follow = text[i+N:i+N+N]
            if follow not in TABLE:
                TABLE[follow] = Record(follow)
            TABLE[base].add( TABLE[follow] )
            i += 1
            base = text[i:i+N]

def add_line(line):
    line = line.strip()
    line = line.split()
    word = None
    for follow in line:
        if follow not in TABLE:
            TABLE[follow] = Record( follow )
        if word:
            TABLE[word].add( TABLE[follow] )
        word = follow

def scan(base_dir:str, file_ext:str='.txt', mode='r'):
    for b, ds, fs in os.walk(base_dir):
        for f in fs:
            if not f.endswith(file_ext):
                continue
            fn = os.path.join(b, f)
            print(f"Reading: {fn}")
            read_file(fn, mode)

def talk(hint=None, l=50):
    if not hint:
        start = random.choice( list( TABLE.values() ) )
    elif hint not in TABLE:
        least = 1000
        least_w = random.choice( list( TABLE.keys() ) )
        print("random key:",least_w)
        for w in hint.split():
            if w in TABLE:
                least_w = w
                break
            for i in range(l):
                start = random.choice( list( TABLE.keys() ) )
                d = levenshtein_distance(hint, start)
                if d < least:
                    least = d
                    least_w = start
        start = TABLE[least_w]
    else:
        start = TABLE[hint]
    print("start = <%s>" % start)
    s = start.build(l)
    i = 0
    while len(s) < l:
        s = start.build(l)
        i += 1
        if i > l:
            return None
    return s

def make_midi():
    import funmid
    while True:
        m = talk('MThd', l=random.randint(2*1024, 16*1024))
        if not m:
            continue
        d = funmid.MidiFile.from_bytes(m)
        if d:
            return m

def midi(l=2048):
    import funmid
    while True:
        m = TABLE['MThd'].build(l)
        if not m: continue
        assert isinstance(m, str)
        if d:= funmid.MidiFile.from_bytes(m.encode('utf-8', errors='ignore')):
            return m

class Tweeter:

    N = 5

    START = '\uFFFF' * N
    END   = '\u0000' * N


    assert len(START) == N
    assert len(END) == N

    def __init__(self):
        self.table = {}

    def _learn(self, text:str):
        i = 0
        n = self.N
        base = text[i:i+n]
        while i+n < len(text):
            if base not in self.table:
                self.table[base] = Record(base)
            follow = text[i+n:i+n+n]
            if follow not in self.table:
                self.table[follow] = Record(follow)
            self.table[base].add( self.table[follow] )
            i += 1
            base = text[i:i+n]

    def _pick(self, key:str):
        entry = self.table[key]
        t = entry.count
        n = random.uniform(0, t)
        for txt in entry.goto:
            count = entry.goto[txt]
            if n < count:
                return txt
            n = n - count
        return None

    def load_tweets(self):
        tweet_fn = 'txt/tweets.json'
        with open(tweet_fn) as f:
            j = json.load(f)

        for entry in j:
            t = entry['tweet']
            body = t['full_text']
            if body.startswith('RT @'):
                # retweet, don't care rn
                continue
            elif body.startswith('@'):
                # me atting someone ehhhhhh. remove the username at least
                body = re.sub(r"^@\w+", '', body)
            self._learn(self.START + body.strip() + self.END)

    def _get(self, hint=''):
        twt = ''
        if hint:
            node = self._pick(hint)
        else:
            node = self._pick(self.START)
        while node and node.start != self.END:
            twt += node.start
            node = self._pick(node.start)
        return twt.strip(self.END)

    def tweet(self, min_length=10) -> str:
        rv = self._get()
        while len(rv) < min_length:
            rv = self._get()
        return rv


class Faqer(Tweeter):

    N = 4
    START = '\uFFFF' * N
    END   = '\u0000' * N


    assert len(START) == N
    assert len(END) == N

    def load_faqs(self):
        faq_dir = 'txt/gamefaqs'
        for base, subdirs, files in os.walk(faq_dir):
            for fn in files:
                if not fn.endswith('.txt'):
                    continue
                print(f"Laoading {fn}")
                self._load_faq(os.path.join(base, fn))

    def _load_faq(self, faq_fn:str):
        with open(faq_fn, errors='ignore') as faq_f:
            faq = faq_f.read()
        for paragraph in re.split(r'\n\s*\n+', faq):
            pp = paragraph.strip()
            if len(pp) < self.N:
                continue
            self._learn( self.START + pp + self.END )

    def give_tip(self, min_length=60) -> str:
        start_hints = (self.START, self.START, self.START, self.START, 'You ', 'Try ', 'The ', 'When', 'Next')
        while True:
            rv = ''
            tries = 20
            while len(rv) < min_length:
                hint = random.choice(start_hints)
                rv = self._get(hint)
                tries -= 1
                if tries < 0:
                    break
            return rv


def main(argv):

    for arg in argv:
        read_log(arg)

    for i in range(20):
        print(talk('hey'))
        print("-------------")


if __name__ == "__main__":
    main(sys.argv[1:])
