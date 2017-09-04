import discord
import time
import asyncio
from discord.ext import commands
'''Module for custom commands.'''

class LyricCommands:

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
                if window_size > 14: 
                    window_size = 14
        else:
            text = msg
            window_size = int(len(text)*0.5)
            if window_size > 14: 
                window_size = 14
        await ctx.message.edit(content=text[0:window_size+1])
        letter = 0
        # all commented out code here is for debugging
        # times = []
        # start = time.time()
        delay = (len(text)-window_size) * 0.03 # depending on the string size we can get away with more speed with less freezes
        if delay > 0.5: 
            delay = 0.5  # although eventually it's just wasteful
        for _ in text:
            # iteration_start = time.time()
            try:
                text[letter+window_size+1]
            except IndexError:
                break
            letter += 1
            await asyncio.sleep(delay)
            await ctx.message.edit(content=text[letter:letter+window_size+1])
            # iteration_end = time.time()
            # times.append(iteration_end - iteration_start)
        # end = time.time()
        # seconds = end - start
        # speed = len(text) / seconds
        # stability = max(times)
        await ctx.message.edit(content="{} {}".format(self.bot.bot_prefix, text))
        
    @commands.command(pass_context=True)
    async def kekify(self, ctx, *, text):
        result = ""
        for char in text:
            if char == "k":
                result += "kek"
            elif char == "K":
                result += "KEK"
            else:
                result += char
        await ctx.message.edit(content=result)
        
    @commands.command(pass_context=True)    
    async def whereami(self, ctx):
        await ctx.message.delete()
        await ctx.send(self.bot.bot_prefix + "You seem to be in {}.".format(ctx.message.channel.mention))    
                       
def setup(bot):
    bot.add_cog(LyricCommands(bot))
