# Discord Packages
import discord
from discord.ext import commands

import traceback

from cogs.music.music_errors import WrongTextChannelError, WrongVoiceChannelError

# Bot Utilities
from cogs.helpformatter import commandhelper
from cogs.utils.paginator import Scroller


class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = self.bot.main_logger.bot_logger.getChild("Errors")

    async def base_msg(self, ctx, state: int = 0xFCBA03):
        embed = discord.Embed(color=state)
        embed.title = '{errors.error_occurred}'
        embed.set_footer(icon_url=ctx.author.avatar_url,
                         text=f'{ctx.author.name}#{ctx.author.discriminator}')
        return embed

    @commands.Cog.listener()
    async def on_command_error(self, ctx, err):

        # Help commands
        if (isinstance(err, commands.MissingRequiredArgument) or
                isinstance(err, commands.BadArgument)):
            paginator = commandhelper(ctx, ctx.command, ctx.invoker, include_subcmd=False)
            scroller = Scroller(ctx, paginator)
            await scroller.start_scrolling()

        if isinstance(err, (commands.CommandNotFound)):
            return

        async def send_error_embed(description, **kwargs):
            embed = await self.base_msg(ctx, state=0xFC0303)
            embed.description = description
            if kwargs.get("title"):
                embed.title = kwargs["title"]
            embed = ctx.localizer.format_embed(embed)
            return await ctx.send(embed=embed)

        # Music related errors
        if isinstance(err, commands.CommandInvokeError):
            if (err.original == 'Join a voice concert first.'):
                return await send_error_embed('{errors.join_voice_first}')

            elif (err.original == 'Not connected.'):
                return await send_error_embed('{errors.not_connected}')

            elif (err.original == 'I need the `CONNECT` and `SING(SPEAK)` permissions.'):
                return await send_error_embed('{errors.need_permission}')

            elif (err.original == 'Not singing'):
                return await send_error_embed('{not_playing}')

            elif (err.original == 'Not listening'):
                return await send_error_embed('{have_to_listen}')

            elif (err.original == 'The concert is currently full'):
                return await send_error_embed('{errors.full_channel}')

        if isinstance(err, WrongVoiceChannelError):
            if(err.original.startswith("You need to be in my voice concert")):
                return await send_error_embed(err.channels[0].name, title='{errors.my_channel}')

            elif (err.original.startswith('You need to be in the right voice concert')):
                changed = False
                response = ctx.localizer.format_str('{settings_check.voicechannel}')
                for channel_id in err.channels:
                    channel = ctx.guild.get_channel(channel_id)
                    if channel is not None:
                        response += f'{channel.name}, '
                        changed = True
                if changed:
                    return await send_error_embed(response[:-2], title='{errors.right_channel}')
                else:
                    return await send_error_embed('{errors.right_channel}')

        if isinstance(err, WrongTextChannelError):
            try:
                await ctx.message.delete()
            except Exception as e:
                self.logger.debug("Error deleting message: %s\nTraceback: %s" % (e, err))
            response = ctx.localizer.format_str('{settings_check.textchannel}')
            for channel_id in err.channels:
                response += f'<#{channel_id}>, '
            msg = await send_error_embed(response[:-2], title='{errors.right_channel}')
            return await msg.delete(delay=5)

        if isinstance(err, commands.CheckFailure):
            pass

        if isinstance(err, commands.CommandOnCooldown):
            await ctx.send(f"{ctx.message.author.mention} Command is on cooldown. "
                           f"Try again in `{err.retry_after:.1f}` seconds.")

        elif isinstance(err, commands.NoPrivateMessage):
            await ctx.send('That command is not available in DMs')

        else:
            # Log all exceptions if the bot is in debug mode
            if self.bot.debug:
                tb = err.__traceback__
                traceback.print_tb(tb)
                self.logger.debug("Error running command: %s\nTraceback: %s" % (ctx.command, err))

            else:
                to_log = (RuntimeError, commands.CheckFailure, commands.CommandInvokeError,
                          commands.NoPrivateMessage)

                if isinstance(err, to_log):
                    self.logger.debug("Error running command: %s\nTraceback: %s" % (ctx.command, err))


def setup(bot):
    bot.add_cog(Errors(bot))
