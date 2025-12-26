import json
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

def valid(_str:str) -> bool:
    for c in _str.upper():
        if c not in string.ascii_uppercase:
            return False
    return True

g_words:list[str] = []
g_width = 5
g_smart = random.random() < 0.69

def load(wordlist:str=os.path.join('txt', 'wordlist.txt'), width=g_width):
    global g_words

    with open(wordlist) as f:
        # set() construction is to remove duplicates (e.g. 'Jewel' and 'jewel' are both in american-english)
        g_words = list(set([l.strip().upper() for l in f.readlines() if (not l.startswith('#')) and valid(l.strip()) and len(l.strip()) == width]))


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
    blank = [' '] * g_width
    mask, contains, excludes, printout = blank[:], blank[:], blank[:], blank[:]
    secret_copy = list(secret)

    # first pass: green and black
    for i, (sc, gc) in enumerate(zip(secret, guess)):
        if sc == gc:
            # correct, green square dat sucka
            mask[i] = sc
            contains[i] = '.'
            excludes[i] = '.'
            printout[i] = '🟩'  # green
            secret_copy[i] = '.'  # remove correct letters for subsequent yellow pass
        else:
            # incorrect, could be yellow or black - default to black for now
            mask[i] = '.'
            contains[i] = '.'
            if gc not in secret:
                # this guessed character doesn't appear in secret
                excludes[i] = gc
            printout[i] = '⬛'  # black

    # second pass: yellows
    for i, gc in enumerate(guess):
        if gc in secret_copy:
            contains[i] = gc
            excludes[i] = '.'
            printout[i] = '🟨'  # yellow
            secret_copy[secret_copy.index(gc)] = '.'  # remove left-to-right (this is my arbitrary choice, I don't know what the real game does) for subsequent guesses

    return ''.join(mask), ''.join(contains), ''.join(excludes), ''.join(printout)

    for i, (sc, gc) in enumerate(zip(secret, guess)):

        if sc == gc:
            # correct, green square dat sucka
            mask += sc
            contains += '.'
            excludes += '.'
            printout += '🟩'  # green
        elif gc in secret:
            # yellows are hard (cannot dupe with other matches)...
            #temp_contains[gc].append(gc)
            mask += '.'

            letter_elsewhere = False
            for ii, (ss,gg) in enumerate(zip(secret, guess)):
                if ii == i:
                    # we're checking this letter (index) in the outer loop
                    continue
                if ss == gc == gg:
                    # correct guess, we'll catch that in the first `if sc == gc` above
                    continue
                elif ss == gc:
                    # the guessed letter appears somewhere else in the secret :O
                    letter_elsewhere = True
                    break
                else:
                    # this letter in the secret is not what was guessed, don't care
                    continue

            if letter_elsewhere:
                contains += gc
                printout += '🟨'  # yellow
            else:
                contains += '.'
                printout += '⬛'  # black
        else:
            mask += '.'
            contains += '.'
            excludes += gc
            printout += '⬛'  # black

    return mask, contains, excludes, printout

g_default_stats = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 'Stumpers': 0}

def update_stats(player, guesses):
    if player not in g_state['hof']:
        g_state['hof'][player] = g_default_stats.copy()
    if guesses > 6:
        guesses = 'Stumpers'
    g_state['hof']['player'][guesses] += 1
    save_state(g_state)

def print_stats(player='Klungo') -> str:
    if 'hof' not in g_state:
        return "No one played ever :("
    if player not in g_state['hof']:
        return f"{player} never played ever :("
    stats = g_state['hof'][player]
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


def autoplay() -> str:
    global g_words
    global g_smart
    g_smart = random.random() < 0.8
    load()
    #random.shuffle(g_words)
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
            update_stats('Klungo', rounds+1)
            return final_str
        history.append((guess, mask, cont, excl))
        excludes += excl
        try:
            #guess = pick(mask, cont, excludes)
            guess = pick2(history)
        except IndexError:
            final_str += "{stumped}\n"
            update_stats('Klungo', 'Stumpers')
            break
        rounds += 1
    final_str += "{lament}\n" + f"||`{secret}`||"
    update_stats('Klungo', 'Stumpers')
    return final_str

state_fn = '.worble_state.json'

default_state = {
    'number': 0,
    'guesses': 0,
    'history': [],
    'secret': '',
    'hof': {},
}
g_state = default_state.copy()

def get_state():
    if not os.path.exists(state_fn):
        return default_state
    with open(state_fn) as state_f:
        return json.load(state_f)

def save_state(state:dict):
    with open(state_fn, 'w+') as f:
        json.dump(state, f)

def reset_state(state:dict) -> dict:
    s = state.copy()
    s['history'] = list()
    s['guesses'] = 0
    if 'number' not in s:
       s['number'] = 0
    s['secret'] = ''
    return s

def clear_persistent_state():
    save_state(default_state)

def avail_guessos(guess:str) -> tuple[int,str]:
    best = 9999999999
    bestw = '?????'
    load('/usr/share/dict/american-english')
    for w in g_words:
        mask, cont, excl, rs = eval_guess2(w, guess)
        legal = list(candidates(mask, cont.replace('.', ''), excl))
        for cand in legal[:]:
            ok = True
            # yellow-space guesses
            if cont != '.....' and re.match(cont, cand):
                ok = False
            # blank space guesses
            if excl != '.....' and re.match(excl, cand):
                ok = False
            if not ok:
                legal.remove(cand)
        if len(legal) < best:
            best = len(legal)
            bestw = w
    return best, bestw

def play_round(secret, guess, state=None) -> tuple[bool|None, str, dict]:
    if not state:
        state = default_state.copy()
        state['secret'] = secret
    if not g_words:
        global g_width
        g_width = len(secret)
        load('usr/share/dict/american-english', g_width)
    m,c,e,r = eval_guess2(secret, guess)
    state['guesses'] += 1
    rs = f"{state['guesses']} {r}"
    if guess == secret:
        state['number'] += 1
        return True, "Congratulations, {player}!", state
    elif state['guesses'] >= 6:
        state['number'] += 1
        return False, f"Sory {{player}} that sux. it was ||{secret}||", state
    else:
        state['history'].append((guess, m, c, e))
        excludes = ''.join([e.replace('.', '') for (_, _, _, e) in state['history']])
        state['total_excludes'] = excludes
        legal = list(candidates(m, c.replace('.', ''), excludes))
        for cand in legal[:]:
            ok = True
            for prev_guess, _, prev_contains, prev_excls in state['history']:
                # ensure not a repeat guess
                if prev_guess == cand:
                    ok = False
                    break
                # yellow-space guesses
                if prev_contains != '.....' and re.match(prev_contains, cand):
                    ok = False
                # blank space guesses
                if prev_excls != '.....' and re.match(prev_excls, cand):
                    ok = False
            if not ok:
                legal.remove(cand)
        state['options'] = legal[:]
        return None, rs + f"||btw: you have {len(legal)} options||", state

def play(player:str, line:str) -> str:
    global g_state
    g_state = get_state()
    retval = ''
    if m := re.search(r"\W?([A-Z)]{5,})\W?", line.upper()):
        guess = m.group(1)
    else:
        return 'what u guess ?'

    if not g_state['secret'] or g_state['guesses'] <= 0:
        global g_width
        secret = ''
        width = len(guess)
        load('/usr/share/dict/american-english', width)  # Vorpy will summon a meteor on me if I use my regular wordlist here. hey vorpy. this ships with linux. you can't get mad at me for this. or you shouldn't, anyway. you can still get mad if you want to. i'm not the police.
        if len(g_words) > 0:
            secret = random.choice(g_words)
        else:
            return "No words are that long (I recommend MAX 12-13 for variety's sake). anyway go 2 hell"
        g_width = width
        g_state['secret'] = secret
        if g_width > 5:
            retval += "Wow u brave... Brave Mode Enabled. brave mode turn on. we get signal...\n"
    else:
        secret = g_state['secret']

    if len(guess) < len(secret):
        return f'Current secret is {len(secret)} letters, u only guessed {len(guess)} u silly billy'

    if len(secret) > 5 and guess not in g_words:
        example = pick2(g_state['history'])
        return f"BRAVERY REQUIRES A PRICE. YOU MUST GUESS WORDS I RECOGNIZE. ||May I suggest {example}?||"

    g_state['guesses'] += 1
    try:
        mask, cont, excl, rs = eval_guess2(secret, guess)
        retval += f"{g_state['guesses']} {rs}"
        if guess == secret:
            retval += f"\nCongratulations, {player}!"
            update_stats(player, g_state['guesses'])
            g_state['number'] += 1
            g_state = reset_state(g_state)
        elif g_state['guesses'] >= 6:
            retval += f"\nSory {player} that sux. it was ||{secret}||"
            update_stats(player, 'Stumpers')
            g_state['number'] += 1
            g_state = reset_state(g_state)
        else:
            g_state['history'].append( (guess, mask, cont, excl) )
            excludes = ''.join([e.replace('.', '') for (_, _, _, e) in g_state['history']])
            g_state['total_excludes'] = excludes
            legal = list(candidates(mask, cont.replace('.', ''), excludes))
            for cand in legal[:]:
                ok = True
                for prev_guess, _, prev_contains, prev_excls in g_state['history']:
                    # ensure not a repeat guess
                    if prev_guess == cand:
                        ok = False
                        break
                    # yellow-space guesses
                    if prev_contains != '.....' and re.match(prev_contains, cand):
                        ok = False
                    # blank space guesses
                    if prev_excls != '.....' and re.match(prev_excls, cand):
                        ok = False
                if not ok:
                    legal.remove(cand)
            retval += f" ||btw: you have {len(legal)} options if u play by hard mode rules||"
        return retval
    finally:
        save_state(g_state)
