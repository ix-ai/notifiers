#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Telegram """

import logging
import time
import telegram
from .core import Notifier

log = logging.getLogger(__package__)


def start(**kwargs):
    """ Returns an instance of the TelegramNotifier """
    return TelegramNotifier(**kwargs)


class TelegramNotifier(Notifier):
    """ The TelegramNotifier class """
    params = {
        'token': {
            'mandatory': True,
            'redact': True,
            'type': 'string',
        },
        'chat_id': {
            'mandatory': True,
            'type': 'string',
        },
        'parse_mode': {
            'default': 'Markdown',
            'type': 'string,'
        },
        'max_retries': {
            'default': 0,
            'type': 'integer',
        },
        'always_succeed': {
            'default': False,
            'type': 'boolean',
        },
    }

    def __init__(self, **kwargs):
        self.settings = {}
        super().__init__(**kwargs)
        self.notifier = telegram.Bot(token=self.settings['token'])
        log.debug(self.redact(f"Initialized with {self.settings}"))

    def send(self, **kwargs):
        """ sends a notification to telegram """

        # Allow per message override of parse_mode
        parse_mode = kwargs.get('parse_mode', self.settings['parse_mode'])

        retry = True
        success = True
        tries = 0

        # Telegram has a maximum message limit of 4096 characters
        if len(kwargs['message']) > 4096:
            success = False
            retry = False
            log.error(f"The Telegram message is too long ({len(kwargs['message'])} > 4096). Not sending.")

        while retry is True and (
            (self.settings['max_retries'] == 0) or (tries < self.settings['max_retries'])
        ):
            tries += 1
            try:
                self.notifier.sendMessage(
                    chat_id=self.settings['chat_id'],
                    text=kwargs['message'],
                    parse_mode=parse_mode,
                    disable_web_page_preview=True,
                )
                log.info("Sent message to telegram.")
                log.debug(f"Message: {kwargs['message']}")
                retry = False
            except (TimeoutError, telegram.error.TimedOut, telegram.error.RetryAfter) as error:
                try:
                    retry_after = 0.5 + int(error.retry_after)
                except AttributeError:
                    retry_after = 2
                    if (self.settings['max_retries'] == 0) or (tries < self.settings['max_retries']):
                        log.warning(f'Exception caught - retrying in {retry_after}s: {error}')
                        time.sleep(retry_after)
                    else:
                        log.warning(f'Exception caught: {error}')
                        success = False
            except (telegram.error.Unauthorized) as error:
                log.error(self.redact(f'{error} - check TELEGRAM_TOKEN - skipping retries.'))
                retry = False
                success = False
            except (telegram.error.BadRequest) as error:
                exit_message = ''
                if str(error) == 'Chat not found':
                    exit_message = 'Check TELEGRAM_CHAT_ID - '
                exit_message = self.redact(f'{exit_message}Skipping retries. The exception: {error}')
                log.error(exit_message)
                retry = False
                success = False
            except Exception as error:
                log.error(self.redact(f"Failed to send message! Exception: {error}"))
                retry = False
                success = False
        if self.settings['always_succeed']:
            success = True
        return success
