from discord.ext import commands, tasks, bridge
import discord
from collections import defaultdict
from .utils import *


class RoleSync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("RoleSync cog is loaded")
        self.sync_roles.start()

    @tasks.loop(minutes=5)
    async def sync_roles(self):
        # Connect to db and get setting for each guild
        pool = await get_db(self.bot)
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT * FROM configs WHERE setting = 'ROLE_SYNC'")
                result = await cur.fetchall()
                sync_configs = defaultdict(list)
                for row in result:
                    # value field is a column separated string with source_guild_id:source_guild_role:target_guild_role:prefix
                    # [discord_id:[{source_guild_id:source_guild_id, source_guild_role:source_guild_role, target_guild_role:target_guild_role, prefix:prefix}]]
                    key = row[1]
                    value = row[3]
                    # split the string into dictionary with source_guild_id, source_guild_role, target_guild_role, prefix keys
                    value = value.split(":")
                    if not value[0] or not value[1] or not value[2] or not value[3]:
                        continue
                    sync_configs[key].append(
                        {
                            "source_guild_id": int(value[0]),
                            "source_guild_role": int(value[1]),
                            "target_guild_role": int(value[2]),
                            "prefix": value[3],
                        }
                    )

        for key, value in sync_configs.items():
            # get the source guild and target guild
            target_guild = self.bot.get_guild(int(key))
            if not target_guild:
                continue
            # print(f"======= Starting sync for {target_guild.name} =======")
            for source_guild_dict in value:

                source_guild = self.bot.get_guild(source_guild_dict["source_guild_id"])
                # print(
                #     f"======= Starting role sync from {source_guild.name} to {target_guild.name} ======="
                # )
                if not source_guild:
                    continue
                # get the source guild role and target guild role objects
                source_guild_role = source_guild.get_role(
                    source_guild_dict["source_guild_role"]
                )
                if not source_guild_role:
                    continue
                target_guild_role = target_guild.get_role(
                    source_guild_dict["target_guild_role"]
                )
                if not target_guild_role:
                    continue
                # get the source guild member for source_guild_role
                source_guild_members_with_role = (
                    source_guild_role.members
                )  # list of members with source_guild_role
                target_guild_members_with_role = (
                    target_guild_role.members
                )  # list of members with target_guild_role
                target_guild_members_all = (
                    target_guild.members
                )  # list of all members in target_guild
                # list of members without target_guild_role in target guild but with source_guild_role in source guild. We need to add the role and prefix to them
                target_guild_members_without_role = [
                    member
                    for member in target_guild_members_all
                    if member not in target_guild_members_with_role
                    and member in source_guild_members_with_role
                ]
                # list of members who are in target_guild_members but not in source_guild_members. We need to remove the role and prefix from them
                target_guild_members_without_role_in_source_guild = [
                    member
                    for member in target_guild_members_with_role
                    if member not in source_guild_members_with_role
                ]
                for member in target_guild_members_without_role:
                    # add the role to the member
                    print(
                        f"Adding {target_guild_role.name} to member {member.name} in {target_guild.name}"
                    )
                    try:
                        await member.add_roles(target_guild_role)
                    except discord.Forbidden:
                        print(
                            f"Could not add {target_guild_role.name} to member {member.name} in {target_guild.name}"
                        )
                    # send a message to the member with the role added
                for member in target_guild_members_without_role_in_source_guild:
                    # remove the role from the member
                    print(
                        f"Removing {target_guild_role.name} from member {member.name} in {target_guild.name}"
                    )
                    try:
                        await member.remove_roles(target_guild_role)
                    except discord.Forbidden:
                        print(
                            f"Could not remove {target_guild_role.name} from member {member.name} in {target_guild.name}"
                        )
                    # send a message to the member with the role removed
                # print(
                #     f"======= Finished role sync from {source_guild.name} to {target_guild.name} ======="
                # )
                # print(f"======= Starting name sync =======")
                # get the source guild member for source_guild_role
                source_guild_members_with_role = (
                    source_guild_role.members
                )  # list of members with source_guild_role
                target_guild_members_with_role = (
                    target_guild_role.members
                )  # list of members with target_guild_role
                target_guild_members_all = (
                    target_guild.members
                )  # list of all members in target_guild
                # list of members without target_guild_role in target guild but with source_guild_role in source guild. We need to add the role and prefix to them
                target_guild_members_without_role = [
                    member
                    for member in target_guild_members_all
                    if member not in target_guild_members_with_role
                    and member in source_guild_members_with_role
                ]
                # list of members who are in target_guild_members but not in source_guild_members. We need to remove the role and prefix from them
                target_guild_members_without_role_in_source_guild = [
                    member
                    for member in target_guild_members_with_role
                    if member not in source_guild_members_with_role
                ]

                for source_member in source_guild_members_with_role:

                    # get the target guild member with the same name
                    target_member = target_guild.get_member(source_member.id)
                    if not target_member:
                        continue
                    # get target_member name without prefix
                    prefix = source_guild_dict["prefix"]
                    target_member_name = (
                        target_member.nick
                        if target_member.nick
                        else target_member.display_name
                    )
                    target_member_name_no_prefix = target_member_name.replace(
                        f"[{source_guild_dict['prefix']}] ", ""
                    )

                    source_member_name = (
                        source_member.nick
                        if source_member.nick
                        else source_member.display_name
                    )
                    # sanitize source member name and remove prefix

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
                        source_member_name = source_member_name.replace(word, "")

                    source_member_name_with_prefix = (
                        f"[{source_guild_dict['prefix']}] {source_member_name}"
                    )
                    source_member_name_no_prefix = source_member_name.replace(
                        prefix, ""
                    )

                    # if the names are different, change the name
                    if target_member_name_no_prefix != source_member_name_no_prefix:
                        print(
                            f"Changing {target_member_name} to [{prefix}] {source_member_name} in {target_guild.name}"
                        )
                        try:
                            nick = f"[{prefix}] {source_member_name}"
                            await target_member.edit(
                                # trim to 32 characters to avoid discord name length limit
                                nick=nick[:32],
                            )
                        except discord.Forbidden:
                            print(
                                f"Could not change {target_member_name} to [{prefix}] {source_member_name} in {target_guild.name}"
                            )
                    elif source_member_name_with_prefix != target_member_name:
                        print(
                            f"Changing {target_member_name} to [{prefix}] {source_member_name} in {target_guild.name}"
                        )
                        try:
                            await target_member.edit(
                                nick=f"[{prefix}] {source_member_name}"
                            )
                        except discord.Forbidden:
                            print(
                                f"Could not change {target_member_name} to [{prefix}] {source_member_name} in {target_guild.name}"
                            )
                for (
                    gone_source_member
                ) in target_guild_members_without_role_in_source_guild:
                    # get the target guild member with the same name
                    target_member = target_guild.get_member(gone_source_member.id)
                    if not target_member:
                        continue
                    # get target_member name without prefix
                    prefix = source_guild_dict["prefix"]
                    target_member_name = (
                        target_member.nick
                        if target_member.nick
                        else target_member.display_name
                    )
                    target_member_name_no_prefix = target_member_name.replace(
                        f"[{prefix}] ", ""
                    )
                    source_member_name = (
                        gone_source_member.nick
                        if gone_source_member.nick
                        else gone_source_member.display_name
                    )
                    source_member_name_no_prefix = source_member_name.replace(
                        f"[{prefix}] ", ""
                    )
                    # if the names are different, change the name
                    if target_member_name != source_member_name_no_prefix:
                        print(
                            f"Changing gone {target_member_name} to {source_member_name_no_prefix} in {target_guild.name}"
                        )
                        try:
                            await target_member.edit(nick=source_member_name_no_prefix)
                        except discord.Forbidden:
                            print(
                                f"Could not change gone {target_member_name} to {source_member_name_no_prefix} in {target_guild.name}"
                            )

            # print(f"======= Finished sync for {target_guild.name} =======")

    @bridge.bridge_command(pass_context=True)
    @commands.is_owner()
    async def add_sync(
        self,
        ctx,
        target_guild_id,
        source_guild_id,
        source_guild_role,
        target_guild_role,
        prefix,
    ):
        """Add a role sync config"""
        if (
            not target_guild_id
            or not source_guild_id
            or not source_guild_role
            or not target_guild_role
            or not prefix
        ):
            await ctx.respond("Missing arguments")
            return
        pool = await get_db(self.bot)
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT * FROM configs WHERE setting = 'ROLE_SYNC' and guild = %s AND value = %s",
                    (
                        target_guild_id,
                        f"{source_guild_id}:{source_guild_role}:{target_guild_role}:{prefix}",
                    ),
                )
                result = await cur.fetchall()
                if result:
                    await ctx.respond(f"Config already exists")
                    return
                await cur.execute(
                    "INSERT INTO configs (setting, guild, value) VALUES (%s, %s, %s)",
                    (
                        "ROLE_SYNC",
                        target_guild_id,
                        f"{source_guild_id}:{source_guild_role}:{target_guild_role}:{prefix}",
                    ),
                )
                await conn.commit()
                await ctx.respond(f"Added config")

    # command to list all guilds
    @bridge.bridge_command(pass_context=True)
    @commands.is_owner()
    async def list_guilds(self, ctx):
        """List all guilds"""
        guilds = self.bot.guilds
        output = ""
        for guild in guilds:
            output += f"{guild.name} - {guild.id}\n"
        # send dm to author
        await ctx.author.respond(output)

    # command to list all roles in a guild
    @bridge.bridge_command(pass_context=True)
    @commands.is_owner()
    async def list_roles(self, ctx, guild_id):
        """List all roles in a guild"""
        guild = self.bot.get_guild(int(guild_id))
        if not guild:
            await ctx.respond("Guild not found")
            return
        roles = guild.roles
        output = ""
        for role in roles:
            output += f"{role.name} - {role.id}\n"
        # send dm to author
        await ctx.author.respond(output)

    # Get current sync configs
    @bridge.bridge_command(pass_context=True)
    @commands.is_owner()
    async def get_sync_configs(self, ctx):
        """Get current sync configs"""
        pool = await get_db(self.bot)
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT * FROM configs WHERE setting = 'ROLE_SYNC'")
                result = await cur.fetchall()
                if not result:
                    await ctx.respond(f"No configs found")
                    return
                output = ""
                for config in result:
                    # for config[1] get guild name by id
                    target_guild_name = self.bot.get_guild(int(config[1])).name
                    # spit config[3] into parts separated by :
                    config_parts = config[3].split(":")
                    # 0 - source guild id, 1 - source guild role id, 2 - target guild role id, 3 - prefix
                    # for config[3][0] get guild name by id
                    source_guild_name = self.bot.get_guild(int(config_parts[0]))
                    # for config[3][1] get role name by id
                    source_guild_role_name = self.bot.get_guild(
                        int(config_parts[0])
                    ).get_role(int(config_parts[1]))
                    # for config[3][2] get role name by id
                    target_guild_role_name = self.bot.get_guild(
                        int(config[1])
                    ).get_role(int(config_parts[2]))
                    # for config[3][3] get prefix
                    # send message to author
                    await ctx.author.respond(
                        f"Syncing to {target_guild_name} from {source_guild_name} the source role {source_guild_role_name} and applying {target_guild_role_name} with prefix {config_parts[3]}\n"
                    )

    # add sync config
    @bridge.bridge_command(pass_context=True)
    @commands.is_owner()
    async def add_sync_config(
        self,
        ctx,
        target_guild_id,
        source_guild_id,
        source_guild_role_id,
        target_guild_role_id,
        prefix,
    ):
        """Add a sync config"""
        if (
            not target_guild_id
            or not source_guild_id
            or not source_guild_role_id
            or not target_guild_role_id
            or not prefix
        ):
            await ctx.respond(
                "target_guild_id, source_guild_id, source_guild_role_id, target_guild_role_id, prefix"
            )
            return
        pool = await get_db(self.bot)
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT * FROM configs WHERE setting = 'ROLE_SYNC' and guild = %s AND value = %s",
                    (
                        target_guild_id,
                        f"{source_guild_id}:{source_guild_role_id}:{target_guild_role_id}:{prefix}",
                    ),
                )
                result = await cur.fetchall()
                if result:
                    await ctx.respond(f"Config already exists")
                    return
                # source_guild_id:source_guild_role:target_guild_role:prefix
                await cur.execute(
                    "INSERT INTO configs (setting, guild, value) VALUES (%s, %s, %s)",
                    (
                        "ROLE_SYNC",
                        target_guild_id,
                        f"{source_guild_id}:{source_guild_role_id}:{target_guild_role_id}:{prefix}",
                    ),
                )
                await conn.commit()
                await ctx.respond(f"Added config")


def setup(bot):
    bot.add_cog(RoleSync(bot))
