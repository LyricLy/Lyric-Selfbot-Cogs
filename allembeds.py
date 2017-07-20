import discord
from discord.ext import commands

'''Turn every message into an embed.'''


class AllEmbeds:

    def __init__(self, bot):
        self.bot = bot
        self.enabled = False
        
    @commands.command(pass_context=True)
    async def toggleembeds(self, ctx):
        self.enabled = not self.enabled
        await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + "Successfully toggled turning all messages to embeds!")
        
    async def on_message(self, message):
        if message.author == self.bot.user:
            if not message.embeds and self.enabled:
                await self.bot.edit_message(message, " ", embed=discord.Embed(description=message.content))

def setup(bot):
    bot.add_cog(AllEmbeds(bot))
