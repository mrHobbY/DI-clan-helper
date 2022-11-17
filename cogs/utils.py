import os
from dotenv import load_dotenv
import aiomysql
from discord.ext import commands


def get_db(bot):
    load_dotenv()
    host = os.getenv("MYSQL_HOST")
    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    db = os.getenv("MYSQL_DB")
    return aiomysql.create_pool(
        host=host, user=user, password=password, db=db, autocommit=True, loop=bot.loop,
    )


class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Utils cog is loaded")


def setup(bot):
    bot.add_cog(Utils(bot))
