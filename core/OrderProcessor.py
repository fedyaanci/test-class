from interface.InventoryService import InventoryService
from interface.PaymentGateway import PaymentGateway

class OrderProcessor:
    def __init__(self, 
                 payment: PaymentGateway, 
                 inventory: InventoryService):
        self._payment = payment
        self._inventory = inventory
        self._orders: dict = {}
        self._daily_limit: int = 50

    @property
    def orders(self) -> dict:
        return self._orders

    @property
    def daily_limit(self) -> int:
        return self._daily_limit
    
    @orders.setter
    def orders(self, 
               value: dict):
        if not isinstance(value, dict):
            raise TypeError("Orders must be a dictionary")
        self._orders = value

    @daily_limit.setter
    def daily_limit(self, 
                    value: int):
        if value < 0:
            raise ValueError("Limit cannot be negative")
        self._daily_limit = value

    def process(self, 
                order_id: str, 
                product_code: str, 
                quantity: int, 
                amount: float) -> str:
        
        if len(self._orders) >= self._daily_limit:
            raise RuntimeError("Daily limit reached")
        
        if not self._inventory.check_stock(product_code, quantity):
            raise ValueError("Product out of stock")
        
        resp = self._payment.charge(amount)

        self._orders[order_id] = "confirmed" if resp.get("ok") else "failed"

        return order_id

    def cancel(self, order_id: str) -> bool:  
        if (order_id in self._orders) and (self._orders[order_id] == "confirmed"):
            self._orders[order_id] = "cancelled"
            return True
        return False

    def update_limit(self,
                     new_limit: int) -> None:
        self.daily_limit = new_limit

    def get_stats(self) -> dict:
        return {"total": len(self._orders), "limit": self._daily_limit}

    def get_order_status(self, 
                         order_id: str) -> str:
        return self._orders.get(order_id, "not_found")