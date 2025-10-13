"""
Handler: create order
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
import config
import requests
from logger import Logger
from handlers.handler import Handler
from order_saga_state import OrderSagaState

class CreateOrderHandler(Handler):
    """ Handle order creation. Delete order in case of failure. """

    def __init__(self, order_data):
        """ Constructor method """
        self.order_data = order_data
        self.order_id = 0
        super().__init__()

    def run(self):
        """Call StoreManager to create order"""
        try:
            # ATTENTION: Si vous roulez ce code dans Docker, n'utilisez pas localhost. Utilisez plutôt le hostname de votre API Gateway
            response = requests.post(f'{config.API_GATEWAY_URL}/store-manager-api/orders',
                json=self.order_data,
                headers={'Content-Type': 'application/json'}
            )
            if response.ok:
                data = response.json() 
                self.order_id = data['order_id'] if data else 0
                self.logger.debug("La création de la commande a réussi")
                return OrderSagaState.DECREASE_STOCK
            else:
                text = response.json() 
                self.logger.debug(f"Erreur {response.status_code} : {text}")
                return OrderSagaState.TERMINATE

        except Exception as e:
            self.logger.debug("La création de la commande a échoué : " + str(e))
            return OrderSagaState.TERMINATE
        
    def rollback(self):
        """Call StoreManager to delete order"""
        try:
            # ATTENTION: Si vous roulez ce code dans Docker, n'utilisez pas localhost. Utilisez plutôt le hostname de votre API Gateway
            response = requests.delete(f'{config.API_GATEWAY_URL}/store-manager-api/orders/{self.order_id}')
            if response.ok:
                data = response.json() 
                self.order_id = data['order_id'] if data else 0
                self.logger.debug("La supression de la commande a réussi")
                return OrderSagaState.TERMINATE
            else:
                text = response.json() 
                self.logger.debug(f"Erreur {response.status_code} : {text}")
                return OrderSagaState.TERMINATE

        except Exception as e:
            self.logger.debug("La supression de la commande a échoué : " + str(e))
            return OrderSagaState.TERMINATE