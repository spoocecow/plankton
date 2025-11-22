import math
import os
import random
import re
import string
from typing import Never, Any, Generator


def has_digits(_str):
   for _l in _str:
      if _l in '0123456789':
         return True
   return False

def make_lookup() -> dict[str, list]:
    return {l: [] for l in string.ascii_uppercase}

g_words:list[str] = []
g_index = [
    make_lookup(),
    make_lookup(),
    make_lookup(),
    make_lookup(),
    make_lookup(),
]
g_smart = random.random() < 0.69

def load():
    global g_words
    global g_index

    with open(os.path.join('txt', 'wordlist.txt')) as f:
        g_words = [l.strip().upper() for l in f.readlines() if (not l.startswith('#')) and (not has_digits(l)) and len(l.strip()) == 5]

    for word in g_words:
        for i, letter in enumerate(word):
            g_index[i][letter].append(word)

def candidates(mask:str='.....', contains:str='', excludes:str='') -> Generator[str, Any, None]:
    # hard mode assumed for now
    m = re.compile(f'^{mask}$')
    for w in g_words:
        #if m.match(w) and c.search(w) and (not excludes or not e.search(w)):
        #    yield w
        #continue
        if m.match(w):
            # greens (or blanks) match, time to check for yellows (if any)
            for c in contains:
                if (mask.count(c) + contains.count(c)) > w.count(c):
                    break
            else:
                # yellows are also OK, now check for already-guessed letters
                for c in excludes:
                    if c in w:
                        break
                else:
                    yield w

def candidates2(history:list[tuple[str,str,str,str]]=[]) -> Generator[str, Any, None]:
    _, mask, cont, excludes = history[-1]
    m = re.compile(f'^{mask}$')
    prev_guesses = [t[0] for t in history]
    for w in g_words:
        if w in prev_guesses:
            continue
        if m.match(w):

            # greens (or blanks) match, time to check for yellows (if any)
            for c in cont:
                if (mask.count(c) + cont.count(c)) > w.count(c):
                    break
            else:
                # yellows are also OK, now check for already-guessed letters
                for c in excludes:
                    if c in w:
                        break
                else:
                    yield w
            continue

def eval_to_re(evstr:str) -> str:
    return re.sub(r"[a-z]", ".")

def pick(mask:str='.....', contains:str='', excludes:str='') -> str:
    return random.choice(tuple(candidates(mask, contains, excludes)))

def pick2(history:list[tuple[str,str,str,str]]=[]) -> str:
    _, mask, contains, excls = history[-1]
    excludes = ''.join([e.replace('.', '') for (_,_,_,e) in history])
    legal = list(candidates(mask, contains.replace('.', ''), excludes))
    # for prev_guess, _, prev_contains, _ in history:
    #     # never guess the same word again
    #     if prev_guess in legal:
    #         legal.remove(prev_guess)
    #         continue
    random.shuffle(legal)
    for cand in legal:
        ok = True
        for prev_guess, _, prev_contains, prev_excls in history:
            # ensure not a repeat guess
            if prev_guess == cand:
                ok = False
                break

            # smart pick would be to avoid making the same known-wrong guesses
            if g_smart:
                # yellow-space guesses
                if prev_contains != '.....' and re.match(prev_contains, cand):
                    ok = False
                # blank space guesses
                if prev_excls != '.....' and re.match(prev_excls, cand):
                    ok = False

        if ok:
            return cand
    raise IndexError("whatever I give up")


def eval_guess(secret:str, guess:str) -> (str, str, str, str):
    mask, contains, excludes, printout = '', '', '', ''

    for i, (sc, gc) in enumerate(zip(secret, guess)):
        if sc == gc:
            mask += sc
            printout += '🟩'
        elif gc in secret:
            # yellows are hard (cannot dupe with other matches)...
            #temp_contains[gc].append(gc)
            mask += '.'
            if (mask.count(gc) + contains.count(gc)) < secret.count(gc):
                contains += gc
            printout += '🟨'
        else:
            mask += '.'
            excludes += gc
            printout += '⬛'

    return mask, contains, excludes, printout

def eval_guess2(secret:str, guess:str) -> (str, str, str, str):
    mask, contains, excludes, printout = '', '', '', ''

    for i, (sc, gc) in enumerate(zip(secret, guess)):
        if sc == gc:
            mask += sc
            contains += '.'
            excludes += '.'
            printout += '🟩'
        elif gc in secret:
            # yellows are hard (cannot dupe with other matches)...
            #temp_contains[gc].append(gc)
            mask += '.'

            letter_isnt_also_correct_elsewhere = True
            for ii, (ss,gg) in enumerate(zip(secret, guess)):
                if ii == i:
                    continue
                if ss == gc == gg:
                    letter_isnt_also_correct_elsewhere = False
                    break
            if letter_isnt_also_correct_elsewhere:
            #if (mask.count(gc) + contains.count(gc)) < secret.count(gc):
                contains += gc
            else:
                contains += '.'
            excludes += '.'
            printout += '🟨'
        else:
            mask += '.'
            contains += '.'
            excludes += gc
            printout += '⬛'

    return mask, contains, excludes, printout


def update_stats(guesses, success, query_only=False) ->  dict[int | str, int]:
    import json
    fn = '.worble_stats.json'
    if os.path.exists(fn):
        with open(fn) as f:
            data = json.load(f)
    else:
        data = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 'Stumpers': 0}

    if not query_only:
        if success:
            data[str(guesses)] += 1
        else:
            data['Stumpers'] += 1
        with open(fn, 'w+') as f:
            json.dump(data, f)
    return data

def print_stats() -> str:
    stats = update_stats(0,0, query_only=True)
    total_plays = sum(stats.values())
    s = ""
    w = int(math.log10(total_plays))
    for g, t in sorted(stats.items()):
        if g != 'Stumpers':
            s += f"{g}/6: {t:0{w}} ({(t/total_plays)*100:.3}%)\n"
        else:
            s += f"???: {t:0{w}} ({(t/total_plays)*100:.3}%)\n"
    s += f"Tot: {total_plays}\n"
    s += f"Win: {((total_plays - stats['Stumpers'])/total_plays)*100:.3}%"
    return s


def play() -> str:
    global g_words
    global g_smart
    g_smart = random.random() < 0.8
    load()
    random.shuffle(g_words)
    secret = random.choice(g_words)
    # a good first guess shouldn't repeat letters
    if g_smart:
        bad = True
        while bad:
            guess = random.choice(g_words)
            for c in guess:
                if guess.count(c) != 1:
                    break
            else:
                bad = False
    else:
        guess = random.choice(g_words)
    rounds = 0
    final_str = ''
    if not g_smart:
        final_str += '{idiot}\n'
    excludes = ''
    history = []
    while rounds < 6:
        mask, cont, excl, round_str = eval_guess2(secret, guess)
        final_str += f"||`{guess}`||  {round_str}\n"
        if guess == secret:
            update_stats(rounds+1, True)
            return final_str
        history.append((guess, mask, cont, excl))
        excludes += excl
        try:
            #guess = pick(mask, cont, excludes)
            guess = pick2(history)
        except IndexError:
            final_str += "{stumped}\n"
            update_stats(rounds + 1, False)
            break
        rounds += 1
    final_str += "{lament}\n" + f"||`{secret}`||"
    update_stats(69, False)
    return final_str