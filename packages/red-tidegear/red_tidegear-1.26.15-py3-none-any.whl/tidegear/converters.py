# SPDX-FileCopyrightText: 2025 cswimr <copyright@csw.im>
# SPDX-License-Identifier: MPL-2.0

"""Module containing discord.py argument converters."""

from typing import TYPE_CHECKING

import discord
from discord.ext.commands.converter import EmojiConverter as _DiscordEmojiConverter
from emoji import EMOJI_DATA
from redbot.core import commands
from redbot.core.i18n import Translator
from typing_extensions import override

__all__ = ["CogConverter", "EmojiConverter"]

_ = Translator("TidegearCog", __file__)


class _CogConverter:
    @classmethod
    def convert(cls, ctx: commands.Context, argument: str) -> commands.Cog:
        cog = ctx.bot.get_cog(argument)
        if not cog:
            msg = _("The {argument} cog is not loaded!").format(argument=argument)
            raise commands.BadArgument(msg)
        return cog


_EmojiConverterResult = discord.Emoji | discord.PartialEmoji


class _EmojiConverter(_DiscordEmojiConverter):
    @override
    async def convert(self, ctx: commands.Context, argument: str) -> _EmojiConverterResult:  # pyright: ignore[reportIncompatibleMethodOverride]
        argument = argument.strip()
        if EMOJI_DATA.get(argument, None):
            return discord.PartialEmoji.from_str(argument)
        return await super().convert(ctx, argument)


if TYPE_CHECKING:
    CogConverter = commands.Cog
    """This converter can be used within a command's parameter typehints to return a [`redbot.core.commands.Cog`][] object.
    **This converter does NOT return a Tidegear cog.**
    """
    EmojiConverter = _EmojiConverterResult
    """This converter can be used within a command's parameter typehints to return either a [`discord.Emoji`][] or [`discord.PartialEmoji][] object."""  # noqa: E501
else:
    CogConverter = _CogConverter
    EmojiConverter = _EmojiConverter
