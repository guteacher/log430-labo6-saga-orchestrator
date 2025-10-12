"""
Command: create payment transaction
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
import requests
from logger import Logger
from commands.command import Command
from order_saga_state import OrderSagaState

class CreatePaymentCommand(Command):

    def __init__(self, order_id, order_data):
        """ Constructor method """
        self.order_id = order_id
        self.order_data = order_data
        self.total_amount = 0
        super().__init__()

    def run(self):
        """Call payment microservice to generate payment transaction"""
        try:
            # TODO: effectuer une requête à /orders pour obtenir le total_amount de la commande (que sera utilisé pour démander la transaction de paiement)
            """
            GET my-api-gateway-address/order/{id} ...
            """

            # TODO: effectuer une requête à /payments pour créer une transaction de paiement
            """
            POST my-api-gateway-address/payments ...
            json={ voir collection Postman pour en savoir plus ... }
            """
            response_ok = True
            if response_ok:
                self.logger.debug("La création d'une transaction de paiement a réussi")
                return OrderSagaState.TERMINATE
            else:
                self.logger.debug(f"Erreur : {response_ok}")
                return OrderSagaState.INCREASE_STOCK

        except Exception as e:
            self.logger.debug("La création d'une transaction de paiement a échoué : " + str(e))
            return OrderSagaState.INCREASE_STOCK
        
    def rollback(self):
        """Call payment microservice to delete payment transaction"""
        # ATTENTION: Nous pourrions utiliser cette méthode si nous avions des étapes supplémentaires, mais ce n'est pas le cas actuellement, elle restera donc INUTILISÉE.
        self.logger.debug("La suppression d'une transaction de paiement a réussi")
        return OrderSagaState.INCREASE_STOCK