"""Localization module."""
from importlib import import_module

import pluggy

from raesl import logger

pm = pluggy.PluginManager("raesl.doc")
hookspec = pluggy.HookspecMarker("raesl.doc")
hookimpl = pluggy.HookimplMarker("raesl.doc")


class Hookspecs:
    @hookspec(firstresult=True)
    def gettext(key: str):
        """Get text translation."""


pm.add_hookspecs(Hookspecs)


def _(key: str, hook: pluggy.PluginManager = pm.hook):
    """Gettext alike translation function."""
    return hook.gettext(key=key)


def list_locales():
    """List available locales."""
    from pathlib import Path

    here = Path(__file__).parent
    return list(
        p.stem for p in here.glob("*") if p.suffix == ".py" and p.name not in {"__init__.py"}
    )


def register_locale(locale: str = "en"):
    """Register a locale. Existing locales are re-registered."""
    if pm.has_plugin(locale):
        pm.unregister(name=locale)
        logger.debug("Unregistered locale: {}.".format(locale))

    mod = import_module("raesl.doc.locales.{}".format(locale))
    pm.register(mod, name=locale)
    logger.debug("Registered locale: {}.".format(locale))


def register_default_locale(locale: str = "en"):
    """Register default locale if no other locale is set."""
    logger.debug("Registering default locale '{}'...".format(locale))
    if not pm.get_plugins():
        register_locale(locale)
    else:
        logger.debug("Default locale already registered.")
