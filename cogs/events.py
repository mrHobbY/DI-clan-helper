from discord.ext import tasks
import discord
import datetime
import pytz
from .utils import *
from datetime import time

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Events cog is loaded")
        self.post_all_events.start()
        self.topic_date.start()
        self.post_current_events.start()

    # tasks.loop run every hour starting exactly at midnight
    @tasks.loop(time=time(7, 0, 0))
    async def post_all_events(self):
        tz = pytz.timezone("US/Eastern")
        today = datetime.datetime.now(tz).strftime("%A")
        pool = await get_db(self.bot)
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT * FROM events where day = %s", (today,))
                events = await cur.fetchall()

        # Get channel config from database from EVENT_ANNOUNCE_CHANNEL setting for every guild
        pool = await get_db(self.bot)
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT * FROM configs WHERE setting = %s",
                    ("EVENT_ANNOUNCE_CHANNEL"),
                )

                channel_id = await cur.fetchall()
        # loop over every defined channel and send the message there
        for config in channel_id:
            # print(config)
            try:
                channel = discord.utils.get(
                    self.bot.get_all_channels(), id=int(config[3])
                )
            except Exception as e:
                print(e)
                continue
            if channel:
                # remove all messages in the channel
                try:
                    await channel.purge()
                except Exception as e:
                    print(
                        f"Cannot purge channel {channel.name} in guild {channel.guild.name} {e}"
                    )
                    continue

                # Get the number of unique events
                unique_events = set([event[1] for event in events])
                msg = f"There are {len(unique_events)} events today **({datetime.datetime.now(tz).strftime('%A, %B %d')})**\n"
                now = datetime.datetime.now(tz).strftime("%m/%d/%Y")
                # format time with am/pm and timezone
                time_format = "%m/%d/%Y %I:%M %p %z"

                # Post a message of Event name and all times for that event where time is [4] in the tuple:
                for event in sorted(unique_events):
                    msg += f"**{event}** at "
                    events_msg = ""

                    for event_details in events:
                        if event_details[1] == event:
                            time_string = f"{now} {event_details[4]} -0400"
                            my_date = datetime.datetime.strptime(
                                time_string, time_format
                            )
                            dt_utc = my_date.astimezone(pytz.UTC)
                            epoch_my_date = int(dt_utc.timestamp())
                            events_msg += f"<t:{epoch_my_date}:t> "
                    msg += events_msg + "\n"
                try:
                    await channel.send(msg)
                except Exception as e:
                    print(
                        f"Cannot send message to channel {channel.name} in guild {channel.guild.name} {e}"
                    )
                    continue

    @tasks.loop(minutes=5)
    async def topic_date(self):
        tz = pytz.timezone("America/New_York")
        # Get channel config from database from EVENT_ANNOUNCE_CHANNEL setting for every guild
        pool = await get_db(self.bot)
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT * FROM configs WHERE setting = %s", ("TIME_CHANNEL"),
                )

                channel_id = await cur.fetchall()
        # loop over every defined channel and send the message there
        for config in channel_id:
            # discord find voice channel by id
            channel = discord.utils.get(self.bot.get_all_channels(), id=int(config[3]))
            # print(channel)
            now = datetime.datetime.now(tz).strftime("%I:%M %p")
            # update voice channel name
            topic = f"Game time: ~ {now}"
            if channel:
                try:
                    await channel.edit(topic=topic, name=topic)
                except Exception as e:
                    print(
                        f"Error updating channel {channel.name} in guild {channel.guild.name} {e}"
                    )
            else:
                pass

    @tasks.loop(minutes=1)
    async def post_current_events(self):
        tz = pytz.timezone("US/Eastern")
        today = datetime.datetime.now(tz).strftime("%A")
        pool = await get_db(self.bot)
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT * FROM events where day = %s", (today,))
                events = await cur.fetchall()
        # events = ([12, 'First event', 'Bilefen', 'Thursday', '5:20 pm', None, 'World', 1],
        #          [12, 'Long event', 'Bilefen', 'Thursday', '6:00 pm', 2, 'World', 1])
        pool = await get_db(self.bot)
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT * FROM configs WHERE setting = %s",
                    ("EVENT_ANNOUNCE_CHANNEL"),
                )

                channel_id = await cur.fetchall()
        # loop over every defined channel and send the message there
        for config in channel_id:
            channel = discord.utils.get(self.bot.get_all_channels(), id=int(config[3]))
            if channel:

                # Get the number of unique events
                current_event_counter = 0
                events_posted = False

                msg = "Upcoming and current events:\n"
                for event_details in events:
                    now = datetime.datetime.now(tz).strftime("%m/%d/%Y")
                    time_format = "%m/%d/%Y %I:%M %p %z"
                    time_string = f"{now} {event_details[4]} -0400"
                    event_start_est = datetime.datetime.strptime(
                        time_string, time_format
                    )
                    event_start_utc = event_start_est.astimezone(pytz.UTC)
                    epoch_start_utc = int(event_start_utc.timestamp())
                    epoch_now = int(datetime.datetime.now(pytz.utc).timestamp())

                    # if we are 15 minutes or less before the epoch_start_utc, post the event
                    if (
                        (
                            epoch_start_utc - epoch_now <= 900
                            and epoch_now - epoch_start_utc <= 60
                        )
                        and not event_details[5]
                    ):  # 15 min before and 1 min after and not duration
                        msg += f"**{event_details[1]}** at {event_details[2]} starting <t:{epoch_start_utc}:R> \n"
                        current_event_counter += 1
                    elif event_details[5] and (
                        epoch_start_utc - epoch_now <= 900
                        and epoch_now - epoch_start_utc
                        <= 60 + (event_details[5] * 60 * 60)
                    ):  # 15 min before and 1 min after and duration
                        msg += f"**{event_details[1]}** at {event_details[2]} starting <t:{epoch_start_utc}:R> for {event_details[5]} hours until <t:{epoch_start_utc + (event_details[5] * 60 * 60)}:t> \n"
                        current_event_counter += 1
                all_messages = await channel.history(limit=None).flatten()
                for message in all_messages:
                    if "There are" in message.content:
                        pass
                    elif current_event_counter == 0:
                        try:
                            await message.delete()
                        except Exception as e:
                            print(
                                f"Error  deleting message {message.content} in channel {channel.name} in guild {channel.guild.name} {e}"
                            )

                    elif "Upcoming and current events" in message.content:
                        events_posted = True
                        if message.content.strip() == msg.strip():
                            pass
                        else:
                            try:
                                await message.edit(content=msg)
                            except Exception as e:
                                print(
                                    f"Error editing message {message.content} in channel {channel.name} in guild {channel.guild.name} {e}"
                                )
                if not events_posted and current_event_counter > 0:
                    try:
                        await channel.send(msg)
                    except Exception as e:
                        print(
                            f"Error sending message {msg} in channel {channel.name} in guild {channel.guild.name} {e}"
                        )


def setup(bot):
    bot.add_cog(Events(bot))
