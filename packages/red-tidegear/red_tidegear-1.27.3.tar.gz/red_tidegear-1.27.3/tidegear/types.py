# SPDX-FileCopyrightText: 2025 cswimr <copyright@csw.im>
# SPDX-License-Identifier: MPL-2.0

"""This module contains type aliases related to the Discord API or general cog development."""

import discord
from redbot.core.commands.context import GuildContext

__all__ = ["GuildChannel", "GuildMessageableChannel", "GuildMessageable"]

GuildChannel = discord.abc.GuildChannel | discord.Thread
"""A superset of [`discord.abc.GuildChannel`][] that adds [`discord.Thread`][]."""

GuildMessageableChannel = discord.TextChannel | discord.VoiceChannel | discord.StageChannel | discord.Thread
"""A subset of Discord guild channels that support sending messages through [`.send`][discord.abc.Messageable.send].

Specifically, this type covers:

- [`discord.TextChannel`][]
- [`discord.VoiceChannel`][]
- [`discord.StageChannel`][]
- [`discord.Thread`][]
"""
GuildMesseagableChannel = GuildMessageableChannel  # kept due to incorrect spelling in a previous Tidegear version

GuildMessageable = GuildMessageableChannel | GuildContext
"""Any messeagable target that is scoped to a guild and implements [`.send`][discord.abc.Messageable.send].
This includes [`GuildMessageableChannel`][tidegear.types.GuildMessageableChannel]
and [`GuildContext`][redbot.core.commands.context.GuildContext].
"""
GuildMesseagable = GuildMessageable  # kept due to incorrect spelling in a previous Tidegear version
