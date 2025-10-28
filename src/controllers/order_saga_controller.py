"""
Order saga controller
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
from handlers.create_order_handler import CreateOrderHandler
from handlers.create_payment_handler import CreatePaymentHandler
from handlers.decrease_stock_handler import DecreaseStockHandler
from controllers.controller import Controller
from order_saga_state import OrderSagaState

class OrderSagaController(Controller):
    """ Manage states and transitions of an order saga """

    def __init__(self):
        """ Constructor method """
        super().__init__()
        self.current_saga_state = OrderSagaState.CREATING_ORDER
    
    def run(self, request):
        """ Perform steps of order saga """
        payload = request.get_json() or {}
        order_data = {
            "user_id": payload.get('user_id'),
            "items": payload.get('items', [])
        }
        self.create_order_handler = CreateOrderHandler(order_data)

        while self.current_saga_state is not OrderSagaState.COMPLETED:
            # TODO: vérifier TOUS les 6 états saga. Utilisez run() ou rollback() selon les besoins.
            if self.current_saga_state == OrderSagaState.CREATING_ORDER:
                self.current_saga_state = self.create_order_handler.run()
            elif self.current_saga_state == OrderSagaState.DECREASING_STOCK:
                self.increase_stock_handler = DecreaseStockHandler(order_data["items"])
                self.current_saga_state = self.increase_stock_handler.run()
            else:
                self.is_error_occurred = True
                self.logger.debug(f"L'état saga n'est pas valide : {self.current_saga_state}")
                self.current_saga_state = OrderSagaState.COMPLETED

        return {
            "order_id": self.create_order_handler.order_id,
            "status":  "Une erreur s'est produite lors de la création de la commande." if self.is_error_occurred else "OK"
        }



    
