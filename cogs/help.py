import discord
from discord.ext import commands, bridge


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Help cog is loaded")

    # overwritten default help command for better text formatting
    @bridge.bridge_command()
    async def help(self, ctx):
        embed = discord.Embed(color=discord.Color.red())
        embed.set_author(name="hobz#8445")
        embed.add_field(
            name="!cr number", value="• Update your current CR", inline=False
        )
        embed.add_field(
            name="!res number", value="• Update your current Resonance", inline=False
        )
        embed.add_field(name="!class hunter", value="• Update your class", inline=False)
        embed.add_field(name="!bg number", value="• Update you BG stats", inline=False)
        embed.add_field(
            name="!name name",
            value="• Update your in game name and Discord name",
            inline=False,
        )
        embed.add_field(
            # whois <user>
            name="!whois user",
            value="• Get info about any user",
            inline=False,
        )
        embed.add_field(
            # whoami
            name="!whoami",
            value="• Get info about yourself",
            inline=False,
        )
        embed.add_field(
            name="!top [filter] ]",
            value="• Get the list of players !top , !top res, !top hunter",
            inline=False,
        )
        # embed.add_field(
        #     name="!mygroup",
        #     value="• Show your current RoE group",
        #     inline=False,
        # )
        # embed.add_field(
        #     name="!whogroup [group]",
        #     value="• Show all members in speficic RoE group",
        #     inline=False,
        # )
        # embed.add_field(
        #     name="!roegroups",
        #     value="• Show all RoE groups",
        #     inline=False,
        # )
        embed.add_field(
            name="!admin_help",
            value="• Show privileged commands for admins",
            inline=False,
        )

        await ctx.respond(embed=embed)

    @bridge.bridge_command()
    @bridge.has_permissions(manage_roles=True)
    async def admin_help(self, ctx):
        embed = discord.Embed(color=discord.Color.red())
        embed.set_author(name="Admin only commands")

        embed.add_field(
            name="Overview",
            value="There are five main areas where this bot can help you run your server\n"
            "1. CR tracker. Members can use !cr/!res/!name commands to update their info"
            "As admin you need to set !set_guild_name TEST_NAME and !set_home_role @role\n"
            "2.Role sync. There is an ability to sync member roles between the servers and update them on join or leave events. Reach out to hobz to setup\n"
            "3. Kions tracker. Speak to hobz to set up. Not a self-service yet.\n"
            "4. ROE groups manager. Speak to hobz to set up. Not a self-service yet.\n"
            "5. DI events tracker. use !set_event_channel #channel to set it up. The messages in that channel will be purged\n"
            "If you have any questions reach out to hobz#8445 on discord\n"
            " ",
            inline=False,
        )

        embed.add_field(
            name="!set_event_channel",
            value="• !set_event_channel #channel to set the DI event channel",
            inline=False,
        )
        embed.add_field(
            name="!set_kion_channel",
            value="• !set_kion_channel #channel to set the DI kion announcement channel",
            inline=False,
        )
        embed.add_field(
            name="!set_timer_channel",
            value="• !set_timer_channel #channel to set the timer channel",
            inline=False,
        )
        embed.add_field(
            name="!set_guild_name",
            value="• !set_guild_name TEST_NAME to set the guild name",
            inline=False,
        )
        embed.add_field(
            name="!set_home_role",
            value="• !set_home_role @role to set the home role",
            inline=False,
        )

        embed.add_field(
            name="!allow_clan_data",
            value="• !allow_clan_data server_id to allow your clan data on foreign servers",
            inline=False,
        )
        embed.add_field(
            name="!disable_clan_data",
            value="• !disable_clan_data server_id to disallow your clan data on foreign servers. !disable_clan_data to see where it is enabled now",
            inline=False,
        )
        embed.add_field(
            name="!roe",
            value="• !roe add|delete|update @member group. !roe add @hobzz 3",
            inline=False,
        )
        embed.add_field(
            name="!createkion",
            value="• !createkion 9/4/2022 6:00pm 8:30pm 9:00pm # Schedule 3 runs",
            inline=False,
        )
        embed.add_field(
            name="!nokion",
            value="• !nokion 9/4/2022 # Remove scheduled run on target date",
            inline=False,
        )
        embed.add_field(
            name="!showkions",
            value="• !showkions # Show all scheduled runs",
            inline=False,
        )
        embed.add_field(
            name="!showkion",
            value="• !showkion 9/4/2022 # Show all scheduled runs on target date",
            inline=False,
        )
        embed.add_field(
            name="!mykion",
            value="• !mykion # Show all scheduled runs where you are assigned to open it",
            inline=False,
        )
        embed.add_field(
            name="!notme",
            value="• !notme [date]# Remove yourself from a scheduled run on target date or all dates if date is not speficied",
            inline=False,
        )
        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
