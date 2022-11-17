from discord.ext import commands, tasks
import discord
from .utils import *


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Admin cog is loaded")

    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def set_guild_name(self, ctx, name):
        guild_id = ctx.guild.id
        guild_name = name
        pool = await get_db(self.bot)
        # check if guild already exists in db in configs table GUILD_NAME setting row
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT * FROM configs WHERE guild = %s AND setting = 'GUILD_NAME'",
                    (guild_id,),
                )
                guild_exists = await cur.fetchone()
                if guild_exists:
                    await cur.execute(
                        "UPDATE guild SET value = %s WHERE guild = %s AND setting = 'GUILD_NAME'",
                        (guild_name, guild_id),
                    )
                else:
                    await cur.execute(
                        "INSERT INTO guild (guild, setting, value) VALUES (%s, 'GUILD_NAME', %s)",
                        (guild_id, guild_name),
                    )
        await ctx.message.add_reaction("✅")

    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def set_home_role(self, ctx, role):
        guild_id = ctx.guild.id
        role_type = type(role)
        if role_type == discord.Role:
            role_id = role.id
        elif role_type == int:
            role_id = role
        else:
            await ctx.send("Pass role_id or @role")
            return
        # get role name by id
        role_name = ctx.guild.get_role(role_id).name
        pool = await get_db(self.bot)
        # check if guild already exists in db in configs table GUILD_HOME_ROLE setting row
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT * FROM configs WHERE guild = %s AND setting = 'GUILD_HOME_ROLE'",
                    (guild_id,),
                )
                guild_exists = await cur.fetchone()
                if guild_exists:
                    await cur.execute(
                        "UPDATE guild SET value = %s WHERE guild = %s AND setting = 'GUILD_HOME_ROLE'",
                        (role, guild_id),
                    )
                else:
                    await cur.execute(
                        "INSERT INTO guild (guild, setting, value) VALUES (%s, 'GUILD_HOME_ROLE', %s)",
                        (guild_id, role),
                    )
                    # also insert ALLOW_CLAN_DATA
                    await cur.execute(
                        "INSERT INTO guild (guild, setting, value) VALUES (%s, 'ALLOW_CLAN_DATA', %s)",
                        (guild_id, guild_id),
                    )

        await ctx.message.add_reaction("✅")
        await ctx.send(f"Home role set to {role_name}")

    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def show_configs(self, ctx):
        guild_id = ctx.guild.id
        pool = await get_db(self.bot)
        # check if guild already exists in db in configs table GUILD_HOME_ROLE setting row
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT * FROM configs WHERE guild = %s", (guild_id,))
                configs = await cur.fetchall()
        for config in configs:
            await ctx.send(f"{config[1]}: {config[2]}")

    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def set_event_channel(self, ctx, channel: discord.TextChannel = None):
        if not channel:
            await ctx.send("Usage: !set_event_channel #channel")
            return
        # write config to db
        pool = await get_db(self.bot)
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                # Check if value already exists in db for given ctx.guild.id and option
                await cur.execute(
                    "SELECT * FROM configs WHERE guild = %s AND setting = %s",
                    (ctx.guild.id, "EVENT_ANNOUNCE_CHANNEL"),
                )
                result = await cur.fetchone()
                if result:
                    # Update value
                    await cur.execute(
                        "UPDATE configs SET value = %s WHERE guild = %s AND setting = %s",
                        (channel.id, ctx.guild.id, "EVENT_ANNOUNCE_CHANNEL"),
                    )
                else:
                    # Insert value
                    await cur.execute(
                        "INSERT INTO configs (guild, setting, value) VALUES (%s, %s, %s)",
                        (ctx.guild.id, "EVENT_ANNOUNCE_CHANNEL", channel.id),
                    )

                await ctx.send(f"Event channel set to {channel.mention}")

    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def set_kion_channel(self, ctx, channel: discord.TextChannel = None):
        if not channel:
            await ctx.send("Usage: !set_kion_channel #channel")
            return
        # write config to db
        pool = await get_db(self.bot)
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                # Check if value already exists in db for given ctx.guild.id and option
                await cur.execute(
                    "SELECT * FROM configs WHERE guild = %s AND setting = %s",
                    (ctx.guild.id, "KION_CHANNEL"),
                )
                result = await cur.fetchone()
                if result:
                    # Update value
                    await cur.execute(
                        "UPDATE configs SET value = %s WHERE guild = %s AND setting = %s",
                        (channel.id, ctx.guild.id, "KION_CHANNEL"),
                    )
                else:
                    # Insert value
                    await cur.execute(
                        "INSERT INTO configs (guild, setting, value) VALUES (%s, %s, %s)",
                        (ctx.guild.id, "KION_CHANNEL", channel.id),
                    )

                await ctx.send(f"Kion channel set to {channel.mention}")


    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def set_timer_channel(self, ctx, channel: discord.VoiceChannel = None):
        if not channel:
            await ctx.send("Usage: !set_time_channel #channel")
            return
        # write config to db
        pool = await get_db(self.bot)
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                # Check if value already exists in db for given ctx.guild.id and option
                await cur.execute(
                    "SELECT * FROM configs WHERE guild = %s AND setting = %s",
                    (ctx.guild.id, "TIME_CHANNEL"),
                )
                result = await cur.fetchone()
                if result:
                    # Update value
                    await cur.execute(
                        "UPDATE configs SET value = %s WHERE guild = %s AND setting = %s",
                        (channel.id, ctx.guild.id, "TIME_CHANNEL"),
                    )
                else:
                    # Insert value
                    await cur.execute(
                        "INSERT INTO configs (guild, setting, value) VALUES (%s, %s, %s)",
                        (ctx.guild.id, "TIME_CHANNEL", channel.id),
                    )

                await ctx.send(f"Time channel set to {channel.mention}")

    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def allow_clan_data(self, ctx, server_id):

        # check that server_id is a valid server and bot is there
        try:
            server = self.bot.get_guild(int(server_id))
            if not server:
                await ctx.send("I'm not aware of that server")
                return
        except Exception as e:
            await ctx.send("Something is off. {e}")
            return

        # Get discord id from the author and insert into configs with ALLOW_CLAN_DATA

        pool = await get_db(self.bot)
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                # Check if value already exists in db for given ctx.guild.id and option
                await cur.execute(
                    "SELECT * FROM configs WHERE guild = %s AND setting = %s",
                    (ctx.guild.id, "ALLOW_CLAN_DATA"),
                )
                result = await cur.fetchone()
                if result:
                    # Update value
                    await cur.execute(
                        "UPDATE configs SET value = %s WHERE guild = %s AND setting = %s",
                        (server_id, ctx.guild.id, "ALLOW_CLAN_DATA"),
                    )
                else:
                    # Insert value
                    await cur.execute(
                        "INSERT INTO configs (guild, setting, value) VALUES (%s, %s, %s)",
                        (ctx.guild.id, "ALLOW_CLAN_DATA", server_id),
                    )

                await ctx.send(f"Clan data allowed for server {server_id}")

    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def disable_clan_data(self, ctx, server_id=None):
        if not server_id:
            # show current configs from ALLOW_CLAN_DATA
            pool = await get_db(self.bot)
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    # Check if value already exists in db for given ctx.guild.id and option
                    await cur.execute(
                        "SELECT * FROM configs WHERE guild = %s AND setting = %s",
                        (ctx.guild.id, "ALLOW_CLAN_DATA"),
                    )
                    result = await cur.fetchall()
                    for server in result:
                        # convert server[2] to guild name and show
                        guild = self.bot.get_guild(int(server[3]))
                        await ctx.send(
                            f"Clan data allowed for server {guild.name} with ID {server[3]}. To disable, use !disable_clan_data {server[3]}"
                        )
        else:
            # disable clan data for server_id
            pool = await get_db(self.bot)
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    # Check if value already exists in db for given ctx.guild.id and option
                    await cur.execute(
                        "SELECT * FROM configs WHERE guild = %s AND setting = %s",
                        (ctx.guild.id, "ALLOW_CLAN_DATA"),
                    )
                    result = await cur.fetchall()
                    for server in result:
                        if server[2] == server_id:
                            await cur.execute(
                                "DELETE FROM configs WHERE guild = %s AND setting = %s AND value = %s",
                                (ctx.guild.id, "ALLOW_CLAN_DATA", server_id),
                            )
                            await ctx.send(f"Clan data disabled for server {server_id}")
                            return
                    await ctx.send(f"Clan data not enabled for server {server_id}")


def setup(bot):
    bot.add_cog(Admin(bot))
