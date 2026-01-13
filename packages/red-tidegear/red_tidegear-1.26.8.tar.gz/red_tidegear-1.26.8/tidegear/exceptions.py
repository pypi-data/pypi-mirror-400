# SPDX-FileCopyrightText: 2025 cswimr <copyright@csw.im>
# SPDX-License-Identifier: MPL-2.0

"""This module contains exceptions used within Tidegear and consuming cogs."""

from typing import Any, Callable, Self, overload

import discord
from discord.utils import MISSING

from tidegear import chat_formatting as cf


class TidegearError(Exception):
    """Parent exception for all exceptions originating from Tidegear.

    Attributes:
        default_message: If set on the class level, this will serve as a default message.
        message: An error message. May be shown to end users. Defaults to `default_message` if not provided.
        send_to_end_user: Whether or not this exception should be sent to end users when raised within a command's callback.
        send_error_kwargs: Additional keyword arguments to pass to [`send_error()`][tidegear.utils.send_error].
            Does not support `content`.
    """

    default_message: str = "No message was provided for this exception!"
    send_to_end_user: bool = False

    def __init__(
        self,
        message: str | None = None,
        /,
        *,
        send_to_end_user: bool = MISSING,
        cause: BaseException | None = None,
        suppress_context: bool = True,
        **send_error_kwargs: Any,
    ) -> None:
        if message:
            self.message: str = message
        else:
            self.message = self.default_message

        super().__init__(self.message)

        if send_to_end_user is not MISSING:
            self.send_to_end_user = send_to_end_user

        if cause:
            self.set_cause(cause, suppress_context=suppress_context)

        self.send_error_kwargs: dict[str, Any] = send_error_kwargs
        self.send_error_kwargs.pop("content", None)

    def set_cause(self, cause: BaseException, *, suppress_context: bool = True) -> Self:
        """Set an exception as the cause for this exception.

        This is intended to emulate the behavior of Python's`raise Exception from Exception` syntax,
        but without actually raising an exception.

        Args:
            cause: The exception that caused this exception.
            suppress_context: Whether or not to set `__suppress_context__` or not. Python's `raise` keyword does this.

        Raises:
            ValueError: If the exception passed to this method is the same as the method's parent exception.

        Returns:
            The exception, to allow for fluent chaining.
        """
        if cause is self:
            msg = "An exception cannot be its own cause."
            raise ValueError(msg)

        self.__cause__ = cause
        self.__suppress_context__ = suppress_context
        return self

    @overload
    async def send(
        self,
        messageable: discord.abc.Messageable | discord.Message,
        /,
        func: Callable[[str], str] = ...,
        edit_original: bool = ...,
        **kwargs: Any,
    ) -> discord.Message: ...
    @overload
    async def send(
        self, messageable: discord.Interaction, /, func: Callable[[str], str] = ..., edit_original: bool = ..., **kwargs: Any
    ) -> discord.InteractionMessage | discord.WebhookMessage: ...

    async def send(
        self,
        messageable: discord.abc.Messageable | discord.Interaction | discord.Message,
        /,
        func: Callable[[str], str] = cf.error,
        edit_original: bool = False,
        **kwargs: Any,
    ) -> discord.Message | discord.InteractionMessage | discord.WebhookMessage:
        """Send a message with the contents of this error's message.
        Wraps [`send_error`][tidegear.utils.send_error], and raises everything that function does.

        Args:
            messageable: The context to send the message to, or an existing message to edit.
            func: The function to use to wrap the message.
            edit_original: Determines behavior when `messageable` is an [`Interaction`][discord.Interaction] that has already been responded to.
                If this argument is `True`, the passed interaction's original response message will be edited instead.
                If this argument is `False`, a follow-up message will be sent instead.
            **kwargs: Additional keyword arguments to pass to [`Messageable.send()`][discord.abc.Messageable.send].

        Returns:
            The sent message.
        """  # noqa: E501
        from tidegear.utils import send_error  # noqa: PLC0415 # this is here to prevent potential circular imports in the future

        return await send_error(
            messageable, func=func, edit_original=edit_original, content=self.message, **self.send_error_kwargs | kwargs
        )


class ConfigurationError(TidegearError):
    """Raised whenever a cog's configuration prevents one of its features from functioning."""


class ArgumentError(TidegearError):
    """Raised whenever an argument is not passed to a function that expects it, within **kwargs."""


class ArgumentValueError(ArgumentError, ValueError):
    """Raised whenever an argument is passed to a function and is of the correct type, but has an improper value.
    Sort of similar to [`ValueError`][].
    """


class ArgumentTypeError(ArgumentError, TypeError):
    """Raised whenever an argument is passed to a function but has the wrong type.
    Sort of similar to [`TypeError`][].
    """


class NotFoundError(TidegearError, LookupError):
    """Raised whenever an operation doing some kind of search or query fails.
    Essentially a [`LookupError`][], but it is a subclass of [`TidegearError`][tidegear.exceptions.TidegearError].
    """


class ContextError(TidegearError):
    """Raised whenever a command, function, or method is called from a context it is not supposed to be called from."""


class UnmetPermissionsError(TidegearError, PermissionError):
    """Raised whenever a user or the bot does not have the required permissions to do something."""
