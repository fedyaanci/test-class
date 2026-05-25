import pytest
from unittest.mock import MagicMock
from core.OrderProcessor import OrderProcessor
from interface.InventoryService import InventoryService
from interface.PaymentGateway import PaymentGateway

@pytest.fixture
def mock_payment():
    return MagicMock(spec=PaymentGateway)

@pytest.fixture
def mock_inventory():
    return MagicMock(spec=InventoryService)

@pytest.fixture
def processor(mock_payment, mock_inventory):
    return OrderProcessor(mock_payment, mock_inventory)

def test_process_success(processor, mock_payment, mock_inventory):
    mock_inventory.check_stock.return_value = True
    mock_payment.charge.return_value = {"ok": True}

    processor.process("заказ-01", "артикул-кроссы", 2, 1500)

    mock_inventory.check_stock.assert_called_once_with("артикул-кроссы", 2)
    mock_payment.charge.assert_called_once_with(1500)

# лимит превышен: внешние сервисы не трогали
def test_process_limit_reached(processor):
    processor.daily_limit = 1
    processor.orders["заказ-архивный"] = "confirmed"

    with pytest.raises(RuntimeError, match="Daily limit reached"):
        processor.process("заказ-02", "артикул-кепка", 1, 49)

    processor._inventory.check_stock.assert_not_called()
    processor._payment.charge.assert_not_called()

# нет товара: проверка контракта  и изоляция оплаты
def test_process_out_of_stock(processor, mock_inventory):
    mock_inventory.check_stock.return_value = False

    with pytest.raises(ValueError, match="Product out of stock"):
        processor.process("заказ-03", "артикул-ноутбук", 5, 250)

    processor._payment.charge.assert_not_called()

# оплата отклонена: проверяем вызов с правильными данными
def test_process_payment_failed(processor, mock_payment, mock_inventory):
    mock_inventory.check_stock.return_value = True
    mock_payment.charge.return_value = {"ok": False}

    processor.process("заказ-04", "артикул-смартфон", 1, 1200)

    mock_payment.charge.assert_called_once_with(1200)

# отмена подтверждённого заказа: только контракт
def test_cancel_success(processor):
    processor.orders["заказ-05"] = "confirmed"
    processor.cancel("заказ-05")

# отмена невалидного заказа: контракт и состояние не проверяем
def test_cancel_invalid(processor):
    processor.orders["заказ-06"] = "failed"
    processor.cancel("заказ-06")
    processor.cancel("заказ-пустышка")

# мутация свойств: проверяем только валидацию контракта сеттера
def test_daily_limit_valid_mutation(processor):
    processor.daily_limit = 100  

def test_daily_limit_invalid_mutation(processor):
    with pytest.raises(ValueError, match="cannot be negative"):
        processor.daily_limit = -10

def test_orders_valid_mutation(processor):
    processor.orders = {"заказ-на-тест": "confirmed"} 

def test_orders_invalid_mutation(processor):
    with pytest.raises(TypeError, match="must be a dictionary"):
        processor.orders = []

def test_update_limit(processor):
    processor.update_limit(75)

def test_get_stats_no_crash(processor):
    processor.orders = {"заказ-стат-1": "confirmed", "заказ-стат-2": "cancelled"}
    processor.get_stats()

def test_get_order_status_no_crash(processor):
    processor.orders["заказ-текущий"] = "confirmed"
    processor.get_order_status("заказ-текущий")
    processor.get_order_status("заказ-несуществующий")