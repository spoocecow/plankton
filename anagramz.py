import inspect
import os
import random
import string
from markov import levenshtein_distance

_thisfile = inspect.getfile( inspect.currentframe() )
cwd = os.path.dirname( os.path.abspath( _thisfile ) )

def has_digits(_str):
   for _l in _str:
      if _l in '0123456789':
         return True
   return False

def _is_substr(_target, _word):
   if len(_word) > len(_target):
      return False
   #assert isinstance(_target, str), "{!r} is {}".format(_target, type(_target))
   #assert isinstance(_word, str), "{!r} is {}".format(_word, type(_word))
   for _l in _word:
      if _word.count(_l) > _target.count(_l):
         return False
   return True

def _is_anagram(_w1, _w2):
   return tuple(sorted(_w1.replace(' ', ''))) == tuple(sorted(_w2.replace(' ', '')))

def _subtract(_base, _remove):
   l = list(_base)
   for c in _remove:
      if c in l:
         l.remove(c)
   return ''.join(l)

def _sanitize(_target:str) -> str:
   ok = []
   for c in _target:
      if c.upper() in string.ascii_uppercase:
         ok.append(c.upper())
      elif c.isspace():
         ok.append(' ')
   return ''.join(ok)

def words():
   with open(os.path.join(cwd, 'txt', 'wordlist.txt')) as wl_f:
      _words = tuple(sorted([l.strip() for l in wl_f.readlines() if (not l.startswith('#')) and (not has_digits(l)) and len(l.strip())>1], key=len, reverse=True))
   _words = _words + ('A', 'I', 'K', 'O', 'U')
   return _words


def get_anagram(target: str) -> list:
   target = _sanitize(target)
   cleantarget = target.replace(' ', '')
   candidates = [w for w in words() if _is_substr(cleantarget, w)]

   def _build(_target, _assembly, _candidates):
      if not _target:
         # we're done..?
         yield _assembly
         return
      for word in sorted(_candidates, key=len, reverse=True):
         if _is_substr(_target, word) and word not in target and word not in _assembly:

            newtarget = _subtract(_target, word)
            if newtarget == '':
               # we're done!
               yield _assembly + [word]
               return
            # it contributes, but does it screw us?
            # look for at least one word that is still in remainder TODO ensure entirety of remainder can be built with words?
            newcandidates = [w for w in _candidates if _is_substr(newtarget, w)]
            if not newcandidates:
               continue
            # keep goin!
            for _res in _build(newtarget, _assembly + [word], newcandidates):
               yield _res

   goo = _build(cleantarget, [], candidates)
   closest = ''
   for res in goo:
      restr = ' '.join(res)
      #print(restr)
      if _is_anagram(cleantarget, restr):
         return res
      elif levenshtein_distance(sorted(restr), sorted(target)) < levenshtein_distance(sorted(closest), sorted(target)):
         closest = restr
   return ["idk man sorry. I gave up at", closest]