class InventoryService:
    def check_stock(self, 
                    product_code: str, 
                    quantity: int) -> bool:
        raise NotImplementedError
