import os
import json
import discord
import requests
from datetime import datetime
from discord.ext import commands

'''Save/load entire servers! Crazy, right?'''


class ServerSave:

    def __init__(self, bot):
        self.bot = bot
		
    @commands.command(pass_context=True)
    async def serversave(self, ctx, *, server=""):
        """Save an entire server! WHAT?!
        Saves the details of a server:
        - name
        - roles
        - emoji
        - region
        - afk timeout
        - afk channel
        - icon
        - 2FA level
        - verification level
        - channels
        
        >serversave [server] - Save the specified server (defaults to the current server) to a file in the server_save folder.
        
        Saved servers can be loaded with the >serverload command (>help serverload for more information)
        """
        if server:
            ctx.guild = self.bot.get_guild(int(server))
        if not ctx.guild:
            return await ctx.send(self.bot.bot_prefix + "That server couldn't be found.")

        await ctx.send(self.bot.bot_prefix + "Saving server `{}`...".format(ctx.guild.name))
        
        if not os.path.exists("server_save"):
            os.makedirs("server_save")
        
        date = datetime.now().strftime("%Y-%m-%d")
        filename = "server_save/{}_{}_{}.json".format(ctx.guild.name, ctx.guild.id, date)
        
        saved_guild = {
            "name": ctx.guild.name,
            "region": str(ctx.guild.region),
            "afk_timeout": ctx.guild.afk_timeout,
            "afk_channel": ctx.guild.afk_channel.name if ctx.guild.afk_channel else None,
            "icon": ctx.guild.icon_url,
            "mfa_level": ctx.guild.mfa_level,
            "verification_level": ["none", "low", "medium", "high", "extreme"].index(str(ctx.guild.verification_level)),
            "roles": [],
            "text_channels": [],
            "voice_channels": [],
            "emojis": []
        }
        
        for role in ctx.guild.roles:
            role_dict = {
                "name": role.name,
                "permissions": list(role.permissions),
                "colour": role.colour.to_rgb(),
                "hoist": role.hoist,
                "position": role.position,
                "mentionable": role.mentionable
            }
        
            saved_guild["roles"].append(role_dict)
                
        for channel in ctx.guild.text_channels:
            channel_dict = {
                "name": channel.name,
                "topic": channel.topic,
                "position": channel.position,
                "nsfw": channel.is_nsfw(),
                "overwrites": []
            }
            
            for overwrite in channel.overwrites:
                overwrite_dict = {
                    "name": overwrite[0].name,
                    "permissions": list(overwrite[1]),
                    "type": "member" if type(overwrite[0]) == discord.Member else "role"
                }
                
                channel_dict["overwrites"].append(overwrite_dict)
            
            saved_guild["text_channels"].append(channel_dict)
            
        for channel in ctx.guild.voice_channels:
            channel_dict = {
                "name": channel.name,
                "position": channel.position,
                "user_limit": channel.user_limit,
                "bitrate": channel.bitrate,
                "overwrites": []
            }
            
            for overwrite in channel.overwrites:
                overwrite_dict = {
                    "name": overwrite[0].name,
                    "permissions": list(overwrite[1]),
                    "type": "member" if type(overwrite[0]) == discord.Member else "role"
                }
                
                channel_dict["overwrites"].append(overwrite_dict)
            
            saved_guild["voice_channels"].append(channel_dict)
            
        for emoji in ctx.guild.emojis:
            emoji_dict = {
                "name": emoji.name,
                "url": emoji.url
            }
            
            saved_guild["emojis"].append(emoji_dict)
                
        
        with open(filename, "w+") as f:
            json.dump(saved_guild, f)
            
        await ctx.send(self.bot.bot_prefix + "Successfully saved `{}` to `{}`!".format(ctx.guild.name, filename))
        
    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def serverload(self, ctx, server=":"):  # filenames cannot contain : so I'm using this as a workaround to make it only use the current server ID if no server is given
        """Load an entire server?!?!?!??!
        Loads in the saved data from a previously saved server.
        Usage:
        >serverload - Attempt to find a save of the current server and load it.
        >serverload <filename> - Find a saved server by filename (if a whole filename is not given, the latest save from all of the filenames that contain the given filename is used)
        """
        if not os.path.exists("server_save") or not os.listdir("server_save"):
            return await ctx.send(self.bot.bot_prefix + "You have no servers saved!")
        
        saves = os.listdir("server_save")
        guild_saves = [x for x in saves if server in x or str(ctx.guild.id) in x]
        
        if not guild_saves:
            return await ctx.send(self.bot.bot_prefix + "That server couldn't be found in your saves.")
            
        parsed_guild_saves = [datetime.strptime(x.split("_")[2].split(".")[0], "%Y-%m-%d") for x in guild_saves]
        
        server_save = guild_saves[parsed_guild_saves.index(max(parsed_guild_saves))]
        
        await ctx.send(self.bot.bot_prefix + "Loading server... (this may take a few minutes, check console for progress)")
        
        print("Beginning server load process...")
        
        with open("server_save/" + server_save, "r") as f:
            g = json.load(f)
            
        print("Loading roles...")
         
        for role in ctx.guild.roles[:]:
            if role.name not in [x["name"] for x in g["roles"]]:
                await role.delete(reason="Loading saved server")
        for role in g["roles"]:
            permissions = discord.Permissions()
            permissions.update(**dict(role["permissions"]))
            if role["name"] not in [x.name for x in ctx.guild.roles]:
                await ctx.guild.create_role(name=role["name"], colour=discord.Colour.from_rgb(*role["colour"]), hoist=role["hoist"], mentionable=role["mentionable"], permissions=permissions, reason="Loading saved server")
            else:
                await [x for x in ctx.guild.roles if x.name == role["name"]][0].edit(name=role["name"], colour=discord.Colour.from_rgb(*role["colour"]), hoist=role["hoist"], mentionable=role["mentionable"], permissions=permissions, reason="Loading saved server")
                
        print("Loading text channels...")
           
        for channel in ctx.guild.text_channels:
            if channel.name not in [x["name"] for x in g["text_channels"]]:
                await channel.delete(reason="Loading saved server")
        for channel in g["text_channels"]:
            overwrites = []
            for overwrite in channel["overwrites"]:
                if overwrite["type"] == "role":
                    if overwrite["name"] not in [x.name for x in ctx.guild.roles]:
                        pass
                    else:
                        role = [x for x in ctx.guild.roles if x.name == overwrite["name"]][0]
                        permissions = discord.PermissionOverwrite()
                        permissions.update(**dict(overwrite["permissions"]))
                        overwrites.append((role, permissions))
                else:
                    if overwrite["name"] not in [x.name for x in ctx.guild.members]:
                        pass
                    else:
                        member = [x for x in ctx.guild.members if x.name == overwrite["name"]][0]
                        permissions = discord.PermissionOverwrite()
                        permissions.update(**dict(overwrite["permissions"]))
                        overwrites.append((member, permissions))
            if channel["name"] in [x.name for x in ctx.guild.text_channels]:
                channel_obj = [x for x in ctx.guild.text_channels if x.name == channel["name"]][0]
                await channel_obj.edit(name=channel["name"], topic=channel["topic"], reason="Loading saved server")
                overwrites_dict = dict(overwrites)
                for overwrite in overwrites_dict:
                    await channel_obj.set_permissions(overwrite, overwrite=overwrites_dict[overwrite], reason="Loading saved server")
            else:
                new_chan = await ctx.guild.create_text_channel(channel["name"], overwrites=dict(overwrites), reason="Loading saved server")
                await new_chan.edit(topic=channel["topic"], nsfw=channel["nsfw"], reason="Loading saved server")
                
        print("Loading voice channels...")   
          
        for channel in ctx.guild.voice_channels:
            if channel.name not in [x["name"] for x in g["voice_channels"]]:
                await channel.delete(reason="Loading saved server")
        for channel in g["voice_channels"]:
            if channel["name"] not in [x.name for x in ctx.guild.voice_channels]:
                overwrites = []
                for overwrite in channel["overwrites"]:
                    if overwrite["type"] == "role":
                        if overwrite["name"] not in [x.name for x in ctx.guild.roles]:
                            pass
                        else:
                            role = [x for x in ctx.guild.roles if x.name == overwrite["name"]][0]
                            permissions = discord.PermissionOverwrite()
                            permissions.update(**dict(overwrite["permissions"]))
                            overwrites.append((role, permissions))
                    else:
                        if overwrite["name"] not in [x.name for x in ctx.guild.members]:
                            pass
                        else:
                            members = [x for x in ctx.guild.members if x.name == overwrite["name"]][0]
                            permissions = discord.PermissionOverwrite()
                            permissions.update(**dict(overwrite["permissions"]))
                            overwrites.append((member, permissions))
                if channel["name"] in [x.name for x in ctx.guild.voice_channels]:
                    channel_obj = [x for x in ctx.guild.voice_channels if x.name == channel["name"]][0]
                    await channel_obj.edit(name=channel["name"], topic=channel["topic"], reason="Loading saved server")
                    overwrites_dict = dict(overwrites)
                    for overwrite in overwrites_dict:
                        await channel_obj.set_permissions(overwrite, overwrite=overwrites_dict[overwrite], reason="Loading saved server")
                else:
                    new_chan = await ctx.guild.create_voice_channel(channel["name"], overwrites=dict(overwrites), reason="Loading saved server")
                    await new_chan.edit(bitrate=channel["bitrate"], user_limit=channel["user_limit"], reason="Loading saved server")
                
        print("Loading emotes...")       
              
        for emoji in ctx.guild.emojis:
            if emoji.name not in [x["name"] for x in g["emojis"]]:
                await emoji.delete(reason="Loading saved server")
        for emoji in g["emojis"]:
            if emoji["name"] in [x.name for x in ctx.guild.emojis]:
                await [x for x in ctx.guild.emojis if x.name == emoji["name"]][0].delete(reason="Loading saved server")
            await ctx.guild.create_custom_emoji(name=emoji["name"], image=requests.get(emoji["url"]).content, reason="Loaded saved server")
                
        print("Positioning channels and roles...")
                
        # set up channel and role positions
        for channel in g["text_channels"]:
            await [x for x in ctx.guild.text_channels if x.name == channel["name"]][0].edit(position=channel["position"] if channel["position"] < len(ctx.guild.text_channels) else len(ctx.guild.text_channels) - 1)
            
        for channel in g["voice_channels"]:
            await [x for x in ctx.guild.voice_channels if x.name == channel["name"]][0].edit(position=channel["position"] if channel["position"] < len(ctx.guild.voice_channels) else len(ctx.guild.voice_channels) - 1)
            
        for role in g["roles"]:
            if role["name"] != "@everyone":
                await [x for x in ctx.guild.roles if x.name == role["name"]][0].edit(position=role["position"] if role["position"] < len(ctx.guild.roles) else len(ctx.guild.roles) - 1)
            
        print("Editing server settings...")
            
        await ctx.guild.edit(name=g["name"], icon=requests.get(g["icon"].rsplit(".", 1)[0] + ".png").content if g["icon"] else None, region=discord.VoiceRegion(g["region"]), afk_channel=[x for x in ctx.guild.voice_channels if x.name == g["afk_channel"]][0] if g["afk_channel"] else None, afk_timeout=g["afk_timeout"], verification_level=discord.VerificationLevel(g["verification_level"]), reason="Loading saved server")
        
        print("Finished loading server backup!")

def setup(bot):
    bot.add_cog(ServerSave(bot))
