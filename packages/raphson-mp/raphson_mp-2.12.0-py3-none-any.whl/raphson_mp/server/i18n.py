import gettext as gettext_lib
import logging
from collections.abc import Callable, Iterator
from datetime import timedelta
from pathlib import Path
from typing import Any

import jinja2
from aiohttp import web
from typing_extensions import override

from raphson_mp.common import const
from raphson_mp.server import vars

_LOGGER = logging.getLogger(__name__)

_FALLBACK_LANGUAGE = "en"
LANGUAGES: dict[str, str] = {
    "en": "English",
    "nl": "Nederlands",
}

_DOMAINS = ["frontend", "backend"]
_LOCALEDIR = Path(const.PACKAGE_PATH, "translations")
_TRANSLATIONS: dict[str, dict[str, gettext_lib.NullTranslations]] = {domain: {} for domain in _DOMAINS}
_NULL_TRANSLATIONS = gettext_lib.NullTranslations()


def translations(domain: str, locale: str | None) -> gettext_lib.NullTranslations:
    if locale is not None and locale != _FALLBACK_LANGUAGE:
        if locale not in _TRANSLATIONS[domain]:
            # translation is not loaded yet
            if locale not in LANGUAGES:
                raise ValueError("Invalid locale:" + locale)
            try:
                _TRANSLATIONS[domain][locale] = gettext_lib.translation(domain, _LOCALEDIR, [locale])
            except Exception as ex:
                _LOGGER.warning("failed to load translation file %s for language %s: %s", domain, locale, ex)
                _TRANSLATIONS[domain][locale] = _NULL_TRANSLATIONS

        return _TRANSLATIONS[domain][locale]
    return _NULL_TRANSLATIONS


def locale_from_request(request: web.Request) -> str:
    """
    Returns two letter language code, matching a language code in
    the LANGUAGES dict
    """
    if user := vars.USER.get():
        if user.language:
            _LOGGER.debug("using user language: %s", user.language)
            return user.language

    if "Accept-Language" in request.headers:
        languages: list[tuple[float, str]] = []
        for line in request.headers.getall("Accept-Language"):
            try:
                for language in line.split(","):
                    if ";q=" in language:
                        split = language.split(";q=")
                        languages.append((float(split[1].strip()), split[0].strip()))
                    else:
                        languages.append((1, language.strip()))
            except Exception:
                _LOGGER.warning("failed to parse Accept-Language header %s", line)

        for _score, language in sorted(languages, reverse=True):
            if language in LANGUAGES:
                _LOGGER.debug("using browser language: %s", language)
                return language

    return _FALLBACK_LANGUAGE


def gettext(message: str, **variables: str):
    return translations("backend", vars.LOCALE.get()).gettext(message) % variables


def gettext_lazy(message: str, **variables: str):
    return LazyString(gettext, message, **variables)


def ngettext(singular: str, plural: str, num: int, **variables: str):
    return translations("backend", vars.LOCALE.get()).ngettext(singular, plural, num) % variables


def format_timedelta(
    delta: timedelta | int,
):
    seconds = delta.seconds if isinstance(delta, timedelta) else delta

    if seconds > 10:
        return gettext("In the future")
    elif seconds > -10:
        return gettext("Just now")
    elif seconds > -60:
        return ngettext(
            "%(seconds)s second ago",
            "%(seconds)s seconds ago",
            -seconds,
            seconds=str(-seconds),
        )
    elif seconds > -50 * 60:
        return ngettext(
            "%(minutes)s minute ago",
            "%(minutes)s minutes ago",
            -seconds // 60,
            minutes=str(-seconds // 60),
        )
    elif seconds > -30 * 60 * 60:
        return ngettext(
            "%(hours)s hour ago",
            "%(hours)s hours ago",
            -seconds // (60 * 60),
            hours=str(-seconds // (60 * 60)),
        )
    elif seconds > -50 * 24 * 60 * 60:
        return ngettext(
            "%(days)s day ago",
            "%(days)s days ago",
            -seconds // (24 * 60 * 60),
            days=str(-seconds // (24 * 60 * 60)),
        )
    elif seconds > -400 * 24 * 60 * 60:
        return ngettext(
            "%(months)s months ago",
            "%(months)s months ago",
            -seconds // (30 * 24 * 60 * 60),
            months=str(-seconds // (30 * 24 * 60 * 60)),
        )
    else:
        return gettext("Long ago")


class _JinjaTranslations:
    @staticmethod
    def gettext(message: str):
        return translations("backend", vars.LOCALE.get()).gettext(message)

    @staticmethod
    def ngettext(singular: str, plural: str, num: int):
        return translations("backend", vars.LOCALE.get()).ngettext(singular, plural, num)


def install_jinja2_extension(jinja_env: jinja2.Environment):
    jinja_env.add_extension("jinja2.ext.i18n")
    jinja_env.install_gettext_translations(  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
        _JinjaTranslations, newstyle=True
    )


"""
LazyString is based on the implementation from flask-babel
https://github.com/python-babel/flask-babel/blob/master/flask_babel/speaklater.py

Copyright (c) 2010 by Armin Ronacher.

Some rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

* Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above
  copyright notice, this list of conditions and the following
  disclaimer in the documentation and/or other materials provided
  with the distribution.

* The names of the contributors may not be used to endorse or
  promote products derived from this software without specific
  prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


class LazyString:
    """
    The `LazyString` class provides the ability to declare
    translations without app context. The translations don't
    happen until they are actually needed.
    """

    _func: Callable[..., str]
    _args: Any
    _kwargs: Any

    def __init__(self, func: Callable[..., str], *args: Any, **kwargs: Any) -> None:
        """
        Construct a Lazy String.

        Arguments:
            func: The function to use for the string.
            args: Arguments for the function.
            kwargs: Kwargs for the function.
        """
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def __getattr__(self, attr: Any) -> str:
        if attr == "__setstate__":
            raise AttributeError(attr)
        string = str(self)
        if hasattr(string, attr):
            return getattr(string, attr)
        raise AttributeError(attr)

    @override
    def __repr__(self) -> str:
        return f"l'{str(self)}'"

    @override
    def __str__(self) -> str:
        return str(self._func(*self._args, **self._kwargs))

    def __len__(self) -> int:
        return len(str(self))

    def __getitem__(self, key: Any) -> str:
        return str(self)[key]

    def __iter__(self) -> Iterator[str]:
        return iter(str(self))

    def __contains__(self, item: str) -> bool:
        return item in str(self)

    def __add__(self, other: str) -> str:
        return str(self) + other

    def __radd__(self, other: str) -> str:
        return other + str(self)

    def __mul__(self, other: Any) -> str:
        return str(self) * other

    def __rmul__(self, other: Any) -> str:
        return other * str(self)

    def __lt__(self, other: str) -> bool:
        return str(self) < other

    def __le__(self, other: str) -> bool:
        return str(self) <= other

    @override
    def __eq__(self, other: Any) -> bool:
        return str(self) == other

    @override
    def __ne__(self, other: Any) -> bool:
        return str(self) != other

    def __gt__(self, other: str) -> bool:
        return str(self) > other

    def __ge__(self, other: str) -> bool:
        return str(self) >= other

    def __html__(self) -> str:
        return str(self)

    @override
    def __hash__(self) -> int:
        return hash(str(self))

    def __mod__(self, other: str) -> str:
        return str(self) % other

    def __rmod__(self, other: str) -> str:
        return other + str(self)
