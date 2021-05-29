import discord
from discord.ext import commands, tasks
from discord_slash import SlashCommand
import os
import re
import datetime
from bot import ChozatuBot
from bson.objectid import ObjectId
import discord_components
import sys


TOKEN = os.environ.get("TOKEN")
MONGO_DB_URL = os.environ.get('MONGO_DB_URL')
MONGO_DB_ID = os.environ.get("MONGO_DB_ID")
bot = ChozatuBot(
    MONGO_DB_URL,
    ObjectId(MONGO_DB_ID),
    discord_components,
    command_prefix='c/',
    intents=discord.Intents.all()
)


ddb = discord_components.DiscordComponents(bot)
slash = SlashCommand(bot, sync_commands=True)

try:
    sys.argv[2]
    if sys.argv[2] == 'test':
        sys.exit()
except:
    pass

bot.run(TOKEN)
