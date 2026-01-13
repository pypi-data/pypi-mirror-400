# SPDX-FileCopyrightText: 2025 cswimr <copyright@csw.im>
# SPDX-License-Identifier: MPL-2.0

"""Module containing discord.py argument converters."""

from typing import TYPE_CHECKING

import discord
import discord.ext.commands
import emoji
from redbot.core import commands
from redbot.core.commands import CogConverter
from redbot.core.i18n import Translator
from typing_extensions import override

__all__ = [
    "CogConverter",  # Kept for backwards compatibility reasons
    "EmojiConverter",
]

_ = Translator("TidegearCog", __file__)


_EmojiConverterResult = discord.Emoji | discord.PartialEmoji


class _EmojiConverter(discord.ext.commands.converter.EmojiConverter):
    @override
    async def convert(self, ctx: commands.Context, argument: str) -> _EmojiConverterResult:  # pyright: ignore[reportIncompatibleMethodOverride]
        argument = argument.strip()
        if emoji.EMOJI_DATA.get(argument, None):
            return discord.PartialEmoji.from_str(argument)
        try:
            return await super().convert(ctx, argument)
        except commands.BadArgument as err:
            match = discord.PartialEmoji._CUSTOM_EMOJI_RE.match(argument)  # noqa: SLF001
            if match is not None:
                groups = match.groupdict()
                animated = bool(groups["animated"])
                emoji_id = int(groups["id"])
                name = str(groups["name"])
                return discord.PartialEmoji(name=name, animated=animated, id=emoji_id)
            raise err


if TYPE_CHECKING:
    EmojiConverter = _EmojiConverterResult
    """This converter can be used within a command's parameter typehints to return either a [`discord.Emoji`][] or [`discord.PartialEmoji`][] object."""  # noqa: E501
else:
    EmojiConverter = _EmojiConverter
