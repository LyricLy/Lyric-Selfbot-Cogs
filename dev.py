import discord
from discord.ext import commands

"""You seem to be in (insert channel name) meme from Nintendo Homebrew."""

class DevMeme:
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(pass_context=True)    
    async def channel(self, ctx):
        await self.bot.delete_message(ctx.message)
        embed = discord.Embed(description="You seem to be in <#{}>.".format(ctx.message.channel.id))
        await self.bot.say("", embed=embed)
        
def setup(bot):
    bot.add_cog(DevMeme(bot))