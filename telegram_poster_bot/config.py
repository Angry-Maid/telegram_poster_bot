# -*- coding: utf-8 -*-

"""
ds-feed-manager settings YAML parser
"""

import logging
import os

import yaml


class TelegramPosterConfig(object):
    """Object representing YAML settings as a dict-like object
    with values as fields.
    """

    def __init__(self):
        """Creates instance and loads settings both from local and
        global paths
        """
        settings_files = []
        project_path = os.path.dirname(__file__)
        project_settings_file = os.path.join(project_path, 'config.yaml')
        settings_files.append(project_settings_file)

        self.config = {}
        for sf in settings_files:
            try:
                self.update_from_file(sf)
            except Exception as e:
                logging.error(
                    u"Error while reading config file {0}: {1}".format(
                        sf,
                        unicode(e)
                    )
                )

    def update(self, dct):
        """Update settings from dict

        :param dct: dict
        """
        self.config.update(dct)

    def update_from_file(self, path):
        """Update settings from YAML file
        """
        with open(path, "r") as custom_config:
            self.config.update(
                yaml.load(custom_config.read())
            )

    def dump(self):
        """Dump settings to YAML string
        """
        return yaml.dump(self.config)

    def __getattr__(self, name):
        return self.config.get(name, None)

    def __repr__(self):
        return "<settings object>"


config = TelegramPosterConfig()
