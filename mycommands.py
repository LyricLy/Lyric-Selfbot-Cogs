import discord
import time
import asyncio
import requests
import re
import json
import string
import urllib
from appuselfbot import bot_prefix
from discord.ext import commands
'''Module for custom commands.'''

codes = requests.get("http://lyricly.tk/langs.json").text
lang_codes = json.loads(codes)

class MyCommands:

    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(pass_context=True)
    async def scroll(self, ctx, *, msg):
        """Scroll through given text.
        Usage:
        scroll (message) - Scroll through text.
        scroll (message) | (window size) - Scroll through text with a customized window size.
        """
        if " | " in msg:
            text, window_size = msg.split(" | ", 1)
            try:
                window_size = int(window_size)
            except ValueError:
                window_size = int(len(text)*0.5)
                if window_size > 14: window_size = 14
        else:
            text = msg
            window_size = int(len(text)*0.5)
            if window_size > 14: window_size = 14
        await self.bot.edit_message(ctx.message, ":robot: " + text[0:window_size+1])
        letter = 0
        # all commented out code here is for debugging
        # times = []
        # start = time.time()
        delay = (len(text)-window_size) * 0.03 #depending on the string size we can get away with more speed with less freezes
        if delay > 0.5: delay = 0.5 #although eventually it's just wasteful
        for _ in text:
            # iteration_start = time.time()
            try:
                text[letter+window_size+1]
            except IndexError:
                break
            letter += 1
            await asyncio.sleep(delay)
            await self.bot.edit_message(ctx.message, ":robot: " + text[letter:letter+window_size+1])
            # iteration_end = time.time()
            # times.append(iteration_end - iteration_start)
        # end = time.time()
        # seconds = end - start
        # speed = len(text) / seconds
        # stability = max(times)
        await self.bot.edit_message(ctx.message, ":robot: {}".format(text))
        
    @commands.command(pass_context=True)
    async def kekify(self, ctx, *, text):
        result = ""
        for char in text:
            if char == "k":
                result += "kek"
            else:
                result += char
        await self.bot.edit_message(ctx.message, result)
                       
def setup(bot):
    bot.add_cog(MyCommands(bot))
