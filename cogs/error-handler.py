import discord
from discord.ext import commands


class ErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send(embed=discord.Embed(
                color=discord.Color.red(),
                description="❌ This command is only supported on servers."
            ))
        elif isinstance(error, commands.CommandNotFound):
            return
        else:
            await ctx.send(embed=discord.Embed(
                title="An error occured during the command execution:",
                color=discord.Color.red(),
                description=f"```{error}```"
            ))

def setup(bot):
    bot.add_cog(ErrorHandler(bot))