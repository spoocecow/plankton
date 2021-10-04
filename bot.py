"""
funny bot for plankton discord
spoocecow 2021
"""
import functools
import logging
import os
import time

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


with open(os.path.join('.never', 'tok.txt')) as tf:
   token = tf.read().strip()

bot.run(token)
