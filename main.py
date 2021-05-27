import discord
from discord.ext import commands, tasks
from discord_slash import SlashCommand
import os
import re
import datetime
from bot import ChozatuBot
from bson.objectid import ObjectId
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType


TOKEN = os.environ.get("TOKEN")
MONGO_DB_URL = os.environ.get('MONGO_DB_URL')
MONGO_DB_ID = os.environ.get("MONGO_DB_ID")
bot = ChozatuBot(
    MONGO_DB_URL,
    ObjectId(MONGO_DB_ID),
    command_prefix='c/',
    intents=discord.Intents.all()
)


ddb = DiscordComponents(bot)
slash = SlashCommand(bot, sync_commands=True)


bot.run(TOKEN)
