"""
funny bot for plankton discord
spoocecow 2021
"""
import datetime
import functools
import logging
import os
import random
import re
import time
from typing import List

import discord
from discord.ext import commands

import catread
import thingbarf


logging.basicConfig(level=logging.DEBUG)


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


bot = commands.Bot(command_prefix='!')

@bot.command(name='gimme')
async def _thingbarf(ctx: commands.Context, *, line: str):
   msg = thingbarf.thingsay(line)
   await ctx.send(msg)


@clock_time_cache(max_age_s=60)
def get_lines(fn: str) -> List[str]:
   with open(fn) as f:
      return [l.strip() for l in f.readlines() if l.strip()]


def get_rand_lines(fn, n=1):
   lines = get_lines(fn)
   return [l.strip() for l in random.sample(lines, n)]


def get_rand_line(fn):
   return get_rand_lines(fn, 1)[0]


@bot.command()
async def english(ctx: commands.Context):
   fn = os.path.join('txt', '18thCdialectdict.txt')
   msg = get_rand_line(fn)
   await ctx.send( msg )


@bot.command()
async def plot(ctx: commands.Context):
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
   while '$read' in s:
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
   await ctx.send(
      r"""` _        /|__/\
//_______/ .  . \
\  F    N    i  /
\   _U____    |
|  ||     |  ||
|__\\     |__\\`"""
   )


@bot.command()
async def tgif(ctx: commands.Context):
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
         srystr,
         srystr,
         srystr,
         srystr,
         srystr,
      )
      opt = random.choice(confused_opts)
      await ctx.send(opt)
      return

   msg = random.choice( (
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
      "tgif"
   ) ).strip()
   await ctx.send( msg )

@bot.command(name='catread')
async def _catread(ctx: commands.Context):
   res = catread.get_catread()
   await ctx.send('```{}```'.format(res))

# TODO BK, wiggle that dumpster machine. acro
# TODO aaq/canjoisnthere - post images???? ;>

@bot.command(name='CYBER')
async def cyber(ctx: commands.Context, *, line: str):
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
  t  J  __,Jb--N\""",  *_s0M`""q_a@NW__JP^u_p"\""p4a,p" _F""V--wL,_F_ F  #  
_,Jp*^#""9   L  5_a*N"\""q__INr" "q_e^"*,p^""qME_ y"\""p6u,f  j'  f "N^--LL_
   L  ]   k,w@#"\""_  "_a*^E   ba-" ^qj-""^pe"  J^-u_f  _f "q@w,j   f  jL  
   #_,J@^""p  `_ _jp-""q  _Dw^" ^cj*""*,j^  "p#_  y""^wE_ _F   F"^qN,_j   
w*^0   4   9__sAF" `L  _Dr"  m__m""q__a^"m__*  "qA_  j" ""Au__f   J   0^--
   ]   J_,x-E   3_  jN^" `u _w^*_  _RR_  _J^w_ j"  "pL_  f   7^-L_F   #
   jLs*^6   `_  _&*"  q  _,NF   "wp"  "*g"   _NL_  p  "-d_   F   ]"*u_F
,x-"F   ]    Ax^" q    hp"  `u jM""u  a^ ^, j"  "*g_   p  ^mg_   DH       ```
 """
   await ctx.send(msg)


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


g_wiggle_detector = re.compile('.*'.join('wigglethatdumpstermachine'))


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

   if message.content.lower().startswith('klungo'):
      # TODO
      await message.channel.send('hey {}'.format(message.author.name.lower()))


# main
with open(os.path.join('.never', 'tok.txt')) as tf:
   token = tf.read().strip()

bot.run(token)
