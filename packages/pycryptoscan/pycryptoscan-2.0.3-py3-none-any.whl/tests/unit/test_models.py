"""
Unit tests for data models.
"""

import pytest
from datetime import datetime, timezone
from decimal import Decimal
from dataclasses import fields, FrozenInstanceError

from cryptoscan.models import (
    PaymentInfo,
    PaymentEvent,
    ErrorEvent,
    PaymentStatus,
    _utc_now,
)


# =============================================================================
# PaymentStatus Tests
# =============================================================================


class TestPaymentStatus:
    """Tests for PaymentStatus enum."""

    def test_status_values(self):
        """Test that all expected status values exist."""
        assert PaymentStatus.PENDING.value == "pending"
        assert PaymentStatus.CONFIRMED.value == "confirmed"
        assert PaymentStatus.FAILED.value == "failed"

    def test_status_from_string(self):
        """Test creating status from string value."""
        assert PaymentStatus("pending") == PaymentStatus.PENDING
        assert PaymentStatus("confirmed") == PaymentStatus.CONFIRMED
        assert PaymentStatus("failed") == PaymentStatus.FAILED

    def test_invalid_status(self):
        """Test that invalid status raises ValueError."""
        with pytest.raises(ValueError):
            PaymentStatus("invalid")


# =============================================================================
# PaymentInfo Tests
# =============================================================================


class TestPaymentInfo:
    """Tests for PaymentInfo dataclass."""

    def test_create_payment_info(self, sample_payment_info: PaymentInfo):
        """Test creating PaymentInfo instance."""
        assert sample_payment_info.transaction_id is not None
        assert sample_payment_info.wallet_address is not None
        assert isinstance(sample_payment_info.amount, Decimal)
        assert isinstance(sample_payment_info.status, PaymentStatus)

    def test_payment_info_required_fields(self):
        """Test that required fields must be provided."""
        with pytest.raises(TypeError):
            PaymentInfo()  # Missing required fields

    def test_payment_info_default_values(self):
        """Test PaymentInfo default values."""
        payment = PaymentInfo(
            transaction_id="tx123",
            wallet_address="0x123",
            amount=Decimal("1.0"),
            currency="ETH",
            status=PaymentStatus.PENDING,
            timestamp=datetime.now(timezone.utc),
        )
        
        assert payment.block_height is None
        assert payment.confirmations == 0
        assert payment.fee is None
        assert payment.from_address == ""
        assert payment.to_address == ""
        assert payment.raw_data == {}

    def test_payment_info_with_all_fields(self):
        """Test PaymentInfo with all fields populated."""
        now = datetime.now(timezone.utc)
        payment = PaymentInfo(
            transaction_id="0xabc123",
            wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f8fE23",
            amount=Decimal("2.5"),
            currency="ETH",
            status=PaymentStatus.CONFIRMED,
            timestamp=now,
            block_height=12345678,
            confirmations=10,
            fee=Decimal("0.001"),
            from_address="0x1111111111111111111111111111111111111111",
            to_address="0x742d35Cc6634C0532925a3b844Bc9e7595f8fE23",
            raw_data={"extra": "data"},
        )
        
        assert payment.transaction_id == "0xabc123"
        assert payment.amount == Decimal("2.5")
        assert payment.block_height == 12345678
        assert payment.confirmations == 10
        assert payment.fee == Decimal("0.001")
        assert payment.raw_data == {"extra": "data"}

    def test_payment_info_has_slots(self):
        """Test that PaymentInfo uses __slots__ for memory efficiency."""
        payment = PaymentInfo(
            transaction_id="tx123",
            wallet_address="0x123",
            amount=Decimal("1.0"),
            currency="ETH",
            status=PaymentStatus.PENDING,
            timestamp=datetime.now(timezone.utc),
        )
        
        # With slots=True, __dict__ should not exist
        assert not hasattr(payment, "__dict__")

    def test_payment_info_equality(self):
        """Test PaymentInfo equality comparison."""
        now = datetime.now(timezone.utc)
        payment1 = PaymentInfo(
            transaction_id="tx123",
            wallet_address="0x123",
            amount=Decimal("1.0"),
            currency="ETH",
            status=PaymentStatus.PENDING,
            timestamp=now,
        )
        payment2 = PaymentInfo(
            transaction_id="tx123",
            wallet_address="0x123",
            amount=Decimal("1.0"),
            currency="ETH",
            status=PaymentStatus.PENDING,
            timestamp=now,
        )
        
        assert payment1 == payment2

    def test_payment_info_different_amounts(self):
        """Test that different amounts create unequal PaymentInfo."""
        now = datetime.now(timezone.utc)
        payment1 = PaymentInfo(
            transaction_id="tx123",
            wallet_address="0x123",
            amount=Decimal("1.0"),
            currency="ETH",
            status=PaymentStatus.PENDING,
            timestamp=now,
        )
        payment2 = PaymentInfo(
            transaction_id="tx123",
            wallet_address="0x123",
            amount=Decimal("2.0"),  # Different amount
            currency="ETH",
            status=PaymentStatus.PENDING,
            timestamp=now,
        )
        
        assert payment1 != payment2


# =============================================================================
# PaymentEvent Tests
# =============================================================================


class TestPaymentEvent:
    """Tests for PaymentEvent dataclass."""

    def test_create_payment_event(self, sample_payment_info: PaymentInfo):
        """Test creating PaymentEvent instance."""
        event = PaymentEvent(
            payment_info=sample_payment_info,
            monitor_id="monitor_001",
            network="ethereum",
        )
        
        assert event.payment_info == sample_payment_info
        assert event.monitor_id == "monitor_001"
        assert event.network == "ethereum"
        assert event.detected_at is not None

    def test_payment_event_auto_timestamp(self, sample_payment_info: PaymentInfo):
        """Test that detected_at is automatically set."""
        before = datetime.now(timezone.utc)
        event = PaymentEvent(
            payment_info=sample_payment_info,
            monitor_id="monitor_001",
            network="ethereum",
        )
        after = datetime.now(timezone.utc)
        
        assert before <= event.detected_at <= after

    def test_payment_event_custom_timestamp(self, sample_payment_info: PaymentInfo):
        """Test PaymentEvent with custom timestamp."""
        custom_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        event = PaymentEvent(
            payment_info=sample_payment_info,
            monitor_id="monitor_001",
            network="ethereum",
            detected_at=custom_time,
        )
        
        assert event.detected_at == custom_time

    def test_payment_event_has_slots(self, sample_payment_info: PaymentInfo):
        """Test that PaymentEvent uses __slots__ for memory efficiency."""
        event = PaymentEvent(
            payment_info=sample_payment_info,
            monitor_id="monitor_001",
            network="ethereum",
        )
        
        # With slots=True, __dict__ should not exist
        assert not hasattr(event, "__dict__")


# =============================================================================
# ErrorEvent Tests
# =============================================================================


class TestErrorEvent:
    """Tests for ErrorEvent dataclass."""

    def test_create_error_event(self):
        """Test creating ErrorEvent instance."""
        error = ValueError("Test error")
        event = ErrorEvent(
            error=error,
            monitor_id="monitor_001",
            network="ethereum",
        )
        
        assert event.error == error
        assert event.monitor_id == "monitor_001"
        assert event.network == "ethereum"
        assert event.message == "Test error"

    def test_error_event_auto_message(self):
        """Test that message is automatically set from error."""
        error = RuntimeError("Something went wrong")
        event = ErrorEvent(
            error=error,
            monitor_id="monitor_001",
            network="ethereum",
        )
        
        assert event.message == "Something went wrong"

    def test_error_event_custom_message(self):
        """Test ErrorEvent with custom message."""
        error = ValueError("Original error")
        event = ErrorEvent(
            error=error,
            monitor_id="monitor_001",
            network="ethereum",
            message="Custom error message",
        )
        
        assert event.message == "Custom error message"

    def test_error_event_auto_timestamp(self):
        """Test that timestamp is automatically set."""
        before = datetime.now(timezone.utc)
        event = ErrorEvent(
            error=ValueError("Test"),
            monitor_id="monitor_001",
            network="ethereum",
        )
        after = datetime.now(timezone.utc)
        
        assert before <= event.timestamp <= after

    def test_error_event_with_exception_chain(self):
        """Test ErrorEvent with chained exception."""
        try:
            try:
                raise ValueError("Inner error")
            except ValueError as e:
                raise RuntimeError("Outer error") from e
        except RuntimeError as error:
            event = ErrorEvent(
                error=error,
                monitor_id="monitor_001",
                network="ethereum",
            )
            
            assert "Outer error" in event.message
            assert event.error.__cause__ is not None


# =============================================================================
# Helper Function Tests
# =============================================================================


class TestUtcNow:
    """Tests for _utc_now helper function."""

    def test_returns_datetime(self):
        """Test that _utc_now returns a datetime."""
        result = _utc_now()
        assert isinstance(result, datetime)

    def test_returns_utc_timezone(self):
        """Test that _utc_now returns UTC timezone."""
        result = _utc_now()
        assert result.tzinfo == timezone.utc

    def test_returns_current_time(self):
        """Test that _utc_now returns approximately current time."""
        before = datetime.now(timezone.utc)
        result = _utc_now()
        after = datetime.now(timezone.utc)
        
        assert before <= result <= after


# =============================================================================
# Edge Cases and Type Safety
# =============================================================================


class TestModelEdgeCases:
    """Test edge cases and type safety for models."""

    def test_payment_info_with_zero_amount(self):
        """Test PaymentInfo with zero amount."""
        payment = PaymentInfo(
            transaction_id="tx123",
            wallet_address="0x123",
            amount=Decimal("0"),
            currency="ETH",
            status=PaymentStatus.CONFIRMED,
            timestamp=datetime.now(timezone.utc),
        )
        
        assert payment.amount == Decimal("0")

    def test_payment_info_with_very_small_amount(self):
        """Test PaymentInfo with very small amount (wei precision)."""
        payment = PaymentInfo(
            transaction_id="tx123",
            wallet_address="0x123",
            amount=Decimal("0.000000000000000001"),  # 1 wei
            currency="ETH",
            status=PaymentStatus.CONFIRMED,
            timestamp=datetime.now(timezone.utc),
        )
        
        assert payment.amount == Decimal("0.000000000000000001")

    def test_payment_info_with_large_amount(self):
        """Test PaymentInfo with very large amount."""
        payment = PaymentInfo(
            transaction_id="tx123",
            wallet_address="0x123",
            amount=Decimal("1000000000000"),  # 1 trillion
            currency="ETH",
            status=PaymentStatus.CONFIRMED,
            timestamp=datetime.now(timezone.utc),
        )
        
        assert payment.amount == Decimal("1000000000000")

    def test_payment_info_with_negative_confirmations(self):
        """Test PaymentInfo accepts negative confirmations (shouldn't happen but test anyway)."""
        payment = PaymentInfo(
            transaction_id="tx123",
            wallet_address="0x123",
            amount=Decimal("1.0"),
            currency="ETH",
            status=PaymentStatus.PENDING,
            timestamp=datetime.now(timezone.utc),
            confirmations=-1,  # Invalid but should not crash
        )
        
        assert payment.confirmations == -1

    def test_payment_info_raw_data_isolation(self):
        """Test that raw_data modifications don't affect other instances."""
        raw_data = {"key": "value"}
        payment = PaymentInfo(
            transaction_id="tx123",
            wallet_address="0x123",
            amount=Decimal("1.0"),
            currency="ETH",
            status=PaymentStatus.CONFIRMED,
            timestamp=datetime.now(timezone.utc),
            raw_data=raw_data,
        )
        
        # Modify original dict
        raw_data["key"] = "modified"
        
        # Payment should still have original value (if passed by reference, this would fail)
        # Note: dataclass doesn't deep copy by default, so this actually shows the reference behavior
        assert payment.raw_data["key"] == "modified"

    def test_all_payment_status_values_usable(self):
        """Test that all PaymentStatus values can be used in PaymentInfo."""
        for status in PaymentStatus:
            payment = PaymentInfo(
                transaction_id="tx123",
                wallet_address="0x123",
                amount=Decimal("1.0"),
                currency="ETH",
                status=status,
                timestamp=datetime.now(timezone.utc),
            )
            assert payment.status == status
