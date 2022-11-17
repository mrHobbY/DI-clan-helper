import discord
from discord.ext import commands
from discord.ext.commands import Cog

from .utils import *


class Roe(Cog):
    def __init__(self, bot):
        self.bot = bot

    # 1. !roe add @Fooz 8 #adds member by tag to group 8. Officer only
    # 1.1 !roe del @Fooz #remove from group
    # 1.2 !roe update @Fooz 1 #change group
    # 2. !whogroup 8 # prints member list of the group 8
    # 3. !roegroups # print all groups
    # 4. !mygroup will tell a person which group they are in if any

    @commands.Cog.listener()
    async def on_ready(self):
        print("ROE cog is loaded")

    @commands.command(pass_context=True)
    @commands.has_permissions(manage_roles=True)
    async def roe(self, ctx, action, member: discord.Member, group: int = 0):
        pool = await get_db(self.bot)
        if group > 10 or group < 0:
            await ctx.send("Groups can be 0-10")
            return
        if not member:
            await ctx.send("Please mention a member. Example: !roe add @Fooz 8")
            return
        if action == "add":
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        "UPDATE DISCORD SET roe_group = %s WHERE discord_id = %s",
                        (group, member.id),
                    )
                    await ctx.message.add_reaction("✅")
        elif action == "del" or action == "delete":
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        "UPDATE DISCORD SET roe_group = 0 WHERE discord_id = %s",
                        (member.id),
                    )
                    await ctx.message.add_reaction("✅")
        elif action == "update":
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        "UPDATE DISCORD SET roe_group = %s WHERE discord_id = %s",
                        (group, member.id),
                    )
                    await ctx.message.add_reaction("✅")
        else:
            await ctx.send("!roe add|update|delete @member group")

    @commands.command(pass_context=True)
    async def whogroup(self, ctx, group: int):
        pool = await get_db(self.bot)
        if group > 10 or group < 0:
            await ctx.send("Groups can be 0-10")
            return
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT * FROM DISCORD WHERE roe_group = %s", (group))
                members = await cur.fetchall()
                message = "```"
                if members:
                    message += f"Group {group}\n"
                    for member in members:
                        message += f"{member[1]:<16} {member[2]:<11} {member[3]:<4}/{member[7]:<4} {member[8]:<5}\n"
                    message += "```"
                    await ctx.send(message)
                else:
                    await ctx.send("No members in that group")

    @commands.command(pass_context=True)
    async def mygroup(self, ctx):

        pool = await get_db(self.bot)
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT * FROM DISCORD WHERE discord_id = %s",
                    (ctx.message.author.id),
                )
                member = await cur.fetchone()
                if member and member[10] != 0:
                    await ctx.send(f"You are in group {member[10]}")
                else:
                    await ctx.send("You are not in any group")

    @commands.command(pass_context=True)
    async def roegroups(self, ctx):

        pool = await get_db(self.bot)
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT * FROM DISCORD where roe_group != 0 ORDER BY roe_group"
                )
                members = await cur.fetchall()
                groups = {}
                # make a dict with keys of group (member[10]) and values of list of tuples (member[1], member[2], member[3], member[4], member[8],member[9])
                for member in members:
                    if member[10] not in groups:
                        groups[member[10]] = []
                    groups[member[10]].append(
                        (member[1], member[2], member[3], member[7], member[8])
                    )

                message = ""
                for group in groups:
                    message += f"\nGroup {group} {len(groups[group])}/8 \n"
                    for member in groups[group]:
                        # 0 name, 1 class ,2 cr, 3 res , 4 clan
                        message += f"{member[0]:<16} {member[1]:<11} {member[2]:<4}/{member[3]:<4} {member[4]:<5}\n"
                # split in chunk starting with "Group 1" and ending with "Group 5"
                mes = message.partition("Group 6")

                await ctx.send(f"```\n{mes[0]}\n```")
                await ctx.send(f"```\n{mes[1]}{mes[2]}\n```")


def setup(bot):
    bot.add_cog(Roe(bot))
