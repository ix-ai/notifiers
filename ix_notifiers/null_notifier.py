#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Null """

import logging
from .core import Notifier

log = logging.getLogger(__package__)


def start(**kwargs):
    """ Returns an instance of NullNotifier """
    return NullNotifier(**kwargs)


class NullNotifier(Notifier):
    """ The NullNotifier class """

    def __init__(self, **kwargs):
        self.settings = {}
        super().__init__(**kwargs)
        log.debug("Initialized")
