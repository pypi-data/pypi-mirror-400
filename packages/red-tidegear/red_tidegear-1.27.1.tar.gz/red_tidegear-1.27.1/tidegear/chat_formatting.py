# SPDX-FileCopyrightText: 2025 cswimr <copyright@csw.im>
# SPDX-License-Identifier: MPL-2.0

# ruff:  noqa: PLC0415

"""Wrapper around [`redbot.core.utils.chat_formatting`][] that overrides a couple functions to use Tidegear constants."""

import datetime
import enum
import typing

import discord
import humanize
from redbot.core.utils.chat_formatting import (
    bold,
    box,
    escape,
    format_perms_list,
    header,
    humanize_list,
    humanize_number,
    hyperlink,
    inline,
    italics,
    pagify,
    quote,
    rich_markup,
    spoiler,
    strikethrough,
    subtext,
    text_to_file,
    underline,
)

from tidegear import constants

__all__ = [
    # tidegear
    "TimestampStyle",
    "format_datetime",
    "error",
    "warning",
    "info",
    "success",
    "question",
    "humanize_timedelta",
    # redbot
    "bold",
    "box",
    "header",
    "hyperlink",
    "inline",
    "italics",
    "spoiler",
    "pagify",
    "strikethrough",
    "subtext",
    "underline",
    "quote",
    "escape",
    "humanize_list",
    "format_perms_list",
    "humanize_number",
    "text_to_file",
    "rich_markup",
]

humanize_timedelta = humanize.precisedelta
"""Replaces [`cf.humanize_timedelta`][redbot.core.utils.chat_formatting.humanize_timedelta] with [`humanize.precisedelta`][]."""


class TimestampStyle(enum.StrEnum):
    """Discord timestamp format options."""

    SHORT_TIME = "t"
    """`4:45 PM`"""
    LONG_TIME = "T"
    """`4:45:33 PM`"""
    SHORT_DATE = "d"
    """`7/5/25`"""
    LONG_DATE = "D"
    """`July 5th, 2025`"""
    SHORT_DATE_AND_TIME = "f"
    """`July 5th, 2025 at 4:45 PM`"""
    LONG_DATE_AND_TIME = "F"
    """`Saturday, July 5th, 2025 at 4:45 PM`"""
    RELATIVE = "R"
    """`3 minutes ago`"""


def format_datetime(dt: datetime.datetime, style: TimestampStyle = TimestampStyle.SHORT_DATE_AND_TIME) -> str:
    """Format a datetime into a Discord-compatible timestamp string.

    Similar to [`discord.utils.format_dt`][], but uses an enum to provide better code readability.

    Example:
        ```python
        from discord.utils import utcnow
        from tidegear import chat_formatting as cf

        datetime = utcnow()
        print(cf.format_datetime(dt=datetime, style=cf.TimestampStyle.LONG_DATE_AND_TIME))
        ```

    Args:
        dt: The datetime to convert into a Discord timestamp.
        style: The timestamp style to apply.

    Returns:
        A string like `<t:1618924800:f>` that Discord will render according to the given style.
    """
    return f"<t:{int(dt.timestamp())}:{style}>"


@typing.overload
def success(text: str, *, view: typing.Literal[False] = ...) -> str: ...
@typing.overload
def success(text: str, *, view: typing.Literal[True]) -> discord.ui.LayoutView: ...
def success(text: str, *, view: bool = False) -> str | discord.ui.LayoutView:
    """Wrap a string in a success emoji.

    Args:
        text: The text to wrap.
        view: Whether or not to return a [`LayoutView`][discord.ui.LayoutView] instead of a raw string.

    Returns:
        The wrapped text, prefixed with the [success constant][tidegear._constants.Constants.TRUE].
    """
    if view:
        layout_view = discord.ui.LayoutView()
        layout_view.add_item(item=discord.ui.TextDisplay(content=f"{constants.TRUE} {text}"))
        return layout_view
    return f"{constants.TRUE} {text}"


@typing.overload
def error(text: str, *, view: typing.Literal[False] = ...) -> str: ...
@typing.overload
def error(text: str, *, view: typing.Literal[True]) -> discord.ui.LayoutView: ...
def error(text: str, *, view: bool = False) -> str | discord.ui.LayoutView:
    """Wrap a string in an error emoji.

    Args:
        text: The text to wrap.
        view: Whether or not to return a [`LayoutView`][discord.ui.LayoutView] instead of a raw string.

    Returns:
        The wrapped text, prefixed with the [error constant][tidegear._constants.Constants.FALSE].
    """
    if view:
        layout_view = discord.ui.LayoutView()
        layout_view.add_item(item=discord.ui.TextDisplay(content=f"{constants.FALSE} {text}"))
        return layout_view
    return f"{constants.FALSE} {text}"


@typing.overload
def warning(text: str, *, view: typing.Literal[False] = ...) -> str: ...
@typing.overload
def warning(text: str, *, view: typing.Literal[True]) -> discord.ui.LayoutView: ...
def warning(text: str, *, view: bool = False) -> str | discord.ui.LayoutView:
    """Wrap a string in a warning emoji.

    Args:
        text: The text to wrap.
        view: Whether or not to return a [`LayoutView`][discord.ui.LayoutView] instead of a raw string.

    Returns:
        The wrapped text, prefixed with the [warning constant][tidegear._constants.Constants.WARNING].
    """
    if view:
        layout_view = discord.ui.LayoutView()
        layout_view.add_item(item=discord.ui.TextDisplay(content=f"{constants.WARNING} {text}"))
        return layout_view
    return f"{constants.WARNING} {text}"


@typing.overload
def question(text: str, *, view: typing.Literal[False] = ...) -> str: ...
@typing.overload
def question(text: str, *, view: typing.Literal[True]) -> discord.ui.LayoutView: ...
def question(text: str, *, view: bool = False) -> str | discord.ui.LayoutView:
    """Wrap a string in a question emoji.

    Args:
        text: The text to wrap.
        view: Whether or not to return a [`LayoutView`][discord.ui.LayoutView] instead of a raw string.

    Returns:
        The wrapped text, prefixed with the [question constant][tidegear._constants.Constants.NONE].
    """
    if view:
        layout_view = discord.ui.LayoutView()
        layout_view.add_item(item=discord.ui.TextDisplay(content=f"{constants.NONE} {text}"))
        return layout_view
    return f"{constants.NONE} {text}"


@typing.overload
def info(text: str, *, view: typing.Literal[False] = ...) -> str: ...
@typing.overload
def info(text: str, *, view: typing.Literal[True]) -> discord.ui.LayoutView: ...
def info(text: str, *, view: bool = False) -> str | discord.ui.LayoutView:
    """Wrap a string in an information emoji.

    Args:
        text: The text to wrap.
        view: Whether or not to return a [`LayoutView`][discord.ui.LayoutView] instead of a raw string.

    Returns:
        The wrapped text, prefixed with the [info constant][tidegear._constants.Constants.INFO].
    """
    if view:
        layout_view = discord.ui.LayoutView()
        layout_view.add_item(item=discord.ui.TextDisplay(content=f"{constants.INFO} {text}"))
        return layout_view
    return f"{constants.INFO} {text}"
