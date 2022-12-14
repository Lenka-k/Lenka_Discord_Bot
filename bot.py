# Discord Packages
import discord
from discord.ext import commands
from discord.flags import MemberCacheFlags

import codecs
import os
import time
import traceback
from argparse import ArgumentParser, RawTextHelpFormatter

import aiohttp
import yaml

# Bot Utilities
from cogs.utils.alias import Aliaser
from cogs.utils.context import Context
from cogs.utils.localizer import Localizer, LocalizerWrapper
from cogs.utils.logger import BotLogger
from cogs.utils.settingsmanager import Settings

initial_extensions = [
    'cogs.errors',
    'cogs.cogmanager',
    'cogs.settings',
    'cogs.misc',
    'cogs.helpformatter'
]

on_ready_extensions = [
    'cogs.nodemanager'
]


def _get_prefix(bot, message):
    if not message.guild:
        prefix = bot.settings.default_prefix
        return commands.when_mentioned_or(prefix)(bot, message)
    prefixes = bot.settings.get(message.guild, 'prefixes', 'default_prefix')
    return commands.when_mentioned_or(*prefixes)(bot, message)


class Bot(commands.Bot):
    def __init__(self, datadir, debug: bool = False):
        intents = discord.Intents.all()
        super().__init__(command_prefix=_get_prefix,
                         description=conf["bot"]["description"],
                         intents=intents,
                         member_cache_flags=MemberCacheFlags.from_intents(intents)
                         )

        self.settings = Settings(datadir, **conf['default server settings'])
        self.APIkeys = conf.get('APIkeys', {})

        self.localizer = Localizer(conf.get('locale path', "./localization"), conf.get('locale', 'en_en'))
        self.aliaser = Aliaser(conf.get('locale path', "./localization"), conf.get('locale', 'en_en'))

        self.datadir = datadir
        self.debug = debug
        self.main_logger = logger
        self.logger = self.main_logger.bot_logger.getChild("Bot")
        self.logger.debug("Debug: %s" % debug)

        for extension in initial_extensions:
            try:
                self.load_extension(extension)
            except Exception:
                self.logger.exception("Loading of extension %s failed" % extension)

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)

        # Replace aliases with commands
        ctx = self.aliaser.get_command(ctx)

        # Add the localizer
        if ctx.command and ctx.command.cog_name:
            ctx.localizer = LocalizerWrapper(self.localizer, ctx.locale, ctx.command.cog_name.lower())
        else:
            ctx.localizer = LocalizerWrapper(self.localizer, ctx.locale, None)

        await self.invoke(ctx)

    async def on_ready(self):
        if not hasattr(self, 'uptime'):
            self.uptime = time.time()

        for extension in on_ready_extensions:
            try:
                self.logger.debug("Loading extension %s" % extension)
                self.load_extension(extension)
            except Exception:
                self.logger.exception("Loading of extension %s failed" % extension)

        print(f'\nLogged in as: {self.user.name}' +
              f' in {len(self.guilds)} servers.')
        print(f'Version: {discord.__version__}\n')
        self.logger.debug("Lenka Fly\n\n\n")

        self.session = aiohttp.ClientSession(loop=self.loop)
        await self.change_presence(activity=discord.Game(type=0,
                                                         name=conf["bot"]["playing status"]),
                                   status=discord.Status.online)


    def run(self):
        try:
            super().run(conf["bot"]["token"], reconnect=True)
        except Exception as e:
            tb = e.__traceback__
            traceback.print_tb(tb)
            print(e)


def run_bot(datadir, debug: bool = False):
    bot = Bot(datadir, debug=debug)
    bot.run()


if __name__ == '__main__':
    parser = ArgumentParser(prog='Lenka',
                            description='Queen of Indie/Pop Music',
                            formatter_class=RawTextHelpFormatter)

    parser.add_argument("-D", "--debug", action='store_true', help='Sets debug to true')
    parser.add_argument("-d", "--data-directory", help='Define an alternate data directory location')

    args = parser.parse_args()
    if args.debug or os.environ.get('debug'):
        is_debug = True
    else:
        is_debug = False

    if args.data_directory:
        datadir = str(args.data_directory)
    else:
        datadir = "data"

    print(f"Data folder: {datadir}")

    with codecs.open(f"{datadir}/config.yaml", 'r', encoding='utf8') as f:
        conf = yaml.load(f, Loader=yaml.SafeLoader)

    logger = BotLogger(is_debug, conf.get('log_path', f'{datadir}/logs'))
    run_bot(debug=is_debug, datadir=datadir)
