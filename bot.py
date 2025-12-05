"""
funny bot for plankton discord
spoocecow 2021-*
"""
import datetime
import functools
import logging
import os
import random
import re
import socket
import stat
import string
import subprocess
import time
from typing import List

import discord
from discord.ext import commands

import anagramz
import catread
import funmid
import midi2vox
import thingbarf
import worble


logging.basicConfig(level=logging.DEBUG)

g_markovproc = None


def clock_time_cache(max_age_s=300) -> callable:
   """
   Cache the results of a particular function call for a particular timespan (in seconds).

   Useful for caching expensive calls that we still might want to have live-ish updates of,
   such as HTTP requests.

   :param max_age_s: maximum age of cached results
   :return: result of decorated function, with previous calls cached appropriately
   """

   _cache = {}
   _access_times = {}

   def _wrapper(func) -> callable:
      @functools.wraps(func)
      def _inner(*args, **kwargs):
         # index based on function and passed-in arguments
         key = hash( (func, args, tuple(kwargs.items())) )

         # return cached value iff the cache has not expired (and it exists for this call in the first place)
         if (time.time() - _access_times.get(key, 0)) < max_age_s and _cache.get(key):
            logging.debug("returning cached value ({} to expiry)".format(max_age_s - (time.time() - _access_times[key])))
            return _cache[key]
         _access_times[key] = time.time()
         _cache[key] = func(*args, **kwargs)
         return _cache[key]
      return _inner

   return _wrapper

intents = discord.Intents(messages=True, guilds=True, message_content=True)
bot = commands.Bot(command_prefix='!', intents=intents)

def levenshtein_distance(first, second):
   """Find the Levenshtein distance between two strings.
   Taken from http://www.korokithakis.net/node/87"""
   if len(first) > len(second):
      first, second = second, first
   if len(second) == 0:
      return len(first)
   first_length = len(first) + 1
   second_length = len(second) + 1
   distance_matrix = [[0] * second_length for x in range(first_length)]
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

import pickle
if os.path.exists('jail'):
   with open('jail', 'rb+') as jailf:
      jail = pickle.load(jailf)
else:
   jail = {}

@bot.command(name='gimme')
async def _thingbarf(ctx: commands.Context, *, line: str):
   """Get some examples of some number of things"""
   global jail
   asker = ctx.author.name.lower()
   for f in dir(ctx.author):
      print("{}: {}".format(f, getattr(ctx.author,f)))

   if asker in jail and jail[asker] >= 10:
      await ctx.send("Your sins have caught up to you.")
      return

   msg = thingbarf.thingsay(line)
   if "Didn't recognize this thing" in msg or "u are a " in msg:
      best_guess = 9999999
      probable_thing = ''
      # what were they trying to do?
      if '`' in msg:
         guessed_thing = re.search('`(.+?)`', msg).group(1)
         for thing in thingbarf.g_thing_map:
            guess = levenshtein_distance(thing, guessed_thing)
            if guess < best_guess:
               best_guess = guess
               probable_thing = thing
      else:
         # just being a fucker
         guessed_thing = 'who cares'
      print("{} != {}, score {}".format(guessed_thing, probable_thing, best_guess))
      if best_guess >= 3 and 'trev' in asker:
         # jail
         criminal = asker
         with open('jail', 'ab+') as jailf:
            if jail.get(criminal, 0) >= 10:
               await ctx.send("Think about what you have done.")
               return
            else:
               if criminal in jail:
                  jail[criminal] += 1
               else:
                  jail[criminal] = 1
               pickle.dump(jail, jailf)
         await ctx.send("The criminal {c} has {n} Hilarious Jokes remaining.".format(c=criminal, n=10-jail[criminal]))
         return

   await ctx.send(msg)


#@clock_time_cache(max_age_s=60)
def get_lines(fn: str) -> List[str]:
   try:
       with open(fn) as f:
          return [l.strip() for l in f.readlines() if l.strip()]
   except UnicodeError:
       with open(fn, 'rb') as f:
          return [l.strip() for l in f.read().decode('cp437').splitlines() if l.strip()]  # python3 is so annoying


def get_rand_lines(fn, n=1):
   lines = get_lines(fn)
   return [l.strip() for l in random.sample(lines, n)]


def get_rand_line(fn):
   return get_rand_lines(fn, 1)[0]


@bot.command()
async def english(ctx: commands.Context):
   """Learn english dialect words from the 1700s"""
   fn = os.path.join('txt', '18thCdialectdict.txt')
   msg = get_rand_line(fn)
   await ctx.send( msg )


@bot.command()
async def plot(ctx: commands.Context):
   """It's da classic plot device"""
   getchar  = lambda: get_rand_line( os.path.join('txt', 'plot', 'char.txt') )
   getplace = lambda: get_rand_line( os.path.join('txt', 'plot', 'place.txt') )
   getverb  = lambda: get_rand_line( os.path.join('txt', 'plot', 'verb.txt') )
   getenemy = lambda: get_rand_line( os.path.join('txt', 'plot', 'enemy.txt') )
   getgoal  = lambda: get_rand_line( os.path.join('txt', 'plot', 'goal.txt') )
   getname  = lambda: get_rand_line( os.path.join('txt', 'plot', 'stupidnames.txt') )
   msg = 'Video Game Plot Summary: **{char}** from **{place}** must **{verb} {enemy}** in order to **{goal}**'
   s = msg.format(
      char=getchar(),
      place=getplace(),
      verb=getverb(),
      enemy=getenemy(),
      goal=getgoal()
   )
   while '$' in s:
      s = s.replace(
         '$read %plotchar', getchar()
      ).replace(
         '$read %plotplace', getplace()
      ).replace(
         '$read %plotverb', getverb()
      ).replace(
         '$read %plotenemy', getenemy()
      ).replace(
         '$read %plotgoal', getgoal()
      ).replace(
         '$read "stupidnames.txt"', getname()
      ).replace(
         '$nick($chan,$rand(1, $nick($chan,0)))', getname()  # TODO how to get server list?
      ).replace(
         ' $+ ', ''
      )
   await ctx.send(s)


@bot.command()
async def funcat(ctx: commands.Context):
   """It's funcat."""
   await ctx.send(
      r"""``` _        /|__/\
//_______/ .  . \
\  F    N    i  /
\   _U____    |
|  ||     |  ||
|__\\     |__\\```"""
   )

@bot.command()
async def copycat(ctx: commands.Context):
   """It's copycat."""
   await ctx.send(
      r"""```                     ___________________
                    /                   \    
                   /    _        /|__/\  \  
 _        /|__/\   |   //_______/ .  . \  |   
//_______/ .  . \  |   \  F    N    i  /  |   
\  F    N    i  / <    \   _U____    |    |  
\   _U____    |    |   |  ||     |  ||    |   
|  ||     |  ||     \  |__\\     |__\\   /     
|__\\     |__\\      \__________________/```"""
   )


@bot.command()
async def tgif(ctx: commands.Context):
   """Thank G*d It's Friday!"""
   today = time.localtime().tm_wday
   if today != 4:
      if random.random() < 0.0113:
         THE_FATED_DAY = datetime.datetime.fromtimestamp(
            time.time() + ( random.random() * 2**32 )
         )
         await ctx.send("You will die on {day}, at {time}.".format(
            day=THE_FATED_DAY.strftime('%A, %B %m, %Y'),
            time=THE_FATED_DAY.strftime('%I:%M %p')
         ))
         return
      day = time.strftime('%A')
      srystr = "{sry} {friend} {its} {day}".format(
         sry=random.choice(['sorry', 'sorry', 'Well', 'Sorry', "I'm sorry", "ごめんなさい"]),
         friend=random.choice(['pal', 'friend', 'bud']) + random.choice([',', '...', ',', '', '']),
         its='it' + random.choice(["'s", "s", ""]) + random.choice(['', '', '', ' surprisingly', ' actually']),
         day=random.choice([day.lower(), day, 'not Friday'])
      )
      confused_opts = (
         f'it is {day.lower()} my dudes',
         f'it is {day.lower()} my dudes',
         f'Happy {day} :)',
         f'Happy {day} :)',
         f"Thank Grunty It's {day}!",
         f"Thank Grunty It's Not Friday! (villains hate friday) (im a villain)",
         f'TGI.... {day}?!?!?',
         f'TGI... {day}???',
         f"TGI{day[0]}... hey wait",
         f"TGI{day[0]}... hey wait",
         f"in my opinion, it's {day} today.",
         "darkter beppery",
         srystr,
         srystr,
         srystr,
         srystr,
         srystr,
      )
      opt = random.choice(confused_opts)
      await ctx.send(opt)
      return

   msg = ''
   if random.random() <= 1/13.:
      msg = get_rand_line( os.path.join('txt', 'greetz.txt') ) + '\n'
   msg += random.choice( (
      """
████████╗░██████╗░██╗███████╗
╚══██╔══╝██╔════╝░██║██╔════╝
░░░██║░░░██║░░██╗░██║█████╗░░
░░░██║░░░██║░░╚██╗██║██╔══╝░░
░░░██║░░░╚██████╔╝██║██║░░░░░
░░░╚═╝░░░░╚═════╝░╚═╝╚═╝░░░░░
      """,
      """
▀█▀ █▀▀ █ █▀▀
░█░ █▄█ █ █▀░
      """,
      """
─────────────────────────────────────────────────────────
─██████████████─██████████████─██████████─██████████████─
─██░░░░░░░░░░██─██░░░░░░░░░░██─██░░░░░░██─██░░░░░░░░░░██─
─██████░░██████─██░░██████████─████░░████─██░░██████████─
─────██░░██─────██░░██───────────██░░██───██░░██─────────
─────██░░██─────██░░██───────────██░░██───██░░██████████─
─────██░░██─────██░░██──██████───██░░██───██░░░░░░░░░░██─
─────██░░██─────██░░██──██░░██───██░░██───██░░██████████─
─────██░░██─────██░░██──██░░██───██░░██───██░░██─────────
─────██░░██─────██░░██████░░██─████░░████─██░░██─────────
─────██░░██─────██░░░░░░░░░░██─██░░░░░░██─██░░██─────────
─────██████─────██████████████─██████████─██████─────────
─────────────────────────────────────────────────────────
      """,
      """
█████████████████████████████████████████████████████████
█░░░░░░░░░░░░░░█░░░░░░░░░░░░░░█░░░░░░░░░░█░░░░░░░░░░░░░░█
█░░▄▀▄▀▄▀▄▀▄▀░░█░░▄▀▄▀▄▀▄▀▄▀░░█░░▄▀▄▀▄▀░░█░░▄▀▄▀▄▀▄▀▄▀░░█
█░░░░░░▄▀░░░░░░█░░▄▀░░░░░░░░░░█░░░░▄▀░░░░█░░▄▀░░░░░░░░░░█
█████░░▄▀░░█████░░▄▀░░███████████░░▄▀░░███░░▄▀░░█████████
█████░░▄▀░░█████░░▄▀░░███████████░░▄▀░░███░░▄▀░░░░░░░░░░█
█████░░▄▀░░█████░░▄▀░░██░░░░░░███░░▄▀░░███░░▄▀▄▀▄▀▄▀▄▀░░█
█████░░▄▀░░█████░░▄▀░░██░░▄▀░░███░░▄▀░░███░░▄▀░░░░░░░░░░█
█████░░▄▀░░█████░░▄▀░░██░░▄▀░░███░░▄▀░░███░░▄▀░░█████████
█████░░▄▀░░█████░░▄▀░░░░░░▄▀░░█░░░░▄▀░░░░█░░▄▀░░█████████
█████░░▄▀░░█████░░▄▀▄▀▄▀▄▀▄▀░░█░░▄▀▄▀▄▀░░█░░▄▀░░█████████
█████░░░░░░█████░░░░░░░░░░░░░░█░░░░░░░░░░█░░░░░░█████████
█████████████████████████████████████████████████████████
      """,
      """
🆃🅶🅸🅵
🅣🅖🅘🅕
      """,
      """
███████╗██████╗░██╗██████╗░░█████╗░██╗░░░██╗
██╔════╝██╔══██╗██║██╔══██╗██╔══██╗╚██╗░██╔╝
█████╗░░██████╔╝██║██║░░██║███████║░╚████╔╝░
██╔══╝░░██╔══██╗██║██║░░██║██╔══██║░░╚██╔╝░░
██║░░░░░██║░░██║██║██████╔╝██║░░██║░░░██║░░░
╚═╝░░░░░╚═╝░░╚═╝╚═╝╚═════╝░╚═╝░░╚═╝░░░╚═╝░░░
      """,
      "tgif",
   ) ).strip()
   await ctx.send( msg )

@bot.command(name='catread')
async def _catread(ctx: commands.Context):
   """Random log line with cat"""
   res = catread.get_catread()
   await ctx.send('```{}```'.format(res))

# TODO BK, acro
# TODO aaq/canjoisnthere - post images???? ;>

@bot.command(name='CYBER')
async def cyber(ctx: commands.Context, *, line:str):
   """Prints an annoying thing"""
   lines = thingbarf.format_lines(line, maxwidth=75)
   head = '\n'.join(line.upper().center(75) for line in lines)
   msg = '```' + head + \
   """
#_                                                                       d
##_                                                                     d#
NN#p                                                                  j0NN
40NNh_                                                              _gN#B0
4JF@NNp_                                                          _g0WNNL@
JLE5@WRNp_                                                      _g@NNNF3_L
_F`@q4WBN@Np_                                                _gNN@ZL#p"Fj_
"0^#-LJ_9"NNNMp__                                         _gN#@#"R_#g@q^9"
a0,3_j_j_9FN@N@0NMp__                                __ggNZNrNM"P_f_f_E,0a
 j  L 6 9""Q"#^q@NDNNNMpg____                ____gggNNW#W4p^p@jF"P"]"j  F 
rNrr4r*pr4r@grNr@q@Ng@q@N0@N#@NNMpmggggmqgNN@NN@#@4p*@M@p4qp@w@m@Mq@r#rq@r
  F Jp 9__b__M,Juw*w*^#^9#""EED*dP_@EZ@^E@*#EjP"5M"gM@p*Ww&,jL_J__f  F j  
-r#^^0""E" 6  q  q__hg-@4""*,_Z*q_"^pwr""p*C__@""0N-qdL_p" p  J" 3""5^^0r-
  t  J  __,Jb--N"\"",  *_s0M`""q_a@NW__JP^u_p"\""p4a,p" _F""V--wL,_F_ F  #  
_,Jp*^#""9   L  5_a*N"\""q__INr" "q_e^"*,p^""qME_ y"\""p6u,f  j'  f "N^--LL_
   L  ]   k,w@#"\""_  "_a*^E   ba-" ^qj-""^pe"  J^-u_f  _f "q@w,j   f  jL  
   #_,J@^""p  `_ _jp-""q  _Dw^" ^cj*""*,j^  "p#_  y""^wE_ _F   F"^qN,_j   
w*^0   4   9__sAF" `L  _Dr"  m__m""q__a^"m__*  "qA_  j" ""Au__f   J   0^--
   ]   J_,x-E   3_  jN^" `u _w^*_  _RR_  _J^w_ j"  "pL_  f   7^-L_F   #
   jLs*^6   `_  _&*"  q  _,NF   "wp"  "*g"   _NL_  p  "-d_   F   ]"*u_F
,x-"F   ]    Ax^" q    hp"  `u jM""u  a^ ^, j"  "*g_   p  ^mg_   DH       ```
 """
   await ctx.send(msg)


@bot.command()
async def minesweep(ctx: commands.Context, *, line:str='9'):
   """Generate a minesweeper board"""
   if line.strip().isdigit():
      inp = int(line.strip())
      size = max(3, min(9, inp))
   else:
      size = random.randint(5, 9)  # 9 is max b/c discord limits emojis in messages to 99 >:c

   def _neighbors(_y, _x):
      _candidates = [(_y+yd, _x+xd) for yd in (-1, 0, 1) for xd in (-1, 0, 1)]
      _candidates.remove((_y,_x))
      _copy = _candidates[:]
      for _ny, _nx in _copy:
         if not 0<=_ny<size or not 0<=_nx<size:
            _candidates.remove((_ny,_nx))
      return _candidates

   board = [[0] * size for _ in range(size)]
   bombs = random.randint(int(0.15 * size * size), int(0.4 * size * size))  # 15-40% of field
   bombflag = -1
   # place da bombs
   while bombs:
      ry, rx = random.randrange(size), random.randrange(size)
      if ry == rx == 0:
         # never place a bomb at top left
         continue
      if board[ry][rx] != bombflag:
         # place bomb
         board[ry][rx] = bombflag
         bombs -= 1
   # scan and increment neighbors of bombs
   for sy in range(size):
      for sx in range(size):
         cell = board[sy][sx]
         if cell == bombflag:
            for (ny, nx) in _neighbors(sy, sx):
               if board[ny][nx] != bombflag:
                  board[ny][nx] += 1
   import pprint
   pprint.pprint(board)
   # board complete, convert to text
   import itertools
   msg = random.choice(['mine', 'mines', 'minesweep', 'mines weep', 'mindsweap', 'mindsweee',
      ''.join(random.choice(list(itertools.permutations('mine')))) + 
      ''.join(random.choice(list(itertools.permutations('sweep'))))
   ])
   msg += '\n'
   conv = {bombflag: ':boom:', 0: ':zero:', 1: ':one:', 2: ':two:', 3: ':three:', 4: ':four:',
           5: ':five:', 6: ':six:', 7: ':seven:', 8: ':eight:'}
   for sy in range(size):
      for sx in range(size):
         msg += '||' + conv[board[sy][sx]] + '||'
      msg += '\n'
   await ctx.send(msg)


@bot.command('anagram')
async def anagramtime(ctx: commands.Context, *, line: str):
   """Generates some funey 'nag a ram's ;-D"""
   if len(line) > 200 or len(line) <3:
      await ctx.send("Be reasonable, {} 💔".format(thingbarf.get_dumdum()))
      return
   res = anagramz.get_anagram(line)
   random.shuffle(res)
   await ctx.send("`{}`".format(' '.join(res)))


@bot.command('randomidi')
async def randomidi(ctx: commands.Context):
   """Klungo will tell you about a random MIDI from vgmusic"""
   mididir = os.path.expanduser('~/Music/midis/music')
   # this only takes like 100ms, good enough
   if not os.path.exists('.midis.txt'):
      try:
         midis = subprocess.check_output(['find', mididir, '-name', '*.mid'])
      except subprocess.CalledProcessError as ex:
         midis = ex.output
      with open('.midis.txt', 'w') as f:
         f.write(midis.decode())

   with open('.midis.txt') as f:
      midis = f.readlines()

   fn = os.path.join(mididir, random.choice(midis).strip())
   midi = funmid.MidiFile(fn)
   info = midi.to_simplynotes()
   midistr = midi2vox.friendly_print(info, do_print=False)
   intro = random.choice((
      'Here is my favorite MIDI', 'This is my favorite MIDI in the world',
      'Here is my favorite MIDI', 'This is my favorite MIDI in the world',
      'There are no better MIDIs than this', 'This, in my estimation, is the best MIDI',
      'I want to marry this MIDI', 'This MIDI is my best friend', 'Check this shit out',
      'This MIDI is pretty good', 'I like this MIDI', 'Here is a good MIDI', 'Here is a fine MIDI',
      'This MIDI is pretty good', 'I like this MIDI', 'Here is a good MIDI', 'Here is a fine MIDI',
      'This MIDI is the GOAT (?)', 'This MIDI is the FOMO (??)', 'This MIDI is the GUH (???)',
      'Here is a MIDI that rocks', 'Here is a MIDI that slaps', 'Here is a MIDI that whips ass',
      'Here is a MIDI that rocks', 'Here is a MIDI that slaps', 'Here is a MIDI that whips ass',
      'Want a good MIDI? How about this', 'Heh heh... Got a good MIDI for ya, stranger',
      "Gyeh heh heh! Take this MIDI, but beware! I'm insane!!!! Gwaaa hah hah hah hah"
   ))
   msg = '{}: {}\n```{}```'.format(intro, os.path.basename(fn).replace('_', r'\_'), midistr)
   await ctx.send(msg)
   await ctx.send(file=discord.File(fn))


@bot.command('wordle')
async def wordle(ctx: commands.Context, *, line:str=''):
    """Klungo plays wordle against himself"""
    affirmations = (
        'i can play wordle.',
        'i CAN play wordle.',
        'i can play wordle...?',
        'i like wordle.',
        'i like to play wordle :)',
        "wordle :) it's the game for me :)",
        "let's wordle!",
        "it's time to wordle",
    )
    geniuswords = (
        "Brain Genius Mode Activated...",
        "Right Now I am a brain wizard",
        "Genius Mode: ENGAGED",
        "me smart >:D",
    )
    imstupid = (
        "Duhhh I'm stumped. I'm soooo stupid I don't know!!!!!!!",
        "I don't know! I don't know!!!",
        "Uhhhhhhhhhhhhhhhh?????????????????",
        "UHHHHHHHHHHHHHH",
        "I'm stupid I don't know any words :("
    )
    laments = (
        "Darn.",
        "Drat.",
        "Shucks.",
        "FUck!!!",
        "ugg.",
        "ugh.",
        "darn.",
        "shoot.",
    )
    fmtstr = '{affirmation}\n' + worble.autoplay()
    await ctx.send(fmtstr.format(
        affirmation=random.choice(affirmations),
        idiot=random.choice(imstupid),
        genius=random.choice(geniuswords),
        stumped=random.choice(imstupid),
        lament=random.choice(laments) + " The secret word was:"
    ))
    if 'stat' in line:
        await ctx.send(worble.print_stats())

@bot.command('klungordle')
async def klungordle(ctx: commands.Context, *, line:str=''):
    """Klungo plays wordle against a chatter :O"""
    player = ctx.author
    await ctx.send( worble.play(player.display_name, line) )

@bot.command('grunty')
async def grunty(ctx: commands.Context):
   """This is not done (or even started)"""
   # TODO
   await ctx.send("someday I will implement this?")


@bot.event
async def on_ready():
   print("Lorged orn.")

#
# General text reactions (non !commands)
#

@bot.listen('on_message')
async def twisted_talky(message: discord.Message):
   """Randomly chime in with >:D"""
   if message.author == bot.user:
      return
   if message.content.endswith('>:D'):
      if random.random() > 0.69:
         time.sleep(random.random())
         await message.channel.send('>:D')


g_wiggle_detector = re.compile('.*?'.join('wigglethatdumpstermachine'))


@bot.listen('on_message')
async def wiggle_detector(message: discord.Message):
   """wiggle that dumpster machine"""
   if message.author == bot.user:
      return

   if g_wiggle_detector.search(message.content.lower()) and len(message.content) < 200:
      await message.channel.send('wiggle that dumpster machine')


@bot.listen('on_message')
async def talky(message: discord.Message):
   """Respond to people talking to us with markov/gpt/somethin'"""
   if message.author == bot.user:
      return
   elif 'klungordle' in message.content:
      return

   if message.content.lower() == 'klungo':
      await message.channel.send( get_klungo_greet(message) )
   elif 'klungo' in message.content.lower():
      # markov bot time wahahwthtyy
      msg = ''
      tries = 3
      while (not msg) and (tries > 0):
         msg = get_markov_fun(message.content.replace('klungo', '').replace('Klungo', '').lstrip(' ,.:!-').rstrip(' ,'))
         tries -= 1
      if msg:
         if msg.startswith('ACTION '):
            msg = msg.replace('ACTION ', '/me ')  # TODO hey this doesn't work. whadda heck I gota do discord.py???
         await message.channel.send( msg )
      else:
         await message.channel.send( '(im shy today ok...) {msg}'.format( msg=get_klungo_greet(message) ) )


def get_klungo_greet(message: discord.Message):
   if random.random() < 0.33:
      greet = get_rand_line( os.path.join('txt', 'greetz.txt') )
   else:
      greet = random.choice(['Hey', 'Hi', 'Hello', 'Sup'] * 2 + ['Ahoy', 'Salutations', 'Hail and well met'])
   thing = thingbarf.thingsay('a thing please')
   them = message.author.name
   if random.random() > 0.69 or 'name' in message.content.lower():
      name = get_rand_line( os.path.join('txt', 'plot', 'stupidnames.txt'))
      if ',' in name:
         name = name[:name.find(',')]
      im = random.choice(["My name is", "My name's", "I'm", "I am"] * 2 + ["You may call me"])
      thing = f"{im} {name}"

   if random.random() < 0.33:
      greet = greet.lower().replace("'", '')
      them = them.lower()
      thing = thing.lower().replace("'", '')

   cmds = sorted(bot.all_commands.keys())
   cmds.remove('CYBER')  # shh
   cmds.remove('help')
   cmdstr = ' '.join('`!{}`'.format(cmd) for cmd in cmds)
   return f"{greet}, {them}. {thing}\n||Supported commands: " + cmdstr + "||"

def get_markov_fun(msg):
   sock = socket.socket()
   try:
      sock.connect(('localhost', 6667))
      print(sock.recv(4096))
      sock.send(b'PASS whatever\n')
      sock.send(b'NICK planktonbot\n')
      sock.send(b'USER foo 0 * :planko\n')
      time.sleep(0.1)
      r = sock.recv(4096)
      while b'End of MOTD command.' not in r:
         print('>',r)
         r = sock.recv(4096)
         time.sleep(0.1)
      print('>',r)
      #time.sleep(0.1)
      #sock.send(b'JOIN #duh\n')
      time.sleep(0.1)
      #print("join>", sock.recv(4096))
      print("Sending:", 'PRIVMSG Klungo {msg}'.format(msg=msg).encode('utf-8'))
      sock.send('PRIVMSG Klungo {msg}\n'.format(msg=msg).encode('utf-8'))
      sock.settimeout(2)
      resp = sock.recv(4096)
      print("HONKERS!!!!!!!!!")
      print(resp)
      sock.send(b'QUIT\n')
      if resp.find(b'PRIVMSG planktonbot :')>0:
         cleanresp = resp[resp.find(b'PRIVMSG planktonbot :')+len(b'PRIVMSG planktonbot :'):].decode('utf-8').strip()
         return ''.join( [c for c in cleanresp if c in string.printable] )
   except (socket.error, socket.timeout, ValueError, IndexError) as e:
      print(e)
      return ''
   finally:
      sock.close()

# secret admin stuff
import secretbot
@bot.listen('on_message')
async def secret(message: discord.Message):
   """?"""
   if message.author == bot.user:
      return
   elif not secretbot.would_handle(message):
      return
   else:
      await secretbot.handle(message)


# main
if __name__ == "__main__":
   with open(os.path.join('.never', 'tok.txt')) as tf:
      token = tf.read().strip()

   bot.run(token)
