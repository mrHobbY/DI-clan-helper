from discord.ext import commands, tasks
import discord
import datetime
import asyncio
from .utils import *


class CR(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("CR cog is loaded")
        self.database_update.start()

    @commands.command(pass_context=True)
    async def cr(self, ctx, *cr):
        if not cr:
            await ctx.send("Enter CR number: !cr 1000")
            return
        try:
            cr = int(cr[0])
            pass
        except ValueError:
            await ctx.send("Need a number")
            return
        if cr > 0 and cr < 19999:
            # fetch all from database

            name = ctx.author.nick if ctx.author.nick else ctx.author.name
            pool = await get_db(self.bot)
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("select distinct clan_name from DISCORD")
                    result = await cur.fetchall()
            # convert results to bracket wrapped list
            clan_list = []
            for clan in result:
                if clan[0] is not None:
                    clan_list.append(f"[{clan[0]}] ")

            for word in clan_list:
                name = name.replace(word, "")

            pool = await get_db(self.bot)
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        "SELECT * FROM DISCORD WHERE discord_id = %s", (ctx.author.id,)
                    )
                    result = await cur.fetchone()
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    if result:
                        await cur.execute(
                            "UPDATE DISCORD SET cr = %s, last_updated = %s WHERE discord_id = %s",
                            (cr, current_time, ctx.author.id),
                        )
                    else:
                        await cur.execute(
                            "INSERT INTO DISCORD (discord_id, cr,last_updated,name, IS_CLAN_MEMBER) VALUES (%s, %s, %s,%s, %s)",
                            (ctx.author.id, cr, current_time, name, 1),
                        )
                    # react to the message with a checkmark
                    await ctx.message.add_reaction("✅")

        else:
            await ctx.send("Mhm...")
            return

    @commands.command(pass_context=True)
    async def res(self, ctx, *res):
        if not res:
            await ctx.send("Enter resonance number: !res 1000")
            return
        try:
            res = int(res[0])
            pass
        except ValueError:
            await ctx.send("Need a number")
            return
        if res > 0 and res < 9999:
            # fetch all from database
            name = ctx.author.nick if ctx.author.nick else ctx.author.name
            pool = await get_db(self.bot)
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("select distinct clan_name from DISCORD")
                    result = await cur.fetchall()
            # convert results to bracket wrapped list
            clan_list = []
            for clan in result:
                if clan[0] is not None:
                    clan_list.append(f"[{clan[0]}] ")

            for word in clan_list:
                name = name.replace(word, "")
            pool = await get_db(self.bot)
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        "SELECT * FROM DISCORD WHERE discord_id = %s", (ctx.author.id,)
                    )
                    result = await cur.fetchone()
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    if result:
                        await cur.execute(
                            "UPDATE DISCORD SET res = %s, last_updated = %s WHERE discord_id = %s",
                            (res, current_time, ctx.author.id),
                        )
                    else:
                        await cur.execute(
                            "INSERT INTO DISCORD (discord_id, res,last_updated,name, IS_CLAN_MEMBER) VALUES (%s, %s, %s,%s, %s)",
                            (ctx.author.id, res, current_time, name, 1),
                        )
                    # react to the message with a checkmark
                    await ctx.message.add_reaction("✅")

        else:
            await ctx.send("Mhm...")
            return

    @commands.command(pass_context=True, name="cls", aliases=["class"])
    async def cls(self, ctx, *cls):
        if not cls:
            await ctx.send("Enter class: !class hunter")
            return
        else:
            cls = cls[0]
        KNOWN_CLASSES = [
            "Necromancer",
            "Wizard",
            "Hunter",
            "Barbarian",
            "Monk",
            "Crusader",
        ]

        if cls.title() not in KNOWN_CLASSES:
            await ctx.send("Valid entries are: " + ", ".join(KNOWN_CLASSES))
            return
        # fetch all from database
        name = ctx.author.nick if ctx.author.nick else ctx.author.name
        pool = await get_db(self.bot)
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("select distinct clan_name from DISCORD")
                result = await cur.fetchall()
        # convert results to bracket wrapped list
        clan_list = []
        for clan in result:
            if clan[0] is not None:
                clan_list.append(f"[{clan[0]}] ")

        for word in clan_list:
            name = name.replace(word, "")

        pool = await get_db(self.bot)
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT * FROM DISCORD WHERE discord_id = %s", (ctx.author.id,)
                )
                result = await cur.fetchone()
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if result:
                    await cur.execute(
                        "UPDATE DISCORD SET class = %s, last_updated = %s WHERE discord_id = %s",
                        (cls.title(), current_time, ctx.author.id),
                    )
                else:
                    await cur.execute(
                        "INSERT INTO cr (discord_id, class,last_updated, name,IS_CLAN_MEMBER) VALUES (%s, %s,%s, %s, %s)",
                        (ctx.author.id, cls.title(), current_time, name, 1),
                    )
                # react to the message with a checkmark
                await ctx.message.add_reaction("✅")

    @commands.command(pass_context=True)
    async def name(self, ctx, *name):
        if not name:
            await ctx.send("Enter in-game name: !name hobz")
            return
        else:
            name = name[0]
        # fetch all from database
        pool = await get_db(self.bot)
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT * FROM DISCORD WHERE discord_id = %s", (ctx.author.id,)
                )
                result = await cur.fetchone()
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if result:
                    await cur.execute(
                        "UPDATE DISCORD SET name = %s, last_updated = %s WHERE discord_id = %s",
                        (name, current_time, ctx.author.id),
                    )
                else:
                    await cur.execute(
                        "INSERT INTO DISCORD (discord_id, name,last_updated,is_clan_member) VALUES (%s, %s, %s, %s)",
                        (ctx.author.id, name, current_time, 1),
                    )
                try:
                    await ctx.author.edit(nick=name)
                except discord.Forbidden:
                    await ctx.send(
                        "I don't have permission to change your nickname. My role needs to be above yours."
                    )
                # react to the message with a checkmark
                await ctx.message.add_reaction("✅")

    @commands.command(pass_context=True)
    async def whoami(self, ctx):
        # fetch all from database
        pool = await get_db(self.bot)
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT * FROM DISCORD WHERE discord_id = %s", (ctx.author.id,)
                )
                result = await cur.fetchone()

                if result:
                    result = list(result)
                    if result[2] == "":
                        result[2] = "Unknown"
                    if result[3] == "":
                        result[3] = "Unknown"
                    embed = discord.Embed(color=discord.Color.red())
                    embed.set_author(name=ctx.author.nick)
                    embed.add_field(
                        name="You are known as", value=result[1], inline=False
                    )
                    embed.add_field(name="You are a", value=result[2], inline=False)
                    embed.add_field(name="You have CR", value=result[3], inline=False)
                    embed.add_field(
                        name="You have Resonance", value=result[7], inline=False
                    )
                    embed.add_field(
                        name="You are in clan:", value=result[8], inline=False
                    )
                    embed.add_field(
                        name="You last updated your CR", value=result[4], inline=False,
                    )

                    await ctx.send(embed=embed)
                else:
                    await ctx.send(
                        "You are not registered. Use any of !cr !name or !class commands to register"
                    )

    @commands.command(pass_context=True)
    async def whois(self, ctx, *in_game_name):
        if not in_game_name:
            await ctx.send("Enter in-game name: !whois hobz")
            return
        else:
            in_game_name = in_game_name[0]

        # fetch author's clan from database
        pool = await get_db(self.bot)
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT * FROM DISCORD WHERE discord_id = %s", (ctx.author.id,)
                )
                result = await cur.fetchone()
                if result:
                    author_clan = result[8]
                else:
                    author_clan = None

        pool = await get_db(self.bot)
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT * FROM DISCORD WHERE name = %s", (in_game_name,)
                )
                result = await cur.fetchone()
                if result:
                    result = list(result)
                    if result[2] == "":
                        result[2] = "Unknown"
                    if result[3] == "":
                        result[3] = "Unknown"
                    embed = discord.Embed(color=discord.Color.red())
                    embed.set_author(name=result[1])
                    embed.add_field(name="Known as", value=result[1], inline=False)
                    embed.add_field(name="They are a", value=result[2], inline=False)
                    if result[8] == author_clan:
                        embed.add_field(
                            name="They have CR", value=result[3], inline=False
                        )
                        embed.add_field(
                            name="They have Resonance", value=result[7], inline=False
                        )
                    else:
                        embed.add_field(
                            name="They have CR", value="Redacted", inline=False
                        )
                        embed.add_field(
                            name="They have Resonance", value="Redacted", inline=False
                        )

                    embed.add_field(
                        name="They are in clan", value=result[8], inline=False
                    )
                    embed.add_field(
                        name="Last updated", value=result[4], inline=False,
                    )
                    await ctx.send(embed=embed)
                else:
                    msg = await ctx.send("No user found")
                    await asyncio.sleep(5)
                    await msg.delete()

    @commands.command(pass_context=True)
    async def top(self, ctx, *args):

        # Depending where we are generate the list of clans to show based on config ALLOW_CLAN_DATA
        pool = await get_db(self.bot)
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT * FROM configs WHERE value = %s and setting = %s",
                    (ctx.guild.id, "ALLOW_CLAN_DATA"),
                )
                result = await cur.fetchall()
            clans = []
            for server in result:
                # Get Server clan_name based server[2] value
                pool = await get_db(self.bot)
                async with pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute(
                            "SELECT * FROM configs WHERE guild = %s and setting = %s",
                            (server[1], "GUILD_NAME"),
                        )
                        new_result = await cur.fetchone()
                        clans.append(new_result[3])

        # Make sure that ctx.author.id is in the list of clans
        pool = await get_db(self.bot)
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT * FROM DISCORD WHERE discord_id = %s AND clan_name in %s",
                    (ctx.author.id, tuple(clans),),
                )
                result = await cur.fetchone()
                if not result:
                    # You can't use this command here. You are not in a clan that allows this
                    await ctx.send(
                        "You can't use this command here. You are not in the clan or correct server"
                    )
                    return

        pool = await get_db(self.bot)
        if not args:

            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    # clan_name in (clans)
                    await cur.execute(
                        "SELECT * FROM DISCORD WHERE is_clan_member = 1 and clan_name in %s ORDER BY cr DESC LIMIT 10",
                        (tuple(clans),),
                    )
                    result = await cur.fetchall()
                    embed = discord.Embed(color=discord.Color.red())
                    embed.set_author(name="Top 10 CR")
                    message = "Top 10 CRs/Res:\n"
                    if len(clans) == 1:
                        for i, row in enumerate(result):
                            message += (
                                f"{i + 1}. {row[1]} - {row[2]} - {row[3]}/{row[7]}\n"
                            )
                    elif len(clans) > 1:
                        for i, row in enumerate(result):
                            message += f"{i + 1}. {row[1]} - {row[2]} - {row[3]}/{row[7]} - {row[8]}\n"
                    await ctx.send(message)
        # elif get top n with class
        elif len(args) == 1:
            try:
                n = int(args[0])
            except ValueError:
                if args[0].title() in [
                    "Necromancer",
                    "Wizard",
                    "Hunter",
                    "Barbarian",
                    "Monk",
                    "Crusader",
                ]:
                    message = f"Top {args[0].title()} CRs/Res \n"
                    # Get top_10 by class
                    top10_by_class = []
                    async with pool.acquire() as conn:
                        async with conn.cursor() as cur:
                            await cur.execute(
                                "SELECT * FROM DISCORD WHERE class = %s AND is_clan_member = 1 AND clan_name in %s ORDER BY cr DESC LIMIT 10",
                                (args[0].title(), tuple(clans)),
                            )
                            result = await cur.fetchall()
                            if len(clans) == 1:
                                for i, row in enumerate(result):
                                    top10_by_class.append(row)
                                    message += f"{i + 1}. {row[1]} - {row[2]} - {row[3]}/{row[7]}\n"
                            elif len(clans) > 1:
                                for i, row in enumerate(result):
                                    top10_by_class.append(row)
                                    message += f"{i + 1}. {row[1]} - {row[2]} - {row[3]}/{row[7]} - {row[8]}\n"
                            if len(message) > 0:
                                await ctx.send(message)
                            return
                elif args[0] == "res":
                    message = f"Top 10 Resonance Res \n"
                    # Get top_10 by resonance
                    top10_by_resonance = []
                    async with pool.acquire() as conn:
                        async with conn.cursor() as cur:
                            await cur.execute(
                                "SELECT * FROM DISCORD WHERE is_clan_member = 1 AND clan_name in %s ORDER BY res+0 DESC LIMIT 10",
                                (tuple(clans),),
                            )

                            result = await cur.fetchall()
                            if len(clans) == 1:
                                for i, row in enumerate(result):
                                    top10_by_resonance.append(row)
                                    message += (
                                        f"{i + 1}. {row[1]} - {row[2]} - {row[7]}\n"
                                    )
                            elif len(clans) > 1:
                                for i, row in enumerate(result):
                                    top10_by_resonance.append(row)
                                    message += f"{i + 1}. {row[1]} - {row[2]} - {row[7]} - {row[8]}\n"
                            if len(message) > 0:
                                await ctx.send(message)
                            return

                else:
                    await ctx.send(
                        "Don't know what you want. Did you try full name of class?"
                    )
                    return
            if n > 0 and n < 301:

                message = "Top " + str(n) + " CRs/Res:\n"
                async with pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute(
                            "SELECT * FROM DISCORD WHERE is_clan_member = 1 AND clan_name in %s ORDER BY cr DESC LIMIT %s",
                            (tuple(clans), n),
                        )
                        result = await cur.fetchall()
                        if len(clans) == 1:
                            # break down into discord message limits of 2000
                            for i, row in enumerate(result):
                                message += f"{i + 1}. {row[1]} - {row[2]} - {row[3]}/{row[7]}\n"
                                if len(message) > 1700:
                                    await ctx.send(message)
                                    message = ""
                        elif len(clans) > 1:
                            for i, row in enumerate(result):
                                message += f"{i + 1}. {row[1]} - {row[2]} - {row[3]}/{row[7]} - {row[8]}\n"
                                if len(message) > 1700:
                                    await ctx.send(message)
                                    message = ""
                        if len(message) > 0:
                            await ctx.send(message)
            else:
                await ctx.send("Tell me a number between 1 and 100")
                return
        # elif show only specific class with top n
        elif len(args) == 2:
            try:
                n = int(args[1])
            except ValueError:
                await ctx.send("Need a number")
                return
            if n > 0 and n < 301:
                if args[0].title() in [
                    "Necromancer",
                    "Wizard",
                    "Hunter",
                    "Barbarian",
                    "Monk",
                    "Crusader",
                ]:

                    message = f"Top {str(n)} {args[0].title()} CRs/Res \n"
                    # Get top n by class
                    top_n_by_class = []
                    async with pool.acquire() as conn:
                        async with conn.cursor() as cur:
                            await cur.execute(
                                "SELECT * FROM DISCORD WHERE class = %s AND is_clan_member = 1 AND clan_name in %s ORDER BY cr DESC LIMIT %s",
                                (args[0].title(), tuple(clans), n),
                            )
                            result = await cur.fetchall()
                            if len(clans) == 1:
                                for i, row in enumerate(result):
                                    top_n_by_class.append(row)
                                    message += f"{i + 1}. {row[1]} - {row[2]} - {row[3]}/{row[7]}\n"
                                    if len(message) > 1700:
                                        await ctx.send(message)
                                        message = ""
                            elif len(clans) > 1:
                                for i, row in enumerate(result):
                                    top_n_by_class.append(row)
                                    message += f"{i + 1}. {row[1]} - {row[2]} - {row[3]}/{row[7]} - {row[8]}\n"
                                    if len(message) > 1700:
                                        await ctx.send(message)
                                        message = ""
                    await ctx.send(message)

                else:
                    await ctx.send("Need a full class name")
                    return
            else:
                await ctx.send("Tell me a number between 1 and 100")
                return
        else:
            await ctx.send("Not sure what you want to do...")
            return

    # Add member to db on join
    @commands.Cog.listener()
    async def on_member_join(self, member):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pool = await get_db(self.bot)
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT * FROM DISCORD WHERE discord_id = %s", member.id
                )
                result = await cur.fetchone()
                if result:
                    return
                else:
                    await cur.execute(
                        f"INSERT INTO DISCORD (discord_id, name, CLASS,CR,LAST_UPDATED, IS_CLAN_MEMBER ) VALUES ({member.id}, '{member.name}', '', 0, '{current_time}', 0)"
                    )
                    return

    @tasks.loop(minutes=15)
    async def database_update(self):
        # get configs from db
        pool = await get_db(self.bot)
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("select * from configs")
                configs = await cur.fetchall()
        known_configs = []
        # given guild_id, setting, value create a dict for settings and values with non unique guild_id, created a nested dict
        # in form of {guild_id: {setting: value, setting: value, setting: value...}}
        for config in configs:
            if config[1] not in known_configs:
                known_configs.append({config[1]: {}})
        for guild in known_configs:
            for config in configs:
                if config[1] in guild:
                    guild[config[1]][config[2]] = config[3]

        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for guild in known_configs:
            for guild_id, config in guild.items():
                # if GUILD_NAME and GUILD_HOME_ROLE are not set, skip
                if "GUILD_NAME" not in config or "GUILD_HOME_ROLE" not in config:
                    continue
                else:
                    # we have the guild, let's work on it
                    members = []
                    if not self.bot.get_guild(int(guild_id)):
                        continue
                    for role in self.bot.get_guild(int(guild_id)).roles:
                        if role.id == int(config["GUILD_HOME_ROLE"]):
                            members = role.members
                            break

                    # This section handles adding new members to the database
                    for member in members:
                        pool = await get_db(self.bot)
                        async with pool.acquire() as conn:
                            async with conn.cursor() as cur:
                                await cur.execute(
                                    "SELECT * FROM DISCORD WHERE discord_id = %s ",
                                    (member.id),
                                )
                                result = await cur.fetchone()
                                if (
                                    result
                                    and result[6] == 1
                                    and result[8] == config["GUILD_NAME"]
                                ):
                                    # If user in DB and Role matches DB, do nothing
                                    pass
                                elif result:
                                    # If user in DB and Role does not match DB, update DB
                                    print(
                                        f"Update user {config['GUILD_NAME']} {member.name} with {member.id} since DB is 0 but user has a role"
                                    )
                                    await cur.execute(
                                        "UPDATE DISCORD SET is_clan_member = 1,last_updated = %s,clan_name = %s WHERE discord_id = %s",
                                        (current_time, config["GUILD_NAME"], member.id),
                                    )
                                elif not result:
                                    # If user not in DB, insert user with the role
                                    print(
                                        f"Create user IDGAF {config['GUILD_NAME']} {member.name} with {member.id}  and set is_clan_member = 1"
                                    )
                                    await cur.execute(
                                        "INSERT INTO DISCORD (discord_id, name, is_clan_member,last_updated,clan_name) VALUES (%s, %s, %s, %s, %s)",
                                        (
                                            member.id,
                                            member.display_name,
                                            1,
                                            current_time,
                                            config["GUILD_NAME"],
                                        ),
                                    )

                    # This section handles removing members from the database
                    # Query for the is_clan_member = 1 users in the database
                    all_members = members
                    all_membmer_ids = [member.id for member in all_members]
                    pool = await get_db(self.bot)
                    async with pool.acquire() as conn:
                        async with conn.cursor() as cur:
                            await cur.execute(
                                "SELECT * FROM DISCORD WHERE is_clan_member = 1 and clan_name = %s",
                                config["GUILD_NAME"],
                            )
                            result = await cur.fetchall()
                            for row in result:
                                # if user not in any of the member groups, set is_clan_member = 0
                                if int(row[5]) not in all_membmer_ids:
                                    print(
                                        f"{row[1]} is not in any of the member groups, set is_clan_member = 0"
                                    )
                                    await cur.execute(
                                        "UPDATE DISCORD SET is_clan_member = 0,last_updated = %s WHERE discord_id = %s",
                                        (current_time, int(row[5])),
                                    )


def setup(bot):
    bot.add_cog(CR(bot))
