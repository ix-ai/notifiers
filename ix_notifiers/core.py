#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" notification core """

import logging
import importlib

log = logging.getLogger(__package__)


class IxNotifiers():
    """ the IxNotifiers class """

    notifiers = [
        'telegram',
        'gotify',
        'null',
    ]

    registered = {}

    def register(self, notifier, **kwargs):
        """ registers a notifier """
        log.debug(f'Registering {notifier}')
        for n in self.notifiers:
            if n == notifier:
                instance = importlib.import_module(f'ix_notifiers.{notifier}_notifier')
                # Strips the prefix from kwargs, if set
                settings = {}
                for k, v in kwargs.items():
                    settings.update({k.replace(f'{notifier}_', ''): v})
                self.registered.update({notifier: instance.start(**settings)})
                log.debug(f'Registered {notifier}')

    def notify(self, **kwargs) -> bool:
        """
        dispatches a notification to all the registered notifiers

        param: kwargs get passed to the `send()` method of the notifier
        return: True if at least one notification channel was successful, False otherwise
        """
        success = False
        for notifier in self.registered:
            log.debug(f'Sending notification to {notifier}')
            if self.registered[notifier].send(**kwargs) is True:
                success = True
        return success


class Notifier():
    """ The base class for all notifiers """

    settings = {}
    params = {}

    def __init__(self, **kwargs):
        # go through self.params and check against kwargs
        for param, setting in self.params.items():
            if setting.get('mandatory') and not kwargs.get(f'{param}'):
                raise ValueError(f'{param} is mandatory')
            self.settings[param] = kwargs.get(f'{param}', self.params[param].get('default'))

            if (setting['type'] == 'boolean') and not isinstance(self.settings[param], bool):
                raise ValueError(f'`{param}` is not bool but {type(self.settings[param])}')
            if (setting['type'] == 'integer') and not isinstance(self.settings[param], int):
                raise ValueError(f'`{param}` is not int but {type(self.settings[param])}')
            if (setting['type'] == 'string') and not isinstance(self.settings[param], str):
                raise ValueError(f'`{param}` is not str but {type(self.settings[param])}')

    def key_to_title(self, key: str) -> str:
        """ converts a configuration key in form 'a_is_b' to a title in form 'A Is B ' """
        parsed = ""
        keys = key.split('_')
        for k in keys:
            parsed += f'{k.capitalize()} '
        return parsed[:-1]

    def send(self, **kwargs):
        """
        logs the notification to info

        return: True
        """
        log.info(f"{self.redact(str(kwargs))}")
        return True

    def redact(self, message: str) -> str:
        """ based on self.params, it replaces sensitive information in message with a redacted string """
        for param, setting in self.params.items():
            if setting.get('redact') and self.settings.get(param):
                message = message.replace(self.settings.get(param), 'xxxREDACTEDxxx')
        return message
