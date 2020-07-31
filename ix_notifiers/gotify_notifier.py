#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Gotify """

import logging
from urllib.parse import urljoin
import requests
from .core import Notifier
from . import constants

log = logging.getLogger(__package__)


def start(**kwargs):
    """ Returns an instance of the GotifyNotifier """
    return GotifyNotifier(**kwargs)


class GotifyNotifier(Notifier):
    """ The GotifyNotifier class """
    params = {
        'token': {
            'mandatory': True,
            'redact': True,
        },
        'url': {
            'mandatory': True,
        },
        'content_type': {
            'default': 'text/markdown'
        },
        'default_priority': {
            'mandatory': False,
        },
    }

    def __init__(self, **kwargs):
        self.settings = {}
        super().__init__(**kwargs)
        self.settings['url'] = urljoin(self.settings['url'], '/message')
        log.debug(self.redact(f"Initialized with {self.settings}"))

    def send(self, **kwargs) -> bool:
        """
        sends the notification to gotify

        return: True on success otherwise False
        """

        success = True
        headers = {
            'X-Gotify-Key': self.settings['token'],
            'user-agent': f'{__package__} {constants.VERSION}.{constants.BUILD}',
        }
        # Allow per message override of content_type
        extras = {
            'client::display': {
                'contentType': kwargs.get('content_type', self.settings['content_type']),
            }
        }

        req_json = {
            'extras': extras,
        }
        try:
            req_json.update({'message': kwargs['message']})
        except KeyError:
            pass

        try:
            req_json.update({'title': kwargs['title']})
        except KeyError:
            pass

        try:
            req_json.update({'priority': int(self.settings['default_priority'])})
        except TypeError:
            log.warning(f"Default priority not understood: {kwargs['default_priority']}")
        except KeyError:
            pass

        try:
            req_json.update({'priority': int(kwargs['priority'])})
        except TypeError:
            log.warning(f"Notification priority not understood: {kwargs['priority']}")
        except KeyError:
            pass

        resp = None
        try:
            resp = requests.post(self.settings['url'], json=req_json, headers=headers)
        except requests.exceptions.RequestException as e:
            # Print exception if reqeuest fails
            log.warning(self.redact(f'Could not connect to the Gotify server. The error: {e}'))
            success = False
        except Exception as e:
            log.error(self.redact(f'Failed to send message! Exception: {e}'))
            success = False

        # Print request result if server returns http error code
        if resp is not None:
            if resp.status_code is not requests.codes.ok:  # pylint: disable=no-member
                log.warning(self.redact(f'Error sending message to Gotify: {bytes.decode(resp.content)}'))
                success = False
            else:
                log.info("Sent message to gotify")

        return success
