"""
Integration tests for payment monitors.
"""

import asyncio
import pytest
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock

from cryptoscan.config import UserConfig
from cryptoscan.factory import create_monitor, get_provider, get_supported_networks
from cryptoscan.exceptions import ValidationError
from cryptoscan.models import PaymentInfo, PaymentStatus, PaymentEvent, ErrorEvent
from cryptoscan.monitoring.monitor import PaymentMonitor
from cryptoscan.networks import NetworkConfig, register_network


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestCreateMonitor:
    """Tests for create_monitor factory function."""

    @pytest.fixture(autouse=True)
    def setup_networks(self):
        """Register test networks before each test."""
        from cryptoscan.networks import register_common_networks
        register_common_networks()

    def test_create_monitor_with_network_name(self, sample_eth_address: str):
        """Test creating monitor with network name string."""
        monitor = create_monitor(
            network="ethereum",
            wallet_address=sample_eth_address,
            expected_amount="1.0",
        )
        
        assert isinstance(monitor, PaymentMonitor)
        assert monitor.wallet_address == sample_eth_address
        assert monitor.expected_amount == Decimal("1.0")

    def test_create_monitor_with_network_config(self, ethereum_config: NetworkConfig, sample_eth_address: str):
        """Test creating monitor with NetworkConfig object."""
        monitor = create_monitor(
            network=ethereum_config,
            wallet_address=sample_eth_address,
            expected_amount="2.5",
        )
        
        assert isinstance(monitor, PaymentMonitor)
        assert monitor.expected_amount == Decimal("2.5")

    def test_create_monitor_with_custom_rpc(self, sample_eth_address: str):
        """Test creating monitor with custom RPC URL."""
        monitor = create_monitor(
            network="ethereum",
            wallet_address=sample_eth_address,
            expected_amount="1.0",
            rpc_url="https://custom-rpc.example.com",
        )
        
        assert monitor.provider.network_config.rpc_url == "https://custom-rpc.example.com"

    def test_create_monitor_with_websocket(self, sample_eth_address: str):
        """Test creating monitor with WebSocket URL."""
        monitor = create_monitor(
            network="ethereum",
            wallet_address=sample_eth_address,
            expected_amount="1.0",
            ws_url="wss://custom-ws.example.com",
        )
        
        assert monitor.provider.network_config.ws_url == "wss://custom-ws.example.com"

    def test_create_monitor_invalid_network(self, sample_eth_address: str):
        """Test that invalid network raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            create_monitor(
                network="invalid_network",
                wallet_address=sample_eth_address,
                expected_amount="1.0",
            )
        
        assert "not in registry" in str(exc_info.value)

    def test_create_monitor_invalid_address(self):
        """Test that invalid address raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            create_monitor(
                network="ethereum",
                wallet_address="invalid_address",
                expected_amount="1.0",
            )
        
        assert "Invalid" in str(exc_info.value)

    def test_create_monitor_negative_amount(self, sample_eth_address: str):
        """Test that negative amount raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            create_monitor(
                network="ethereum",
                wallet_address=sample_eth_address,
                expected_amount="-1.0",
            )
        
        assert "positive" in str(exc_info.value)

    def test_create_monitor_zero_amount(self, sample_eth_address: str):
        """Test that zero amount raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            create_monitor(
                network="ethereum",
                wallet_address=sample_eth_address,
                expected_amount="0",
            )
        
        assert "positive" in str(exc_info.value)

    def test_create_monitor_with_user_config(self, sample_eth_address: str, user_config: UserConfig):
        """Test creating monitor with custom UserConfig."""
        monitor = create_monitor(
            network="ethereum",
            wallet_address=sample_eth_address,
            expected_amount="1.0",
            user_config=user_config,
        )
        
        assert monitor.config.timeout == user_config.timeout
        assert monitor.config.max_retries == user_config.max_retries

    def test_create_monitor_auto_stop(self, sample_eth_address: str):
        """Test creating monitor with auto_stop enabled."""
        monitor = create_monitor(
            network="ethereum",
            wallet_address=sample_eth_address,
            expected_amount="1.0",
            auto_stop=True,
        )
        
        assert monitor.auto_stop is True

    def test_create_monitor_realtime_mode(self, sample_eth_address: str):
        """Test creating monitor with explicit realtime mode."""
        monitor = create_monitor(
            network="ethereum",
            wallet_address=sample_eth_address,
            expected_amount="1.0",
            realtime=True,
        )
        
        assert monitor.realtime is True

    def test_create_monitor_polling_mode(self, sample_eth_address: str):
        """Test creating monitor with explicit polling mode."""
        monitor = create_monitor(
            network="ethereum",
            wallet_address=sample_eth_address,
            expected_amount="1.0",
            realtime=False,
        )
        
        assert monitor.realtime is False

    def test_create_monitor_min_confirmations(self, sample_eth_address: str):
        """Test creating monitor with custom min_confirmations."""
        monitor = create_monitor(
            network="ethereum",
            wallet_address=sample_eth_address,
            expected_amount="1.0",
            min_confirmations=6,
        )
        
        assert monitor.min_confirmations == 6


# =============================================================================
# PaymentMonitor Tests
# =============================================================================


class TestPaymentMonitor:
    """Tests for PaymentMonitor class."""

    @pytest.fixture
    def mock_provider(self):
        """Create a mock provider."""
        provider = MagicMock()
        provider.NETWORK_NAME = "ethereum"
        provider.CURRENCY_SYMBOL = "ETH"
        provider.connect = AsyncMock()
        provider.close = AsyncMock()
        provider.get_transactions = AsyncMock(return_value=[])
        provider.network_config = MagicMock()
        provider.network_config.ws_url = None
        provider.network_config.chain_type = "evm"
        return provider

    @pytest.fixture
    def monitor(self, mock_provider: MagicMock, sample_eth_address: str) -> PaymentMonitor:
        """Create a PaymentMonitor instance for testing."""
        return PaymentMonitor(
            provider=mock_provider,
            wallet_address=sample_eth_address,
            expected_amount="1.0",
            poll_interval=1.0,
            max_transactions=5,
            auto_stop=False,
            realtime=False,  # Use polling for tests
        )

    def test_monitor_initialization(self, monitor: PaymentMonitor, sample_eth_address: str):
        """Test monitor initialization."""
        assert monitor.wallet_address == sample_eth_address
        assert monitor.expected_amount == Decimal("1.0")
        assert monitor.poll_interval == 1.0
        assert monitor.max_transactions == 5
        assert monitor.auto_stop is False
        assert monitor.is_running is False

    def test_monitor_id_auto_generated(self, mock_provider: MagicMock, sample_eth_address: str):
        """Test that monitor_id is auto-generated if not provided."""
        monitor = PaymentMonitor(
            provider=mock_provider,
            wallet_address=sample_eth_address,
            expected_amount="1.0",
        )
        
        assert monitor.monitor_id is not None
        assert len(monitor.monitor_id) > 0

    def test_monitor_id_custom(self, mock_provider: MagicMock, sample_eth_address: str):
        """Test custom monitor_id."""
        monitor = PaymentMonitor(
            provider=mock_provider,
            wallet_address=sample_eth_address,
            expected_amount="1.0",
            monitor_id="custom_id_123",
        )
        
        assert monitor.monitor_id == "custom_id_123"

    def test_on_payment_decorator(self, monitor: PaymentMonitor):
        """Test on_payment as decorator."""
        @monitor.on_payment
        async def handler(event):
            pass
        
        assert handler in monitor._payment_callbacks

    def test_on_payment_method(self, monitor: PaymentMonitor):
        """Test on_payment as method call."""
        async def handler(event):
            pass
        
        monitor.on_payment(handler)
        
        assert handler in monitor._payment_callbacks

    def test_on_payment_no_duplicates(self, monitor: PaymentMonitor):
        """Test that same callback isn't added twice."""
        async def handler(event):
            pass
        
        monitor.on_payment(handler)
        monitor.on_payment(handler)
        
        assert monitor._payment_callbacks.count(handler) == 1

    def test_on_error_decorator(self, monitor: PaymentMonitor):
        """Test on_error as decorator."""
        @monitor.on_error
        async def handler(event):
            pass
        
        assert handler in monitor._error_callbacks

    def test_on_error_method(self, monitor: PaymentMonitor):
        """Test on_error as method call."""
        async def handler(event):
            pass
        
        monitor.on_error(handler)
        
        assert handler in monitor._error_callbacks

    def test_monitor_repr(self, monitor: PaymentMonitor):
        """Test monitor string representation."""
        repr_str = repr(monitor)
        
        assert "PaymentMonitor" in repr_str
        assert "ethereum" in repr_str
        assert "1" in repr_str  # expected amount
        assert "stopped" in repr_str

    @pytest.mark.asyncio
    async def test_emit_payment_async_callback(self, monitor: PaymentMonitor, sample_payment_info: PaymentInfo):
        """Test emitting payment to async callback."""
        received_events = []
        
        @monitor.on_payment
        async def handler(event):
            received_events.append(event)
        
        await monitor._emit_payment(sample_payment_info)
        
        assert len(received_events) == 1
        assert isinstance(received_events[0], PaymentEvent)
        assert received_events[0].payment_info == sample_payment_info

    @pytest.mark.asyncio
    async def test_emit_payment_sync_callback(self, monitor: PaymentMonitor, sample_payment_info: PaymentInfo):
        """Test emitting payment to sync callback."""
        received_events = []
        
        def handler(event):
            received_events.append(event)
        
        monitor.on_payment(handler)
        await monitor._emit_payment(sample_payment_info)
        
        assert len(received_events) == 1

    @pytest.mark.asyncio
    async def test_emit_error_async_callback(self, monitor: PaymentMonitor):
        """Test emitting error to async callback."""
        received_events = []
        
        @monitor.on_error
        async def handler(event):
            received_events.append(event)
        
        error = ValueError("Test error")
        await monitor._emit_error(error)
        
        assert len(received_events) == 1
        assert isinstance(received_events[0], ErrorEvent)
        assert received_events[0].error == error

    @pytest.mark.asyncio
    async def test_emit_error_sync_callback(self, monitor: PaymentMonitor):
        """Test emitting error to sync callback."""
        received_events = []
        
        def handler(event):
            received_events.append(event)
        
        monitor.on_error(handler)
        error = RuntimeError("Test error")
        await monitor._emit_error(error)
        
        assert len(received_events) == 1

    @pytest.mark.asyncio
    async def test_callback_exception_handling(self, monitor: PaymentMonitor, sample_payment_info: PaymentInfo):
        """Test that callback exceptions don't crash the monitor."""
        @monitor.on_payment
        async def bad_handler(event):
            raise RuntimeError("Callback error")
        
        @monitor.on_payment
        async def good_handler(event):
            pass
        
        # Should not raise
        await monitor._emit_payment(sample_payment_info)

    @pytest.mark.asyncio
    async def test_stop_when_not_running(self, monitor: PaymentMonitor):
        """Test stopping monitor that isn't running."""
        # Should not raise
        await monitor.stop()
        
        assert monitor.is_running is False


# =============================================================================
# Provider Tests
# =============================================================================


class TestGetProvider:
    """Tests for get_provider function."""

    @pytest.fixture(autouse=True)
    def setup_networks(self):
        """Register test networks before each test."""
        from cryptoscan.networks import register_common_networks
        register_common_networks()

    def test_get_provider_valid_network(self):
        """Test getting provider for valid network."""
        provider = get_provider("ethereum")
        
        assert provider is not None
        assert provider.NETWORK_NAME == "ethereum"

    def test_get_provider_with_alias(self):
        """Test getting provider using network alias."""
        provider = get_provider("eth")
        
        assert provider is not None
        assert provider.NETWORK_NAME == "ethereum"

    def test_get_provider_invalid_network(self):
        """Test getting provider for invalid network."""
        with pytest.raises(ValidationError) as exc_info:
            get_provider("invalid_network")
        
        assert "Unsupported network" in str(exc_info.value)

    def test_get_provider_custom_rpc(self):
        """Test getting provider with custom RPC URL."""
        provider = get_provider(
            "ethereum",
            rpc_url="https://custom-rpc.example.com",
        )
        
        assert provider.rpc_url == "https://custom-rpc.example.com"


class TestGetSupportedNetworks:
    """Tests for get_supported_networks function."""

    @pytest.fixture(autouse=True)
    def setup_networks(self):
        """Register test networks before each test."""
        from cryptoscan.networks import register_common_networks
        register_common_networks()

    def test_returns_list(self):
        """Test that function returns a list."""
        networks = get_supported_networks()
        
        assert isinstance(networks, list)

    def test_includes_common_networks(self):
        """Test that common networks are included."""
        networks = get_supported_networks()
        
        assert "ethereum" in networks
        assert "eth" in networks  # alias


# =============================================================================
# Network Registration Tests
# =============================================================================


class TestNetworkRegistration:
    """Tests for network registration."""

    def test_register_custom_network(self, sample_eth_address: str):
        """Test registering a custom network."""
        custom_config = NetworkConfig(
            name="testnet",
            symbol="TEST",
            rpc_url="https://testnet.example.com",
            address_pattern=r"^0x[a-fA-F0-9]{40}$",
            decimals=18,
            chain_type="evm",
        )
        
        register_network(custom_config)
        
        # Should now be able to create monitor with this network
        monitor = create_monitor(
            network="testnet",
            wallet_address=sample_eth_address,
            expected_amount="1.0",
        )
        
        assert monitor.provider.NETWORK_NAME == "testnet"

    def test_register_network_with_aliases(self, sample_eth_address: str):
        """Test registering network with aliases."""
        custom_config = NetworkConfig(
            name="mychain",
            symbol="MYC",
            rpc_url="https://mychain.example.com",
            address_pattern=r"^0x[a-fA-F0-9]{40}$",
            decimals=18,
            aliases=["my", "myc"],
            chain_type="evm",
        )
        
        register_network(custom_config)
        
        # Should work with alias
        from cryptoscan.networks import get_network
        network = get_network("my")
        
        assert network is not None
        assert network.name == "mychain"


# =============================================================================
# End-to-End Integration Tests
# =============================================================================


class TestEndToEndMonitoring:
    """End-to-end integration tests for monitoring workflow."""

    @pytest.fixture(autouse=True)
    def setup_networks(self):
        """Register test networks before each test."""
        from cryptoscan.networks import register_common_networks
        register_common_networks()

    @pytest.mark.asyncio
    async def test_full_monitoring_workflow(self, sample_eth_address: str):
        """Test complete monitoring workflow with mocked provider."""
        # Create monitor
        monitor = create_monitor(
            network="ethereum",
            wallet_address=sample_eth_address,
            expected_amount="1.0",
            poll_interval=0.1,
            auto_stop=True,
            realtime=False,
        )
        
        # Track events
        payment_events = []
        error_events = []
        
        @monitor.on_payment
        async def on_payment(event):
            payment_events.append(event)
        
        @monitor.on_error
        async def on_error(event):
            error_events.append(event)
        
        # Mock the provider to return a matching payment
        matching_payment = PaymentInfo(
            transaction_id="0xtest123",
            wallet_address=sample_eth_address,
            amount=Decimal("1.0"),
            currency="ETH",
            status=PaymentStatus.CONFIRMED,
            timestamp=datetime.now(timezone.utc),
            confirmations=10,
        )
        
        # Mock the strategy's check method to return our payment
        with patch.object(
            monitor.provider, 
            'get_recent_transactions', 
            new_callable=AsyncMock, 
            return_value=[matching_payment]
        ):
            # Start monitoring in background task
            task = asyncio.create_task(monitor.start())
            
            # Wait briefly for monitoring to detect payment
            await asyncio.sleep(0.3)
            
            # Stop monitor
            await monitor.stop()
            
            try:
                await asyncio.wait_for(task, timeout=1.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass

    @pytest.mark.asyncio
    async def test_monitor_with_multiple_callbacks(self, sample_eth_address: str, sample_payment_info: PaymentInfo):
        """Test monitor with multiple payment callbacks."""
        monitor = create_monitor(
            network="ethereum",
            wallet_address=sample_eth_address,
            expected_amount="1.0",
            realtime=False,
        )
        
        results = {"callback1": False, "callback2": False, "callback3": False}
        
        @monitor.on_payment
        async def callback1(event):
            results["callback1"] = True
        
        @monitor.on_payment
        async def callback2(event):
            results["callback2"] = True
        
        @monitor.on_payment
        def callback3(event):  # Sync callback
            results["callback3"] = True
        
        # Emit payment directly
        await monitor._emit_payment(sample_payment_info)
        
        assert all(results.values())

    @pytest.mark.asyncio
    async def test_monitor_error_propagation(self, sample_eth_address: str):
        """Test that monitor errors are properly propagated."""
        monitor = create_monitor(
            network="ethereum",
            wallet_address=sample_eth_address,
            expected_amount="1.0",
            realtime=False,
        )
        
        error_received = []
        
        @monitor.on_error
        async def on_error(event):
            error_received.append(event)
        
        # Emit an error
        test_error = ConnectionError("Network failure")
        await monitor._emit_error(test_error)
        
        assert len(error_received) == 1
        assert error_received[0].error == test_error
        assert "Network failure" in error_received[0].message
