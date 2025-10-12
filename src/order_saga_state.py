"""
Saga states
SPDX-License-Identifier: LGPL-3.0-or-later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

from enum import Enum

# TODO: Veuillez consulter le diagramme de machine à états pour en savoir plus
class OrderSagaState(Enum):
    CREATE_ORDER = 1
    DECREASE_STOCK = 2
    CREATE_PAYMENT = 3
    INCREASE_STOCK = 4
    DELETE_ORDER = 5
    TERMINATE = 6
