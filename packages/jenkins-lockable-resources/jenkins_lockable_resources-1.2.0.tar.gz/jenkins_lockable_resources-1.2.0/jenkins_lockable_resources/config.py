#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CLI configuration utils
"""

import os
import collections

import yaml


class Config(dict):
    def __init__(self, *args, policy="overwrite"):
        self._policy = policy
        super().__init__(*args)

    def update(self, d):
        if not isinstance(d, dict):
            raise TypeError("Expected a dictionary")
        for k, v in d.items():
            if k not in self:
                self[k] = v
                continue

            # Key already exists in the dictionary
            merge_into = self[k]
            if isinstance(merge_into, collections.abc.Mapping) and isinstance(
                v, collections.abc.Mapping
            ):
                if not isinstance(merge_into, Config):
                    self[k] = Config(merge_into, policy=self._policy)
                self[k].update(v)
                continue

            if isinstance(merge_into, (list, tuple)) and isinstance(v, (list, tuple)):
                self[k] = v
                continue

            if not isinstance(v, collections.abc.Mapping) and not isinstance(
                v, collections.abc.Sequence
            ):
                self[k] = v
                continue

            if type(merge_into) is type(v):
                self[k] = v
                continue

            # Non matching merge types
            if self._policy == "strict":
                raise TypeError("Value type missmatch")
            if self._policy != "overwrite":
                continue

            self[k] = v


class ConfigLoader:
    """
    Loader class to load configuration file

    Config file holds tool parameters divided into sections or sub sections for each command or sub command:

    File structure:

        [/etc/myconf.yml]

            commamd_1:
                parameter_1: 'Test'
                parameter_2: 4

                sub_command:
                    parameter_1: true

            commamd_2:
                parameter_1: false

        [myconf.yml]

            commamd_2:
                parameter_1: true
        ...

    ConfigLoader can load a configuration dictionnary for the whole file or for a specific root section path.

    Example:
        This will load only the configuration for the command_1 section:

        >>> loader = ConfigLoader(config_files=['/etc/myconf.yml', 'myconf.yml'])
        >>> loader.conf
        {'commamd_1': {'parameter_1': 'Test', 'parameter_2': 4, 'sub_command': {'parameter_1': True}, 'commamd_2':
        'parameter_1': True}}

    """

    def __init__(self, config_files, defaults=None):
        """
        Create a new ConfigLoader instance

        Args:
            section (str, optional): the root section for the parser. Defaults to None.
            defaults (dict, optional): the default config values. Defaults to {}.
        """
        self._config_files = config_files
        self._defaults = defaults or {}
        self._conf = {}

    def _iter_conf_files(self):
        for path in self._config_files:
            path = os.path.expanduser(path)
            if os.path.exists(path):
                yield path

    def load(self):
        conf = Config(self._defaults.copy())
        for path in self._iter_conf_files():
            with open(path, "r", encoding="utf-8") as f:
                c = yaml.safe_load(f)
            if c:
                conf.update(c)
        return conf

    @property
    def conf(self):
        if not self._conf:
            self._conf = self.load()
        return self._conf

    @property
    def click_settings(self):
        return {"default_map": self.conf}
