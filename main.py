import os
from discord.ext import commands, bridge
import discord
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN" + "_" + os.getenv("env"))
OWNER_DISCORD_ID = os.getenv("OWNER_DISCORD_ID")


class Bot(bridge.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=["!"],
            allowed_mentions=discord.AllowedMentions(
                users=True, everyone=False, roles=False, replied_user=False
            ),
            intents=discord.Intents.all(),
            owner_id=int(OWNER_DISCORD_ID),
        )

    async def on_ready(self):
        print("Bot loaded")
        await self.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching, name="!help")
        )


bot = Bot()


def main():
    bot.remove_command("help")
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and not filename.startswith("_"):
            bot.load_extension(f"cogs.{filename[:-3]}")
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
