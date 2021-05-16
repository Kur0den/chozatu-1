import discord
from discord.ext import commands, tasks
import datetime
from discord_slash import SlashCommand
from discord_slash import SlashContext
from discord_slash import utils
import os
import re
import datetime
from pykakasi import kakasi
import aiohttp

with open('config.json', 'r', encoding='utf-8') as file:
    from json import load
    config = load(file)


kakasi = kakasi()
kakasi.setMode('J', 'H')
conv = kakasi.getConverter()

def to_h(self, text):
    return conv.do(text)

commands.Bot.to_h = to_h

async def fetch_message(self, url):
    id_regex = re.compile(r'(?:(?P<channel_id>[0-9]{15,21})-)?(?P<message_id>[0-9]{15,21})$')
    link_regex = re.compile(
        r'https?://(?:(ptb|canary|www)\.)?discord(?:app)?\.com/channels/'
        r'(?:[0-9]{15,21}|@me)'
        r'/(?P<channel_id>[0-9]{15,21})/(?P<message_id>[0-9]{15,21})/?$'
    )
    match = id_regex.match(url) or link_regex.match(url)
    channel_id = match.group("channel_id")
    message_id = int(match.group("message_id"))

    channel = await bot.fetch_channel(channel_id)
    message = await channel.fetch_message(message_id)
    return message

commands.Bot.fetch_message = fetch_message

async def close(self):
    await self.ready_ch.send('<a:server_rotation:774429204673724416>停止')
    for extension in tuple(self.__extensions):
        try:
            self.unload_extension(extension)
        except Exception:
            pass

    for cog in tuple(self.__cogs):
        try:
            self.remove_cog(cog)
        except Exception:
            pass

    await super().close()
commands.Bot.close = close

TOKEN = os.environ.get("TOKEN")
bot = commands.Bot(command_prefix='c/', intents=discord.Intents.all())
bot.config = config
slash = SlashCommand(bot, sync_commands=True)

bot.ready = False

time_remove_role_regix = re.compile(
    r'(?P<user_id>[0-9]{15,21})/'
    r'(?P<role_id>[0-9]{15,21})/'
    r'(?P<datetime>[0-9]{4}\-[0-9]{2}\-[0-9]{2} [0-9]{2}\:[0-9]{2}\:[0-9]{2}\.[0-9]{6})'
)

from glob import glob
files = glob('./cogs/*')

count = 0
for f in files:
    if f.endswith('.py'):
        f = f[len('./cogs/'):-(len('.py'))]
        if f == 'template':
            continue
        bot.load_extension(f'cogs.{f}')
        print(f'cogs.{f} was loaded!')
        count += 1



print('#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#')
print(f'\n    ALL COG WAS LOADED\n    COG COUNT : {count}\n    {datetime.datetime.now().strftime("%H : %M : %S")}\n')
print('#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#')


@bot.check
def check_commands(ctx):
    return ctx.guild.id == config['guild']


@bot.event
async def on_ready():
    if bot.ready:
        return
    #bot_id, token, guild_id
    #await utils.manage_commands.remove_all_commands_in(804649928638595093, TOKEN, 733707710784340100)

    bot.guild = bot.get_guild(config['guild'])

    # 運営ロールオブジェクトの取得
    bot.unei_role = bot.guild.get_role(config['unei_role'])

    # slashコマンド実行履歴を送信するチャンネル関連
    ch = await bot.fetch_channel(config['slash_hist'])
    bot.history_channel = ch

    # yutronコマンド関連
    bot.yutron_backup = bot.get_channel(config['yutron_image_ch'])
    bot.yutron_images = []
    async for msg in bot.yutron_backup.history(limit=None):
        if msg.content.startswith('https://'):
            bot.yutron_images.append(msg.content)

    # scsコマンド関連
    bot.scs_backup = bot.get_channel(config['scs_image_ch'])
    bot.scs_images = []
    async for msg in bot.scs_backup.history(limit=None):
        if msg.content.startswith('https://'):
            bot.scs_images.append(msg.content)

    # rule コマンド関連
    rule_basic_ch = bot.get_channel(config['rule_basic_ch'])
    rule_basic_msg = await rule_basic_ch.fetch_message(config['rule_basic_msg'])

    rule_mcserver_ch = bot.get_channel(config['rule_mcserver_ch'])
    rule_mcserver_msg = await rule_mcserver_ch.fetch_message(config['rule_mcserver_msg'])

    rule_siritori_ch = bot.get_channel(config['rule_siritori_ch'])
    rule_siritori_msg = await rule_siritori_ch.fetch_message(config['rule_siritori_msg'])

    bot.rules = {
        "basic": rule_basic_msg.content,
        "mcserver": rule_mcserver_msg.content,
        "siritori": rule_siritori_msg.content
    }

    # pin機能関連
    bot.pin_ch = bot.get_channel(config['pin_ch'])
    webhooks = await bot.pin_ch.webhooks()
    bot.pin_webhook = discord.utils.get(webhooks, name='超雑談鯖_pin_wh')

    # 起動情報関連
    bot.ready_ch = bot.get_channel(config['ready_ch'])
    await bot.ready_ch.send('<a:server_rotation:774429204673724416>起動')

    #運営部屋取得
    bot.unei_ch = bot.get_channel(config['unei_ch'])

    # approve関連
    bot.approve_ch = bot.get_channel(config['approve_ch'])
    bot.wait_until_approve_role = bot.guild.get_role(config['wait_until_approve_role'])

    # ボイスチャット時間報酬関連
    bot.voice_time_ch = bot.get_channel(config['voice_time_ch'])
    bot.voice_money_min = config['voice_money_min']
    bot.voice_money_max = config['voice_money_max']
    bot.voice_give_per = config['voice_give_per']

    # NG_WORD 関連
    bot.ng_word_ch = bot.get_channel(config['ng_word_ch'])
    bot.ng_words = []
    async for msg in bot.ng_word_ch.history(limit=None):
        bot.ng_words.append(msg.content)

    # ロール自動削除系
    bot.time_remove_role_ch = await bot.fetch_channel(config['time_remove_role_ch'])
    bot.time_remove_role = {}
    bot.time_remove_role_guild = bot.guild

    async for msg in bot.time_remove_role_ch.history(limit=None):
        match = time_remove_role_regix.match(msg.content)
        bot.time_remove_role[datetime.datetime.strptime(match.group('datetime'), '%Y-%m-%d %H:%M:%S.%f')] = dict(
            user_id = int(match.group('user_id')),
            role_id = int(match.group('role_id')),
            message = msg
        )

    # メッセージレポート機能関連
    report_channel = bot.get_channel(config['report_channel'])
    whs = await report_channel.webhooks()
    bot.report_wh = discord.utils.get(whs, name='main')

    # しりとり関連
    bot.siritori_ch = bot.get_channel(config['siritori_ch'])
    bot.siritori_list = []
    async for msg in bot.siritori_ch.history(limit=None):
        if msg.author.bot or msg.content.startswith(bot.command_prefix) or msg.content.startswith('!') or msg.content in bot.siritori_list:
            continue
        bot.siritori_list.insert(0, msg.content)
    bot.siritori = True

    # その他
    bot.ready = True
    print("ready")

    time_action_loop.stop()
    time_action_loop.start()
    return

@tasks.loop(seconds=60.0)
async def time_action_loop():
    delete_keys = []
    now = datetime.datetime.utcnow()
    for _datatime in bot.time_remove_role.keys():
        if now > _datatime:
            try:
                member = await bot.time_remove_role_guild.fetch_member(bot.time_remove_role[_datatime]['user_id'])
                role = bot.time_remove_role_guild.get_role(bot.time_remove_role[_datatime]['role_id'])
                await member.remove_roles(role)
                await bot.time_remove_role[_datatime]['message'].delete()
                delete_keys.append(_datatime)
            except:
                traceback.print_exc()

    for key in delete_keys:
        del bot.time_remove_role[key]

@bot.event
async def on_slash_command(ctx):
    if not ctx.guild.id == config['guild']:
        return

    used_command = ctx.name
    used_subcommand = ctx.subcommand_name
    used_channel = ctx.channel.mention
    used_author = ctx.author.mention
    embed = discord.Embed(title='コマンドが実行されました')
    embed.add_field(name='コマンド名', value=used_command)
    embed.add_field(name='サブコマンド名', value=used_subcommand)
    embed.add_field(name='使用されたチャンネル', value=used_channel)
    embed.add_field(name='使用者', value=used_author)
    await bot.history_channel.send(embed=embed, allowed_mentions=discord.AllowedMentions.none())


bot.run(TOKEN)
