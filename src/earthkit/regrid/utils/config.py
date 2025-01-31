# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import functools
import logging
import os
import warnings
from abc import ABCMeta
from abc import abstractmethod
from contextlib import contextmanager
from typing import Callable

import yaml

from earthkit.regrid import __version__ as VERSION
from earthkit.regrid.utils.html import css
from earthkit.regrid.utils.humanize import as_bytes
from earthkit.regrid.utils.humanize import as_percent
from earthkit.regrid.utils.humanize import as_seconds
from earthkit.regrid.utils.humanize import list_to_human

LOG = logging.getLogger(__name__)

OLD_CONFIG_FILE = os.path.expanduser("~/.earthkit_regrid/settings.yaml")
CONFIG_DIR = os.path.expanduser("~/.config/earthkit/regrid")
CONFIG_FILE_NAME = "config.yaml"
CONFIG_FILE_ENV_NAME = "CONFIG_FILE"
ENV_PREFIX = "EARTHKIT_REGRID_"


class Validator(metaclass=ABCMeta):
    @abstractmethod
    def check(self, value):
        pass

    #
    @abstractmethod
    def explain(self):
        pass

    # @staticmethod
    # def make(value):
    #     v = _validators.get(type(value), None)
    #     if v is not None:
    #         return v(value)
    #     else:
    #         raise TypeError(f"Cannot create Validator for type={type(value)}")


# class ValueValidator(Validator):
#     def __init__(self, value):
#         self.value = value

#     def check(self, value):
#         return value == self.value

#     def explain(self):
#         return f"Valid when = {self.value}."


class ValuesValidator(Validator):
    """Check if value is in a list of valid values"""

    def __init__(self, values):
        self.values = values

    def check(self, value):
        return value in self.values

    def explain(self):
        return f"Valid values: {list_to_human(self.values)}."


class ListValidator(Validator):
    """Check if a list of values is in a list of valid values"""

    def __init__(self, values):
        self.values = values

    def check(self, value):
        return value in self.values

    def explain(self):
        return f"Valid values: {list_to_human(self.values)}."


# _validators = {bool: ValueValidator, list: ValuesValidator}


class ConfigOption:
    def __init__(
        self,
        default,
        description,
        getter=None,
        none_ok=False,
        kind=None,
        docs_default=None,
        validator=None,
    ):
        self.default = default
        self.description = description
        self.getter = getter
        self.none_ok = none_ok
        self.kind = kind if kind is not None else type(default)
        self.docs_default = docs_default if docs_default is not None else self.default
        self.validator = validator

    def kind(self):
        return type(self.default)

    def save(self, name, value, f):
        for n in self.docs_description.split("\n"):
            print(f"# {n.strip()}", file=f)
        print(file=f)
        comment = yaml.dump({name: self.default}, default_flow_style=False)
        for n in comment.split("\n"):
            if n:
                print(f"# {n}", file=f)
        if value != self.default:
            print(file=f)
            yaml.dump({name: value}, f, default_flow_style=False)

    @property
    def docs_description(self):
        d = self.description
        t = ""
        if self.validator:
            t = self.validator.explain()

        return d.replace("{validator}", t)

    def validate(self, name, value):
        if self.validator is not None and not self.validator.check(value):
            raise ValueError(f"Config option '{name}' cannot be set to {value}. {self.validator.explain()}")


_ = ConfigOption


CONFIG_AND_HELP = {
    "user-cache-directory": _(
        os.path.join(os.path.expanduser("~"), ".cache", "earthkit-regrid"),
        """Cache directory used when ``cache-policy`` is ``user``.
        See :doc:`/guide/caching` for more information.""",
    ),
    "temporary-cache-directory-root": _(
        None,
        """Parent of the cache directory when ``cache-policy`` is ``temporary``.
        See :doc:`/guide/caching` for more information.""",
        getter="_as_str",
        none_ok=True,
    ),
    "temporary-directory-root": _(
        None,
        """Parent of the temporary directory when ``cache-policy`` is ``off``.
        See :doc:`/guide/caching` for more information.""",
        getter="_as_str",
        none_ok=True,
    ),
    "cache-policy": _(
        "user",
        """Caching policy. {validator}
        See :doc:`/guide/caching` for more information. """,
        validator=ValuesValidator(["off", "temporary", "user"]),
    ),
    "maximum-cache-size": _(
        "5GB",
        """Maximum disk space used by the earthkit-regrid cache (e.g.: 100G or 2T).
        Can be set to None.""",
        getter="_as_bytes",
        none_ok=True,
    ),
    "maximum-cache-disk-usage": _(
        None,
        """Disk usage threshold after which earthkit-regrid expires older cached
        entries (% of the full disk capacity). Can be set to None.
        See :ref:`caching` for more information.""",
        getter="_as_percent",
        none_ok=True,
    ),
    "url-download-timeout": _(
        "30s",
        """Timeout when downloading from an url.""",
        getter="_as_seconds",
    ),
    "check-out-of-date-urls": _(
        False,
        "Perform a HTTP request to check if the remote version of a cache file has changed",
    ),
    "download-out-of-date-urls": _(
        False,
        "Re-download URLs when the remote version of a cached file as been changed",
    ),
    "maximum-matrix-memory-cache-size": _(
        "500MB",
        """The maximum memory size of the in-memory matrix cache in bytes. Only used when ``matrix-memory-cache-policy`` is ``"largest"`` or ``"lru"``. Can be set to None.
        See :ref:`memory_cache` for more information.""",
        getter="_as_bytes",
        none_ok=True,
    ),
    "matrix-memory-cache-policy": _(
        "largest",
        """The matrix in-memory cache policy. {validator}
        See :ref:`memory_cache` for more information.""",
        validator=ValuesValidator(["off", "unlimited", "largest", "lru"]),
    ),
    "matrix-memory-cache-strict-mode": _(
        False,
        """Raise exception if the matrix cannot be fitted into the in-memory cache.  Only used when ``matrix-memory-cache-policy`` is ``"largest"`` or ``"lru"``.
        See :ref:`memory_cache` for more information.""",
    ),
    "local-matrix-directories": _(
        None,
        """Parent of the cache directory when ``cache-policy`` is ``temporary``.
        See :doc:`/guide/caching` for more information.""",
        getter="_as_str",
        none_ok=True,
    ),
    "remote-matrix-directories": _(
        None,
        """Parent of the cache directory when ``cache-policy`` is ``temporary``.
        See :doc:`/guide/caching` for more information.""",
        getter="_as_str",
        none_ok=True,
    ),
    # "backend-policy": _(
    #     "all",
    #     """The interpolation backend policy. {validator}
    #     See :ref:`backend` for more information.""",
    #     validator=ListValidator(["local_matrix", "matrix", "mir", "all"]),
    # ),
    "backend-order": _(
        None,
        """The interpolation backend order. {validator}
        See :ref:`backend` for more information.""",
        getter="_as_list",
        none_ok=True,
    ),
}


NONE = object()
DEFAULTS = {}
for k, v in CONFIG_AND_HELP.items():
    DEFAULTS[k] = v.default


@contextmanager
def new_config(s):
    """Context manager to create new config"""
    CONFIG._stack.append(s)
    CONFIG._notify()
    try:
        yield None
    finally:
        CONFIG._stack.pop()
        CONFIG._notify()


def forward(func):
    @functools.wraps(func)
    def wrapped(self, *args, **kwargs):
        if self._stack:
            return func(self._stack[-1], *args, **kwargs)
        return func(self, *args, **kwargs)

    return wrapped


def save_config(path, config):
    LOG.debug("Saving config")
    from filelock import FileLock

    lock = path + ".lock"
    with FileLock(lock):
        with open(path, "w") as f:
            print("# This file is automatically generated", file=f)
            print(file=f)

            for k, v in sorted(config.items()):
                h = CONFIG_AND_HELP.get(k)
                if h:
                    print(file=f)
                    print("#", "-" * 76, file=f)
                    h.save(k, v, f)

            print(file=f)
            print("#", "-" * 76, file=f)
            print("# Version of earthkit-regrid", file=f)
            print(file=f)
            yaml.dump({"version": VERSION}, f, default_flow_style=False)
            print(file=f)
    try:
        os.unlink(lock)
    except OSError:
        pass


def env_var_name(name):
    return ENV_PREFIX + name.upper().replace("-", "_")


class Config:
    _auto_save_config = True
    _notify_enabled = True

    def __init__(self, config_yaml: str, defaults: dict, callbacks=[]):
        self._defaults = defaults
        self._config = dict(**defaults)
        self._callbacks = [c for c in callbacks]
        self._config_yaml = config_yaml
        self._pytest = None
        self._stack = []

    @forward
    def get(self, name: str, default=NONE):
        """[summary]

        Parameters
        ----------
            name: str
                [description]
            default: [type]
                [description]. Defaults to NONE.

        Returns
        -------
            [type]: [description]
        """
        if name not in CONFIG_AND_HELP:
            raise KeyError("No config name '%s'" % (name,))

        config_item = CONFIG_AND_HELP[name]

        getter, none_ok = (
            config_item.getter,
            config_item.none_ok,
        )
        if getter is None:
            getter = lambda name, value, none_ok: value  # noqa: E731
        else:
            getter = getattr(self, getter)

        st, value, _ = self._env(name)
        if not st:
            if default is NONE:
                value = self._config[name]
            else:
                value = self._config.get(name, default)

        return getter(name, value, none_ok)

    @forward
    def set(self, *args, **kwargs):
        """[summary]

        Parameters
        ----------
            name: str
                [description]
            value: [type]
                [description]
        """
        if len(args) == 0:
            assert len(kwargs) > 0
            for k, v in kwargs.items():
                self._set(k.replace("_", "-"), v)
            self._changed()
        else:
            if len(args) == 1 and isinstance(args[0], dict):
                for k, v in args[0].items():
                    self._set(k, v)
            else:
                self._set(*args, **kwargs)
        self._changed()

    def _set(self, name: str, *args, **kwargs):
        """[summary]

        Parameters
        ----------
            name: str
                [description]
            value: [type]
                [description]
        """
        if name not in CONFIG_AND_HELP:
            raise KeyError("No config option '%s'" % (name,))

        if self._has_env(name):
            msg = (
                f"Config option '{name}' is also set by environment variable '{env_var_name(name)}'."
                "The environment variable takes precedence and its value is returned when calling get()."
            )
            if self._auto_save_config:
                msg += " Still, the value set here will be saved to the config file."
            warnings.warn(msg)

        config_item = CONFIG_AND_HELP[name]

        klass = config_item.kind

        if klass in (bool, int, float, str):
            # TODO: Proper exceptions
            assert len(args) == 1
            assert len(kwargs) == 0
            value = args[0]
            value = klass(value)

        if klass is list:
            assert len(args) > 0
            assert len(kwargs) == 0
            value = list(args)
            if len(args) == 1 and isinstance(args[0], list):
                value = args[0]

        if klass is dict:
            assert len(args) <= 1
            if len(args) == 0:
                assert len(kwargs) > 0
                value = kwargs

            if len(args) == 1:
                assert len(kwargs) == 0
                value = args[0]

        getter, none_ok = (
            config_item.getter,
            config_item.none_ok,
        )
        if getter is not None:
            assert len(args) == 1
            assert len(kwargs) == 0
            value = args[0]
            # Check if value is properly formatted for getter
            getattr(self, getter)(name, value, none_ok)
        else:
            if not isinstance(value, klass):
                raise TypeError("Config option '%s' must be of type '%s'" % (name, klass))

        config_item.validate(name, value)
        self._config[name] = value

        LOG.debug(f"_set {name}={value} stack_size={len(self._stack)}")

    @forward
    def reset(self, name: str = None):
        """Reset config to default values.

        Parameters
        ----------
            name: str, optional
                The name of the config option to reset to default. If it
                does not have a default, it is removed. If `None` is passed, all config options are
                reset to their default values. Defaults to None.
        """
        if name is None:
            self._config = dict(**DEFAULTS)
        else:
            if name not in DEFAULTS:
                raise KeyError("No config option name '%s'" % (name,))

            self._config.pop(name, None)
            if name in DEFAULTS:
                if self._has_env(name):
                    msg = (
                        f"Config option '{name}' is also set by environment variable '{env_var_name(name)}'."
                        "The environment variable takes precedence and its value is returned when calling get()."
                    )
                    if self._auto_save_config:
                        msg += " Still, the value reset here will be saved to the config file."
                    warnings.warn(msg)
                self._config[name] = DEFAULTS[name]
        self._changed()

    @forward
    def __repr__(self):
        r = []
        env = self.env()
        for k, v in sorted(self._config.items()):
            config = CONFIG_AND_HELP.get(k, None)
            default = config.default if config else ""
            if k in env:
                r.append(f"{k}: ({env[k][0]}={env[k][1]}, {v}, {default})")
            else:
                r.append(f"{k}: ({v}, {default})")
        return "\n".join(r)

    @forward
    def _repr_html_(self):
        html = [css("table")]
        html.append("<table class='ek'>")

        env = self.env()
        columns = ["Name", "Value", "Default"]
        html.append("<tr><th>%s</th></tr>" % ("</th><th>".join(columns)))

        for k, v in sorted(self._config.items()):
            config = CONFIG_AND_HELP.get(k, None)
            default = config.default if config else ""
            if k in env:
                html.append(
                    "<tr><td>%s</td><td>%s=%r<br>(%r)</td><td>%r</td></tr>"
                    % (k, env[k][0], env[k][1], v, default)
                )
            else:
                html.append("<tr><td>%s</td><td>%r</td><td>%r</td></tr>" % (k, v, default))

        html.append("</table>")
        return "".join(html)

    @forward
    def dump(self):
        for k, v in sorted(self._config.items()):
            yield ((k, v, CONFIG_AND_HELP.get(k)))

    def _changed(self):
        if self._auto_save_config:
            self._save()
        self._notify()

    def _notify(self):
        if self._notify_enabled:
            for cb in self._callbacks:
                cb()

    def on_change(self, callback: Callable[[], None]):
        self._callbacks.append(callback)

    def _save(self):
        if self._config_yaml is None:
            return

        try:
            save_config(self._config_yaml, self._config)
        except Exception:
            LOG.error(
                "Cannot save earthkit-regrid config (%s)",
                self._config_yaml,
                exc_info=True,
            )

    @forward
    def save_as(self, path):
        try:
            save_config(path, self._config)
        except Exception:
            LOG.error(
                f"Cannot save earthkit-regrid config ({path})",
                exc_info=True,
            )

    def _as_bytes(self, name, value, none_ok):
        return as_bytes(value, name=name, none_ok=none_ok)

    def _as_percent(self, name, value, none_ok):
        return as_percent(value, name=name, none_ok=none_ok)

    def _as_seconds(self, name, value, none_ok):
        return as_seconds(value, name=name, none_ok=none_ok)

    def _as_str(self, name, value, none_ok):
        if value is None and none_ok:
            return None
        return str(value)

    def _as_int(self, name, value, none_ok):
        if value is None and none_ok:
            return None
        if isinstance(value, str):
            value = value.replace('"', "").replace("'", "").strip()
        return int(value)

    def _as_list(self, name, value, none_ok):
        if value is None and none_ok:
            return []
        if isinstance(value, str):
            value = value.replace('"', "").replace("'", "").strip()
            return value.split(",")
        return list(value)

    @forward
    def temporary(self, *args, config_yaml=None, **kwargs):
        tmp = Config(config_yaml, self._config)
        # until the tmp object is at the top of the stack we do not want
        # notify the observers
        if len(args) > 0 or len(kwargs) > 0:
            # tmp does not have any callbacks so it will not broadcast the changes
            tmp.set(*args, **kwargs)
        tmp._callbacks = self._callbacks
        return new_config(tmp)

    @property
    def autosave(self):
        return Config._auto_save_config

    @autosave.setter
    def autosave(self, v):
        Config._auto_save_config = v

    def env(self):
        r = {}
        for k in sorted(self._config.keys()):
            st, value, name = self._env(k)
            if st:
                r[k] = (name, value)
        return r

    @staticmethod
    def _has_env(name):
        return env_var_name(name) in os.environ

    @staticmethod
    def _env(name):
        name = env_var_name(name)
        if name in os.environ:
            return (True, os.environ.get(name), name)
        return (False, None, None)


# TODO: remove this function when the old config (aka settings) is not used anymore
def _migrate_old_config(config_file):
    old_config_file = os.path.expanduser(OLD_CONFIG_FILE)
    if os.path.exists(old_config_file):
        config = dict(**DEFAULTS)
        try:
            with open(old_config_file) as f:
                s = yaml.load(f, Loader=yaml.SafeLoader)
                if not isinstance(s, dict):
                    return False

                config.update(s)
                save_config(config_file, config)
                return True
        except Exception:
            LOG.error(
                f"Cannot migrate old settings to earthkit-regrid config file={config_file}",
                exc_info=True,
            )
    return False


def _init_config_file():
    config_file = None

    name = env_var_name(CONFIG_FILE_ENV_NAME)
    if name in os.environ:
        config_file = os.environ[name]
    if not config_file:
        config_file = os.path.expanduser(os.path.join(CONFIG_DIR, CONFIG_FILE_NAME))

    if config_file is None:
        LOG.error("Cannot construct earthkit-regrid config file path")
        return None

    try:
        config_dir = os.path.dirname(config_file)
        if not os.path.exists(config_dir):
            ori_mask = os.umask(0o077)
            os.makedirs(config_dir, 0o700)
            os.umask(ori_mask)
    except Exception:
        LOG.error(
            f"Cannot create earthkit-regrid config directory={config_dir}",
            exc_info=True,
        )

    if os.path.exists(config_dir):
        try:
            if not os.path.exists(config_file):
                if not _migrate_old_config(config_file):
                    save_config(config_file, DEFAULTS)
        except Exception:
            LOG.error(
                f"Cannot save settings to earthkit-regrid config file={config_file}",
                exc_info=True,
            )

    return config_file


def _init_config(config_yaml):
    save = False
    config = dict(**DEFAULTS)
    try:
        with open(config_yaml) as f:
            s = yaml.load(f, Loader=yaml.SafeLoader)
            if not isinstance(s, dict):
                s = {}

            config.update(s)

        # if s != config:
        #     save = True

        if config.get("version") < VERSION:
            save = True

    except Exception:
        LOG.error(
            "Cannot load earthkit-regrid config (%s), reverting to defaults",
            config_yaml,
            exc_info=True,
        )

    return config, save


save = False
config_yaml = _init_config_file()
config, save = _init_config(config_yaml)

CONFIG = Config(config_yaml, config)
if save:
    CONFIG._save()
