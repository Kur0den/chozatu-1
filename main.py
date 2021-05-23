import discord
from discord.ext import commands, tasks
from discord_slash import SlashCommand
import os
import re
import datetime
from bot import ChozatuBot

TOKEN = os.environ.get("TOKEN")
bot = ChozatuBot(command_prefix='c/', intents=discord.Intents.all())
slash = SlashCommand(bot, sync_commands=True)


bot.run(TOKEN)
