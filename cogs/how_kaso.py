import discord
from discord.ext import commands

class Delta_to:
    def __init__(self, day, hour, min, sec, milli, micro):
        self.day = day
        self.hour = hour
        self.min = min
        self.sec = sec
        self.milli = milli
        self.micro = micro
    def __str__(self):
        return f"Delta_to(day={self.day}, hour={self.hour}, min={self.min}, sec={self.sec}, milli={self.milli}, micro={self.micro})"

def trans(delta):
    day = delta.days

    hour = delta.seconds // 3600

    min = (delta.seconds - hour * 3600) // 60

    sec = delta.seconds - (hour * 3600) - (min * 60)

    milli = int(delta.microseconds / 1000)
    micro = int(delta.microseconds - milli * 1000)
    return Delta_to(day, hour, min, sec, milli, micro)

class How_kaso(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.content == '過疎' or message.author.bot:
            return

        msgs = await message.channel.history(limit=2).flatten()

        n = message.created_at
        l = msgs[1].created_at
        delta = n - l
        t = trans(delta)
        await message.reply(f'ただいまの過疎記録、{t.day}日 {t.hour}時間 {t.min}分 {t.sec}秒 {t.milli}ミリ秒')
        if str(message.author.id) in self.bot.send_kaso_count.keys():
            self.bot.send_kaso_count[str(message.author.id)] += 1
        if str(message.author.id) not in self.bot.send_kaso_count.keys():
            self.bot.send_kaso_count[str(message.author.id)] = 1

def setup(bot):
    bot.add_cog(How_kaso(bot))
