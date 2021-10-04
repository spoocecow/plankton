"""
funny bot for plankton discord
spoocecow 2021
"""
import functools
import logging
import os
import random
import time
from typing import List

import discord
from discord.ext import commands

import thingbarf


logging.basicConfig(level=logging.INFO)


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


@bot.command()
async def woooo(ctx: commands.Context, *, line: str):
   msg = '```' + line.upper().center(75) + \
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

# TODO catread, BK, wiggle that dumpster machine. acro
# TODO aaq/canjoisnthere - post images???? ;>

with open(os.path.join('.never', 'tok.txt')) as tf:
 token = tf.read().strip()

bot.run(token)
