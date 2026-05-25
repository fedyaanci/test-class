class PaymentGateway:
    def charge(self, 
               amount: float) -> dict:
        raise NotImplementedError
