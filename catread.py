# coding=utf-8
import math
import random
import re
import os, sys
import logging

g_log = logging.getLogger('catread')
shandle = logging.StreamHandler(stream=sys.stdout)
fhandle = logging.FileHandler('catread.log')
g_log.addHandler(shandle)
g_log.addHandler(fhandle)

WIDTH = 49

g_nickBlacklist = ['Colliwobble']
g_wordBlacklist = ['Klungo', '!logread', '!joke', '']

g_LOGDIR = os.path.join('.never', 'logs')


def format_lines_old(msg, maxwidth=WIDTH):
    lines = ['']
    line_num = len(msg) / maxwidth
    wordos = msg.split()
    words = []
    for w in wordos:
        temp_w = [w]
        if len(w) > (maxwidth/2): # long spammy line, go ahead and split
            mp = len(w) / 2
            temp_w = [ w[:mp], w[mp:] ]
        words.extend(temp_w)
    while words:
        if len(lines[-1]) >= maxwidth:
            lines.append('')
        word = words.pop(0)
        lines[-1] += word + ' '
    return map(str.strip, lines)


def format_lines(msg, maxwidth=WIDTH):
    lineno = math.ceil(len(msg) / maxwidth)
    if lineno >= 4:
        linelen = maxwidth
    else:
        linelen = (len(msg) / lineno) * 1.25  # allow for some wiggle room
    lines = [u'']
    raw_words = msg.split()
    words = []
    for w in raw_words:
        words.append(w)
    for w in words:
        if (len(lines[-1]) + 1 +  len(w)) > linelen:
            lines.append(u'')
        lines[-1] += u' ' + w
    return [s.strip() for s in lines]



def catsay(msg, nick='A Cat', date=''):
   catfmt = r"""
                   {0}
 _        /|__/\   {1}
//_______/ .  . \  {2}
\  C   T     i  / <{3}
 \   A____    |    {4}
 | ||     | ||     {5}
 |__\\    |__\\    {6}
   """
   lines = format_lines(msg, WIDTH)
   if len(lines) > 5:
      g_log.error("This was too long: %s", msg)
      return None
   balloon_width = max( map(len, lines) )
   top_line = ' ' + '_' * (balloon_width+2) + ' '
   bottom_line = '\\' + '_' * (balloon_width+2) + '/'
   blank_line = ''
   fmted_lines = ['| %s |' % line.center(balloon_width) for line in lines]
   middle_line_i = 3
   vertical_centered_lines = [top_line] + fmted_lines[:] + [bottom_line]
   while len(vertical_centered_lines) < 7:
      if len(vertical_centered_lines) % 2 == 0:
         vertical_centered_lines.append(blank_line)
      else:
         vertical_centered_lines.insert(0, blank_line)
         vertical_centered_lines.append(blank_line)
   assert len(vertical_centered_lines) == 7, "zuhh? %d" % len(vertical_centered_lines)
   vertical_centered_lines[middle_line_i] = ' ' + vertical_centered_lines[middle_line_i][1:]
   if vertical_centered_lines[-1] == blank_line:
       if date:
           vertical_centered_lines[-1] =  ('~ %s, %s' % (nick, date)).rjust(balloon_width+4)
       elif nick:
           vertical_centered_lines[-1] =  ('~ %s' % nick).rjust(balloon_width+4)
       else:
           vertical_centered_lines[-1] =  ('~ %s' % nick).rjust(balloon_width+4)
   return catfmt.format(
      *vertical_centered_lines, width=balloon_width
   )

def sanitize(line):
    import string
    return ''.join([c for c in line if c in string.printable])

def is_line_bad(nick, text):
    if nick in g_nickBlacklist:
        return True
    for bl_word in g_wordBlacklist:
        if bl_word in text:
            return True
    return False

def get_line(log):
    with open(log, encoding='ansi') as logfile:
        logging.debug("opening %s", log)
        lines = logfile.readlines()
        line_bad = True
        is_speech = re.compile(
            r"""
            [¡\[]?(?P<timestamp>\d\d:\d\d[:.]\d\d)[\]!] # timestamp
            \s+<[\s\d]*(?P<nick>[\w\d_\\]+).*>  # nick
            \s+(?P<text>.*)\s*
            """,
            re.IGNORECASE | re.MULTILINE | re.VERBOSE
        )
        original_line = random.choice(lines)
        line = sanitize( original_line.strip() )
        while line_bad:
            match = is_speech.search(line)
            if match:
                nick = match.group('nick')
                text = match.group('text')
                tstamp = match.group('timestamp')
                if is_line_bad(nick, text):
                    g_log.info( "this line bad: %s", line)
                elif text.startswith('!'):
                    # boring read bad I hate it
                    g_log.debug("this line boring: %s", line)
                else:
                    g_log.info("Good: %s", match.groupdict())
                    info = match.groupdict()
                    try:
                        date = tstamp + ' ' + find_date(original_line, lines)
                    except ValueError:
                        date = ''
                    info['date'] = date
                    return info
            original_line = random.choice(lines)
            line = sanitize( original_line.strip() )
        return {}

def find_date(line, loglines):
    line_i = loglines.index(line)
    date = ''
    for log_l in reversed(loglines[:line_i]):
        if log_l.startswith('Session Start:'):
            _, _, wd, m, d, t, y = log_l.split()
            return '%s %s %s' % (m,d,y)

def get_logfile():
    return os.path.join(g_LOGDIR, random.choice(os.listdir(g_LOGDIR)) )


def get_catread(data=None):
    if data:
        line = data
        msg = catsay(line)
    else:
        logfile = get_logfile()
        retries = 5
        msg = None
        while not msg:
            line_info = get_line(log=logfile)
            line = line_info.get('text')
            nick = line_info.get('nick')
            date = line_info.get('date')
            msg = catsay(line, nick, date)
            retries -= 1
            if retries < 0:
                return ''
    if msg.startswith('\n'):
        msg = msg[1:]
    while re.match('^\s+$', msg, re.MULTILINE | re.UNICODE):
        msg = msg[msg.find('\n')+1:]
    return msg

