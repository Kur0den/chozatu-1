from discord.ext.commands import Bot
from discord.ext.tasks import loop
from datetime import datetime

class ChozatuBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ready = False


        from pykakasi import kakasi
        kakasi = kakasi()
        kakasi.setMode('J', 'H')
        self.conv = kakasi.getConverter()

        with open('config.json', 'r', encoding='utf-8') as file:
            from json import load
            self.config = load(file)


        import re
        self.fm_id_regex = id_regex = re.compile(r'(?:(?P<channel_id>[0-9]{15,21})-)?(?P<message_id>[0-9]{15,21})$')
        self.fm_link_regex = re.compile(
            r'https?://(?:(ptb|canary|www)\.)?discord(?:app)?\.com/channels/'
            r'(?:[0-9]{15,21}|@me)'
            r'/(?P<channel_id>[0-9]{15,21})/(?P<message_id>[0-9]{15,21})/?$'
        )

        self.time_remove_role_regix = re.compile(
            r'(?P<user_id>[0-9]{15,21})/'
            r'(?P<role_id>[0-9]{15,21})/'
            r'(?P<datetime>[0-9]{4}\-[0-9]{2}\-[0-9]{2} [0-9]{2}\:[0-9]{2}\:[0-9]{2}\.[0-9]{6})'
        )


        # add check
        self.add_check(self.check_commands)


        # 最後に実行
        self.load_extensions()


    def __str__(self):
        return '超雑談鯖専属Bot'

    """ Bot command's check"""
    def check_commands(self, ctx):
        return ctx.guild.id == self.config['guild'] or self.is_owner(ctx.author)

    async def on_ready(self):
        if self.ready:
            return

        #bot_id, token, guild_id
        #await utils.manage_commands.remove_all_commands_in(804649928638595093, TOKEN, 733707710784340100)

        self.guild = self.get_guild(self.config['guild'])

        # 運営ロールオブジェクトの取得
        self.unei_role = self.guild.get_role(self.config['unei_role'])

        # slashコマンド実行履歴を送信するチャンネル関連
        ch = await self.fetch_channel(self.config['slash_hist'])
        self.history_channel = ch

        # yutronコマンド関連
        self.yutron_backup = self.get_channel(self.config['yutron_image_ch'])
        self.yutron_images = []
        async for msg in self.yutron_backup.history(limit=None):
            if msg.content.startswith('https://'):
                self.yutron_images.append(msg.content)

        # scsコマンド関連
        self.scs_backup = self.get_channel(self.config['scs_image_ch'])
        self.scs_images = []
        async for msg in self.scs_backup.history(limit=None):
            if msg.content.startswith('https://'):
                self.scs_images.append(msg.content)

        # rule コマンド関連
        rule_basic_ch = self.get_channel(self.config['rule_basic_ch'])
        rule_basic_msg = await rule_basic_ch.fetch_message(self.config['rule_basic_msg'])

        rule_mcserver_ch = self.get_channel(self.config['rule_mcserver_ch'])
        rule_mcserver_msg = await rule_mcserver_ch.fetch_message(self.config['rule_mcserver_msg'])

        rule_siritori_ch = self.get_channel(self.config['rule_siritori_ch'])
        rule_siritori_msg = await rule_siritori_ch.fetch_message(self.config['rule_siritori_msg'])

        self.rules = {
            "basic": rule_basic_msg.content,
            "mcserver": rule_mcserver_msg.content,
            "siritori": rule_siritori_msg.content
        }

        # pin機能関連
        self.pin_ch = self.get_channel(self.config['pin_ch'])
        webhooks = await self.pin_ch.webhooks()
        from discord.utils import get
        self.pin_webhook = get(webhooks, name='超雑談鯖_pin_wh')

        # 起動情報関連
        self.ready_ch = self.get_channel(self.config['ready_ch'])
        await self.ready_ch.send('<a:server_rotation:774429204673724416>起動')

        #運営部屋取得
        self.unei_ch = self.get_channel(self.config['unei_ch'])

        # approve関連
        self.approve_ch = self.get_channel(self.config['approve_ch'])
        self.wait_until_approve_role = self.guild.get_role(self.config['wait_until_approve_role'])

        # ボイスチャット時間報酬関連
        self.voice_time_ch = self.get_channel(self.config['voice_time_ch'])
        self.voice_money_min = self.config['voice_money_min']
        self.voice_money_max = self.config['voice_money_max']
        self.voice_give_per = self.config['voice_give_per']

        # NG_WORD 関連
        self.ng_word_ch = self.get_channel(self.config['ng_word_ch'])
        self.ng_words = []
        async for msg in self.ng_word_ch.history(limit=None):
            self.ng_words.append(msg.content)

        # ロール自動削除系
        self.time_remove_role_ch = await self.fetch_channel(self.config['time_remove_role_ch'])
        self.time_remove_role = {}
        self.time_remove_role_guild = self.guild

        async for msg in self.time_remove_role_ch.history(limit=None):
            match = self.time_remove_role_regix.match(msg.content)
            self.time_remove_role[datetime.datetime.strptime(match.group('datetime'), '%Y-%m-%d %H:%M:%S.%f')] = dict(
                user_id = int(match.group('user_id')),
                role_id = int(match.group('role_id')),
                message = msg
            )

        # メッセージレポート機能関連
        report_channel = self.get_channel(self.config['report_channel'])
        whs = await report_channel.webhooks()
        self.report_wh = get(whs, name='main')

        # しりとり関連
        self.siritori_ch = self.get_channel(self.config['siritori_ch'])
        self.siritori_list = []
        async for msg in self.siritori_ch.history(limit=None):
            if msg.author.bot or msg.content.startswith(self.command_prefix) or msg.content.startswith('!') or msg.content in self.siritori_list:
                continue
            self.siritori_list.insert(0, msg.content)
        self.siritori = True

        self.time_action_loop.stop()
        self.time_action_loop.start()


        from aiohttp import ClientSession
        self.session = ClientSession()
        self.session_bot = ClientSession(headers={'Authorization': "Bot "+self.http.token})


        print(f'ready: {self.user} (ID: {self.user.id})')
        self.ready = True

    async def close(self):
        await self.ready_ch.send('<a:server_rotation:774429204673724416>停止')
        for extension in tuple(self.extensions):
            try:
                self.unload_extension(extension)
            except Exception:
                pass

        for cog in tuple(self.cogs):
            try:
                self.remove_cog(cog)
            except Exception:
                pass

        self.session.close()
        self.session_bot.close()

        await super().close()

    async def fetch_message(self, url):

        match = self.fm_id_regex.match(url) or self.fm_link_regex.match(url)
        channel_id = match.group("channel_id")
        message_id = int(match.group("message_id"))

        channel = await self.fetch_channel(channel_id)
        message = await channel.fetch_message(message_id)
        return message

    def to_h(self, text):
        return self.conv.do(text)

    def load_extensions(self):
        from pathlib import Path
        ext_files = tuple(Path('cogs/.').glob('*.py'))
        count = 0
        for ext in ext_files:
            f = str(ext).replace('/', '.')[:-3]
            try:
                self.load_extension(f)
                print(f'{f} was loaded!')
            except:
                print(f'{f} couldn\'t load...')
            count += 1

        print('#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#')
        print(f'\n    ALL COG WAS LOADED\n    COG COUNT : {count}\n    {datetime.utcnow().strftime("%H : %M : %S")}\n')
        print('#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#')

    @loop(seconds=60.0)
    async def time_action_loop(self):
        delete_keys = []
        now = datetime.utcnow()
        for _datatime in self.time_remove_role.keys():
            if now > _datatime:
                try:
                    member = await self.time_remove_role_guild.fetch_member(self.time_remove_role[_datatime]['user_id'])
                    role = self.time_remove_role_guild.get_role(self.time_remove_role[_datatime]['role_id'])
                    await member.remove_roles(role)
                    await bot.time_remove_role[_datatime]['message'].delete()
                    delete_keys.append(_datatime)
                except:
                    traceback.print_exc()

        for key in delete_keys:
            del bot.time_remove_role[key]

    async def on_slash_command(self, ctx):
        if not ctx.guild.id == self.config['guild']:
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
        await self.history_channel.send(embed=embed, allowed_mentions=discord.AllowedMentions.none())
