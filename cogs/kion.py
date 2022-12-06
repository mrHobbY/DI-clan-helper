import discord
from discord.ext.commands import Cog
from discord.ext import bridge
from discord.ui import Button, View
import datetime
from dateutil import parser
import re
from .utils import *

"""
# make kion on date with 3 slots
!createkion 9/4/2022 6pm 8:30pm 9:00pm
# remove all kions on date 
!nokion 9/4/2022
# show all kions  
!showkions 
# Show specific date kions
!showkion 9/4/2022
"Kion scheduled for 9/4/2022 has following available slots for the signup" 


# by clicking the button it signs the officer for opening

!mykion : tells officer when to open a kion
!notme 9/4/2022 : removes the officer

!postkion 9/4/2022

"Posts/updates pregenerated messages with officers signed up" 

"""


def standardize_date(dateinput):
    dt = parser.parse(dateinput)
    # if date is in the before yesterday, do not allow
    if dt < datetime.datetime.now() - datetime.timedelta(days=2):
        # raise error
        raise ValueError("Date is in the past")

    return dt.strftime("%Y-%m-%d")


class KionButtonView(View):
    def __init__(self, ctx, db_result):
        super().__init__(timeout=20)

        self.ctx = ctx
        self.db_result = db_result
        self.buttons = []
        self.value = None

        for i in range(len(db_result)):
            if db_result[i][3] is None:
                self.buttons.append(
                    Button(
                        style=discord.ButtonStyle.green,
                        label=db_result[i][2],
                        row=i,
                        custom_id=db_result[i][2],
                    )
                )
            else:
                # get discord display_name from row[3] in current ctx.guild
                member = ctx.guild.get_member(db_result[i][3])

                self.buttons.append(
                    Button(
                        style=discord.ButtonStyle.red,
                        label=f"{member.display_name} at {db_result[i][2]}",
                        disabled=True,
                        row=i,
                        custom_id=db_result[i][2],
                    )
                )

        async def callback(interaction):
            for button in self.children:
                button.disabled = True
                button.label = "Done"
            await interaction.response.edit_message(view=self)
            self.value = "green"
            self.stop()

        for button in self.buttons:
            button.callback = callback
            self.add_item(button)

    async def on_button_click(self, button, interaction):
        await interaction.response.send_message(
            f"You clicked {button.label}", ephemeral=True
        )

    async def on_error(self, error: Exception, item, interaction) -> None:
        await interaction.response.send_message(
            f"An error occurred: {error}", ephemeral=True
        )

    async def interaction_check(self, interaction) -> bool:
        if interaction.user.id == self.ctx.author:
            await interaction.response.send_message(
                "You are not the author of this command", ephemeral=True
            )

    async def on_timeout(self):
        for button in self.children:
            button.disabled = True
        await self.message.edit(view=self)


class KionView(View):
    def __init__(self, ctx):
        super().__init__(timeout=20)
        self.ctx = ctx

    async def on_timeout(self):
        for button in self.children:
            button.disabled = True
        await self.message.edit(view=self)

    async def on_error(self, error: Exception, item, interaction) -> None:
        await interaction.response.send_message(
            f"An error occurred: {error}", ephemeral=True
        )

    async def interaction_check(self, interaction) -> bool:
        if interaction.user.id == self.ctx.author:
            await interaction.response.send_message(
                "You are not the author of this command", ephemeral=True
            )
        return True


class TwoButtonView(View):
    def __init__(self, ctx):
        super().__init__(timeout=20)
        self.ctx = ctx
        self.value = None

    @discord.ui.button(
        label="Do it!", style=discord.ButtonStyle.green, custom_id="green"
    )
    async def button_callback(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        for button in self.children:
            button.disabled = True
            button.label = "Done"
        await interaction.response.edit_message(view=self)
        self.value = "green"
        self.stop()

    @discord.ui.button(label="Hold on", style=discord.ButtonStyle.red, custom_id="red")
    async def red_button_callback(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        for button in self.children:
            button.disabled = True
            button.label = "Try later"
        await interaction.response.edit_message(view=self)
        self.value = "red"
        self.stop()

    async def on_timeout(self):
        for button in self.children:
            button.disabled = True
        await self.message.edit(view=self)

    async def on_error(self, error: Exception, item, interaction) -> None:
        await interaction.response.send_message(
            f"An error occurred: {error}", ephemeral=True
        )

    async def interaction_check(self, interaction) -> bool:
        if interaction.user.id == self.ctx.author:
            await interaction.response.send_message(
                "You are not the author of this command", ephemeral=True
            )
        return True


class Kion(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Kion cog is loaded")

    @bridge.bridge_command(pass_context=True)
    @bridge.has_permissions(manage_roles=True)
    async def createkion(self, ctx, date, *times):
        try:
            proper_date = standardize_date(date)
        except ValueError:
            # date cannot be in the past
            await ctx.send(
                f"Unless you have time machine, you cannot create a kion in the past"
            )
            return
        except:
            # Send message about date format
            await ctx.send(f"Invalid date {date}. Use yyyy-mm-dd (2022-12-25) format")
            return
        valid_ampm_time_regex = "(1[0-2]|0?[1-9]):([0-5][0-9])([AaPp][Mm])"
        pattern = re.compile(valid_ampm_time_regex)
        # times at least 1 no more than 5
        if len(times) < 1 or len(times) > 5:
            await ctx.send(
                f"Invalid number of Kion runs: {len(times)}. Use between 1-5 times"
            )
            return

        for time in times:
            if not pattern.match(time):
                # await ctx.send(f"Invalid time {time}. Use 12 hour format: 1:00pm")
                await ctx.send(f"Invalid time {time}. Use 12 hour format: 1:00pm")
                return

        view = TwoButtonView(ctx)

        await ctx.send(f"You are about to create Kion on {date} at {times} ", view=view)
        await view.wait()

        if view.value == "green":
            # Create kion in the database. Check if it already exists. If it does, do nothing.
            pool = await get_db(self.bot)
            for time in times:
                async with pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute(
                            "SELECT * FROM kion WHERE event_date = %s AND event_time = %s",
                            (proper_date, time),
                        )
                        result = await cur.fetchone()
                        if result is None:
                            # does not exist, create
                            await cur.execute(
                                "INSERT INTO kion (event_date, event_time) VALUES (%s, %s)",
                                (proper_date, time),
                            )
                            await ctx.send(f"Kion created on {date} at {time}")
                        else:
                            # already exists, do nothing
                            await ctx.send(f"Kion already exist on {date} at {time}")
                            pass

    @bridge.bridge_command(pass_context=True)
    @bridge.has_permissions(manage_roles=True)
    async def nokion(self, ctx, date):
        try:
            proper_date = standardize_date(date)
        except ValueError:
            # date cannot be in the past
            await ctx.send(
                f"Unless you have time machine, you cannot delete a kion from the past"
            )
            return
        except:
            # Send message about date format
            await ctx.send(f"Invalid date {date}. Use yyyy-mm-dd (2022-12-25) format")
            return

        view = TwoButtonView(ctx)
        pool = await get_db(self.bot)
        # check if kion exists in db
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT * FROM kion WHERE event_date = %s", (proper_date,)
                )
                result = await cur.fetchone()
                if result is None:
                    # does not exist, do nothing
                    await ctx.send(f"Kion is not scheduled on {date}")
                    return

        await ctx.send(f"You are about to remove all Kions on {date}", view=view)
        await view.wait()

        if view.value == "green":
            # Remove kion in the database.

            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        "DELETE FROM kion WHERE event_date = %s", (proper_date,)
                    )
                    await ctx.send(f"All Kions removed on {date}")

    @bridge.bridge_command(pass_context=True)
    @bridge.has_permissions(manage_roles=True)
    async def showkions(self, ctx):
        pool = await get_db(self.bot)
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                # where event_date >= current date in DATE format and group by event_date
                await cur.execute(
                    "SELECT * FROM kion WHERE event_date >= %s group by event_date ORDER BY event_date ASC",
                    (datetime.date.today(),),
                )
                result = await cur.fetchall()
                if result is None:
                    await ctx.send(f"No Kions scheduled")
                    return
                else:
                    # print result
                    message = "```"
                    message += "Scheduled Kions:\n"
                    for row in result:
                        message += f"{row[1]}\n"
                    message += "```"
                    await ctx.send(message)

    @bridge.bridge_command(pass_context=True)
    @bridge.has_permissions(manage_roles=True)
    async def showkion(self, ctx, date=None):
        if not date:
            await ctx.send(f"Please specify a date")
            return
        try:
            proper_date = standardize_date(date)
        except ValueError:
            # date cannot be in the past
            pass
        except:
            # Send message about date format
            await ctx.send(f"Invalid date {date}. Use yyyy-mm-dd (2022-12-25) format")
            return

        pool = await get_db(self.bot)
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                # where event_date >= current date in DATE format and group by event_date
                await cur.execute(
                    "SELECT * FROM kion WHERE event_date = %s ORDER BY event_date ASC",
                    (proper_date,),
                )
                result = await cur.fetchall()
                if result is None:
                    await ctx.send(f"No Kions scheduled")
                    return
                else:
                    # Create reaction buttons for each result. Make it green if row[3] is Null, otherwise red and value of row[3]
                    # Reacting to button will update row[3] to user.id
                    buttons = []
                    for i in range(len(result)):
                        if result[i][3] is None:
                            buttons.append(
                                Button(
                                    style=discord.ButtonStyle.green,
                                    label=result[i][2],
                                    row=i,
                                    custom_id=result[i][2],
                                )
                            )
                        else:
                            # get discord display_name from row[3] in current ctx.guild
                            member = ctx.guild.get_member(result[i][3])

                            buttons.append(
                                Button(
                                    style=discord.ButtonStyle.red,
                                    label=f"{member.display_name} at {result[i][2]}",
                                    disabled=True,
                                    row=i,
                                    custom_id=result[i][2],
                                )
                            )

                    view = KionView(ctx)

                    async def callback(interaction: discord.Interaction):
                        # check if interaction.user.id already signed up for another time
                        # if so, remove it
                        # update row[3] to interaction.user.id
                        # update button to red and label to interaction.user.display_name
                        # update button to green and label to interaction.custom_id

                        # Ensure that author is interacting with their own message
                        if interaction.user.id != ctx.author.id:
                            return

                        # add timeout and remove buttons

                        pool = await get_db(self.bot)
                        async with pool.acquire() as conn:
                            async with conn.cursor() as cur:
                                await cur.execute(
                                    "SELECT * FROM kion WHERE event_date = %s AND officer_discord_id = %s",
                                    (proper_date, interaction.user.id),
                                )
                                result = await cur.fetchone()
                                if result is not None:
                                    # remove existing signup
                                    await cur.execute(
                                        "UPDATE kion SET officer_discord_id = NULL WHERE event_date = %s AND officer_discord_id = %s",
                                        (proper_date, interaction.user.id),
                                    )
                                    # update button to green
                                    for button in view.children:
                                        if button.custom_id == result[2]:
                                            button.style = discord.ButtonStyle.green
                                            button.disabled = False
                                            button.label = result[2]
                                            break

                                # update new signup
                                await cur.execute(
                                    "UPDATE kion SET officer_discord_id = %s WHERE event_date = %s AND event_time = %s",
                                    (
                                        interaction.user.id,
                                        proper_date,
                                        interaction.custom_id,
                                    ),
                                )
                                # update button to red
                                for button in view.children:
                                    if button.custom_id == interaction.custom_id:
                                        button.style = discord.ButtonStyle.red
                                        button.disabled = True
                                        button.label = f"{interaction.user.display_name} at {interaction.custom_id}"
                                        break
                        await interaction.response.edit_message(view=view)

                    for button in buttons:
                        button.callback = callback
                        view.add_item(button)

                    await ctx.send(f"Kions on {date}", view=view)
                    await view.wait()

    @bridge.bridge_command(pass_context=True)
    @bridge.has_permissions(manage_roles=True)
    async def mykion(self, ctx):
        pool = await get_db(self.bot)
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                # where event_date >= current date in DATE format and group by event_date
                await cur.execute(
                    "SELECT * FROM kion WHERE event_date >= %s and officer_discord_id = %s ORDER BY event_date ASC",
                    (datetime.date.today(), ctx.author.id),
                )
                result = await cur.fetchall()
                if len(result) == 0:
                    await ctx.send(f"No Kions for you")
                    return
                else:
                    # print result
                    message = "```"
                    message += "You are scheduled for:\n"
                    for row in result:
                        message += f"{row[1]} {row[2]}\n"
                    message += "```"
                    await ctx.send(message)

    @bridge.bridge_command(pass_context=True)
    @bridge.has_permissions(manage_roles=True)
    async def notme(self, ctx, date=None):
        # updates database for spefic date with discord_officer_id = NULL, so that it can be assigned to someone else
        # if date is not specified, it will update all kions for the user
        if date is None:
            pool = await get_db(self.bot)
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    # where event_date >= current date in DATE format and group by event_date
                    await cur.execute(
                        "UPDATE kion SET officer_discord_id = NULL WHERE officer_discord_id = %s",
                        (ctx.author.id,),
                    )
                    # add checkmark reaction
                    await ctx.message.add_reaction("✅")
                    return
        else:
            try:
                proper_date = standardize_date(date)
            except ValueError:
                # date cannot be in the past
                ctx.message.add_reaction("❌")
                return
            except:
                # Send message about date format
                await ctx.send(
                    f"Invalid date {date}. Use yyyy-mm-dd (2022-12-25) format"
                )
                return
            pool = await get_db(self.bot)
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    # where event_date >= current date in DATE format
                    await cur.execute(
                        "UPDATE kion SET officer_discord_id = NULL WHERE officer_discord_id = %s and event_date = %s",
                        (ctx.author.id, proper_date),
                    )
                    # add checkmark reaction
                    await ctx.message.add_reaction("✅")

    @bridge.bridge_command(pass_context=True)
    @bridge.has_permissions(manage_roles=True)
    async def postkion(self, ctx, date=None):
        if date is None:
            await ctx.send("Please specify a date")
            return
        else:
            try:
                proper_date = standardize_date(date)
            except ValueError:
                # date cannot be in the past
                ctx.message.add_reaction("❌")
            except:
                # Send message about date format
                await ctx.send(
                    f"Invalid date {date}. Use yyyy-mm-dd (2022-12-25) format"
                )
                return
            pool = await get_db(self.bot)
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    # where event_date >= current date in DATE format and group by event_date
                    await cur.execute(
                        "SELECT * FROM kion WHERE event_date = %s ORDER BY event_time ASC",
                        (proper_date,),
                    )
                    result = await cur.fetchall()
                    if len(result) == 0:
                        await ctx.send(f"No Kions for {date}")
                        return
                    else:
                        # print result
                        # convert DATE to day of the week string
                        proper_date = parser.parse(proper_date)
                        day_of_week = proper_date.strftime("%A")
                        # Convert DATE to Full Month and number day string
                        month_day = proper_date.strftime("%B %d")
                        message = f"@everyone Alliance! Next KION IS SCHEDULED FOR {day_of_week}, {month_day} \n\n"
                        message += f"We will have {len(result)} runs\n\n"
                        for row in result:
                            if row[3] is None:
                                message += f"{row[2]} need an officer to open \n\n"
                            else:
                                # get discord display_name from row[3] in current ctx.guild
                                message += f"{row[2]} opened by <@{int(row[3])}>\n\n"

                        # get channel id from db config
                        await cur.execute(
                            "SELECT * FROM configs WHERE setting = %s",
                            ("KION_CHANNEL"),
                        )

                        channel_id = await cur.fetchall()
                        channel = self.bot.get_channel(int(channel_id[0][1]))
                        if channel is None:
                            await ctx.send("KION_CHANNEL not set")
                            return
                        await channel.send(message)


def setup(bot):
    bot.add_cog(Kion(bot))
