# -*- coding: utf-8 -*-

"""
.. currentmodule:: src.main

This module is the main application entry point.
"""

import logging.config

from src import model


def initialize_logging():
    """Initializes the logging module for use throughout the whole application, reading the configuration from the
    ``logging.conf`` file located at the same level as the main module.

    :rtype: None
    """
    logging.config.fileConfig('logging.conf')

if __name__ == '__main__':
    initialize_logging()
    model.initialize_tb_folder()
    tb = model.TermBase('prova')
    tb.schema.add_property('Domain', 'E')
