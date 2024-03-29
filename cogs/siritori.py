import discord
from discord.ext import commands
import datetime

def purge_check(m):
    return not m.embeds[0].title in ['しりとりHelp', 'チャンネルリセット中...'] if bool(m.embeds) else True

def is_siritori_ch(ctx):
    return ctx.channel.id == 827104884246708254
    
class Siritori(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.has_role(738956776258535575) # 運営ロール
    @commands.check(is_siritori_ch) # しりとりチャンネル
    async def reset(self, ctx):
        if not self.bot.siritori:
            return
        self.bot.siritori = False
        n_member = 'None'
        async for msg in ctx.channel.history(limit=None):
            if msg.content.endswith('ん'):
                n_member = msg.author.mention
                break
                
        msg = await ctx.send(embed=discord.Embed(title='チャンネルリセット中...', description='しりとりが終了しました', color=0x00ffff))
        await ctx.channel.purge(limit=None, check=purge_check)
        await msg.edit(
            embed=discord.Embed(
                title='しりとりが終了しました', 
                description=f'連結回数: {len(self.bot.siritori_list)}\n”ん”をつけた人: {n_member}',
                color=0x00ffff
            )
        )
        self.bot.siritori_list = []
        self.bot.siritori = True
    
    @commands.command()
    @commands.check(is_siritori_ch) # しりとりチャンネル
    async def inv(self, ctx, moji):
        if not self.bot.siritori:
            return
        if not moji in self.bot.siritori_list:
            await ctx.send(embed=discord.Embed(title='発言されたことのない単語です', color=0xff0000), delete_after=5.0)
            await ctx.message.delete()
            return
        if self.bot.unei_role in ctx.author.roles:
            async for msg in ctx.channel.history():
                if msg.content == moji:
                    await msg.delete()
            self.bot.siritori_list.remove(moji)
            await ctx.send(embed=discord.Embed(title=f'”{moji}”を削除しました', color=0x00ffff))
            return
        
        async for msg in ctx.channel.history():
            if msg.content == moji and msg.author.id == ctx.author.id:
                await msg.delete()
                self.bot.siritori_list.remove(moji)
                await ctx.send(embed=discord.Embed(title=f'”{moji}”を削除しました', color=0x00ffff))
                return
        await ctx.send(embed=discord.Embed(f'過去100メッセージに{ctx.author.mention}が送信した”{moji}”という内容のメッセージがみつかりませんでした', color=0xff0000), delete_after=5.0)
        return
    
    @commands.command()
    @commands.check(is_siritori_ch) # しりとりチャンネル
    async def show(self, ctx, page=1):
        if not self.bot.siritori:
            return
        tango_count = 1
        page_count = 1
        pages = {}
        page_naiyou = ''
        for r in range(0, len(self.bot.siritori_list), 10):
            for tango in self.bot.siritori_list[r:r+10]:
                if page_naiyou == '':
                    page_naiyou = f"{tango_count}. {tango}"
                else:
                    page_naiyou += f"\n{tango_count}. {tango}"
                tango_count += 1
            pages[page_count] = page_naiyou
            page_count += 1
            page_naiyou = ''
        await ctx.send(embed=discord.Embed(title='しりとり履歴', description=f'```{pages[page]}```').set_footer(text=f'{page}/{page_count-1}'))
        return
    
    @commands.command(name='len')
    @commands.check(is_siritori_ch) # しりとりチャンネル
    async def _len(self, ctx):
        if not self.bot.siritori:
            return
        await ctx.send(embed=discord.Embed(title='現在の連結回数', description=len(self.bot.siritori_list), color=0x00ffff))
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if not self.bot.siritori:
            return
        if not message.channel.id == 827104884246708254:
            return
        
        if message.author.bot or message.content.startswith(self.bot.command_prefix) or message.content.startswith('!'):
            return
        
        if message.content in self.bot.siritori_list:
            await message.delete()
            await message.channel.send(embed=discord.Embed(title=f'”{message.content}” はすでに使用されています', color=0xff0000).set_author(name=message.author.name, icon_url=message.author.avatar.url))
            return
        
        self.bot.siritori_list.append(message.content)
        
        
def setup(bot):
    bot.add_cog(Siritori(bot))
