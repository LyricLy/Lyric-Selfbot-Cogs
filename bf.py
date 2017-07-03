#Importing libraries
import discord
from discord.ext import commands
from cogs.utils.checks import *
from sys import argv

class BrainF:
    """
    Esoteric language parsing. 
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def bf(self, ctx, program, stdin=""):
        # make sure brackets match
        count = 0
        for i in program:
            if i == "[":
                count += 1
            elif i == "]":
                count -= 1
            if count < 0:
                raise SyntaxError("unmatched brackets in program")
        if count != 0: 
            raise SyntaxError("unmatched brackets in program")
            
        # initialize variables 
        cells = [0]
        pointer = 0
        idx = 0
        loops = 0
        result = ""
        broke = False
        
        # begin main loop
        while idx < len(program):
            char = program[idx]
            # print(cells)
            # print(pointer)
            # print(cells[pointer])
            # print(char)
            if char == "+":
                cells[pointer] += 1
            elif char == "-":
                cells[pointer] -= 1
            elif char == "<":
                if pointer > 0:
                    pointer -= 1
                else:
                    cells.insert(0, 0)  # since this changes the indexing we don't need to decrement the pointer
            elif char == ">":
                try:
                    cells[pointer+1]
                except IndexError:
                    cells.append(0)
                pointer += 1
            elif char == "[":
                if cells[pointer] == 0:
                    extra = 0
                    for pos, char in enumerate(program[idx+1:]):
                        if char == "[":
                            extra += 1
                        elif char == "]":
                            if extra:
                                extra -= 1
                            else:
                                idx = pos
                                break
            elif char == "]":
                if cells[pointer] == 0:
                    pass
                else:
                    extra = 0
                    for pos, char in reversed(list(enumerate(program[:idx]))):
                        if char == "]":
                            extra += 1
                        elif char == "[":
                            if extra:
                                extra -= 1
                            else:
                                idx = pos
                                break
            elif char == ",":
                try:
                    cells[pointer] = ord(stdin[0])
                except IndexError:
                    cells[pointer] = 0
                stdin = stdin[1:]
            elif char == ".":
                result += chr(cells[pointer])
            idx += 1
            loops += 1
            if loops > 1000:
                await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + "This program appears to have gotten stuck in a loop. Terminating execution...")
                broke = True
                break
        if not broke: await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + result)

def setup(bot):
    bot.add_cog(BrainF(bot))
