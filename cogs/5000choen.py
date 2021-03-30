import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash import SlashCommand
from discord_slash import SlashContext
import cooldown
import aiohttp
import io
import asyncio
import traceback
import random, string

def randomname(n):
   randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
   return ''.join(randlst)

async def edit(msg, embed):
    await msg.edit(embeds=[embed])
    
def urlcreate(top, bottom, hoshii, noalpha, rainbow):
    result = f'http://5000choyen.app.cyberrex.ml/image?top={top}&bottom={bottom}&type=png'
    if hoshii:
        result += '&hoshii=true'
    if noalpha:
        result += '&noalpha=true'
    if rainbow:
        result += '&rainbow=true'
    return result

cool = cooldown.CoolDown(15)
class FiveThousand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_subcommand(
        base="image", name="5000choyen",
        base_description="楽しもう！", description="5000兆円ジェネレーター",
        guild_ids=[733707710784340100],
        options=[
            dict(
                name='top',
                description='上部文字',
                type=3,
                required=True
            ),
            dict(
                name='bottom',
                description='下部文字',
                type=3,
                required=True
            ),
            dict(
                name='hoshii',
                description='下部文字を「欲しい！」に固定する',
                type=5,
                required=False
            ),
            dict(
                name='noalpha',
                description='背景を白にする',
                type=5,
                required=False
            ),
            dict(
                name='rainbow',
                description='文字を虹色にする(hoshiiがTrueの場合は下部文字は虹色になりません)',
                type=5,
                required=False
            )
        ]
    )
    async def _five_thousand_gene(self, ctx, top, bottom, hoshii=False, noalpha=False, rainbow=False):
        try:
            print('実行')
            if cool.check(ctx.author.id):
                await ctx.send(f'現在クールダウン中です\n解除まで: {round(cool.retry_after(ctx.author.id), 2)}', hidden=True)
                return
            cool.add(ctx.author.id)
            
            msg = await ctx.send(embed=discord.Embed(title='Wait a few seconds...'))
            print('wait a few seconds')
            
            print('aiohttp start')
            async with aiohttp.ClientSession() as session:
                async with session.post(url=urlcreate(top, bottom, hoshii, noalpha, rainbow)) as r:
                    read = await r.read()
                    data = io.BytesIO(read)
                    file = discord.File(data, f'{randomname(10)}.PNG')
            print('aiohttp finish')
            msg_ft = await self.bot.five_thousand.send(file=file)
            print('FiveThousand sent')
            embed=discord.Embed(description='Powerd by [5000choyen-api](https://github.com/CyberRex0/5000choyen-api)')
            embed.set_image(url=msg_ft.attachments[0].url)
            #print(msg_ft.attachments[0].url)
            print(embed.image)
            await msg.edit(embed=embed)
            
            
            print('all process finished in image/5000choyen')
        except Exception as e:
            traceback.print_exc()
        return
        


def setup(bot):
    bot.add_cog(FiveThousand(bot))
