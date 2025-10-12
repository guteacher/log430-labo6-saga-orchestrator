"""
Order saga controller
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
from commands.create_order_command import CreateOrderCommand
from commands.create_payment_command import CreatePaymentCommand
from commands.decrease_stock_command import DecreaseStockCommand
from controllers.controller import Controller
from order_saga_state import OrderSagaState

class OrderSagaController(Controller):

    def __init__(self):
        """ Constructor method """
        super().__init__()
        self.current_saga_state = OrderSagaState.CREATE_ORDER
    
    def run(self, request):
        """ Perform steps of order saga """
        payload = request.get_json() or {}
        order_data = {
            "user_id": payload.get('user_id'),
            "items": payload.get('items', [])
        }
        self.create_order_command = CreateOrderCommand(order_data)

        while self.current_saga_state is not OrderSagaState.TERMINATE:
            # TODO: vérifier TOUS les 6 états saga. Utilisez run() ou rollback() selon les besoins.
            if self.current_saga_state == OrderSagaState.CREATE_ORDER:
                self.current_saga_state = self.create_order_command.run()
            elif self.current_saga_state == OrderSagaState.DECREASE_STOCK:
                self.increase_stock_command = DecreaseStockCommand(order_data["items"])
                self.current_saga_state = self.increase_stock_command.run()
            else:
                self.is_error_occurred = True
                self.logger.debug(f"L'état saga n'est pas valide : {self.current_saga_state}")
                self.current_saga_state = OrderSagaState.TERMINATE

        return {
            "order_id": self.create_order_command.order_id,
            "status":  "Une erreur s'est produite lors de la création de la commande." if self.is_error_occurred else "OK"
        }



    
