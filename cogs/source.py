import discord
from discord.ext import commands
from inspect import getsourcelines
from os.path import relpath




class Source(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def source(self, ctx, *, command=None):
        source_url = 'https://github.com/Req-kun/chozatu'
        branch = 'main'
        if command is None:
            return await ctx.send(source_url)

        obj = self.bot.get_command(command.replace('.', ' '))
        if obj is None:
            return await ctx.send('Could not find command.')

        src = obj.callback.__code__
        module = obj.callback.__module__
        filename = src.co_filename

        lines, firstlineno = getsourcelines(src)
        if not module.startswith('discord'):
            location = relpath(filename).replace('\\', '/')
        else:
            location = module.replace('.', '/') + '.py'
            source_url = 'https://github.com/Rapptz/discord.py'
            branch = 'master'
        await ctx.send(f'<{source_url}/blob/{branch}/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}>')

def setup(bot):
    bot.add_cog(Source(bot))
