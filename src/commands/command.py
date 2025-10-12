"""
Base command class
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
from logger import Logger
from abc import ABC, abstractmethod

class Command(ABC):

    def __init__(self):
        """ Constructor method """
        self.logger = Logger.get_instance('Command')

    @abstractmethod
    def run(self):
        """ Run an operation """
        pass

    @abstractmethod
    def rollback(self):
        """ Revert the effects of the operation executed by the run method"""
        pass