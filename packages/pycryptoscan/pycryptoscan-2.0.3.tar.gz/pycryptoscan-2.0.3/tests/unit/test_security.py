"""
Unit tests for security module.
"""

import pytest

from cryptoscan.security import (
    validate_rpc_url,
    validate_ws_url,
    mask_address,
    mask_transaction_id,
    sanitize_log_data,
    VALID_RPC_SCHEMES,
    MIN_ADDRESS_LENGTH_FOR_MASKING,
)


# =============================================================================
# URL Validation Tests
# =============================================================================


class TestValidateRpcUrl:
    """Tests for RPC URL validation."""

    @pytest.mark.parametrize("url", [
        "https://ethereum-rpc.publicnode.com",
        "http://localhost:8545",
        "https://mainnet.infura.io/v3/YOUR-PROJECT-ID",
        "wss://ethereum-rpc.publicnode.com",
        "ws://localhost:8546",
        "https://rpc.ankr.com/eth",
        "https://api.example.com:8080/rpc",
        "https://user:pass@rpc.example.com",
    ])
    def test_valid_rpc_urls(self, url: str):
        """Test that valid RPC URLs are accepted."""
        assert validate_rpc_url(url) is True

    @pytest.mark.parametrize("url", [
        "file:///etc/passwd",
        "javascript:alert(1)",
        "data:text/html,<script>alert(1)</script>",
        "ftp://ftp.example.com",
        "mailto:test@example.com",
        "ssh://server.example.com",
        "telnet://server.example.com",
    ])
    def test_invalid_schemes(self, url: str):
        """Test that invalid URL schemes are rejected."""
        assert validate_rpc_url(url) is False

    @pytest.mark.parametrize("url", [
        "",
        None,
        "not-a-url",
        "https://",
        "://missing-scheme.com",
        123,
        [],
        {},
    ])
    def test_malformed_urls(self, url):
        """Test that malformed URLs are rejected."""
        assert validate_rpc_url(url) is False

    @pytest.mark.parametrize("url", [
        "https://example.com/<script>",
        "https://example.com/'>alert(1)",
        'https://example.com/"onclick=alert(1)',
        "https://example.com/<img src=x>",
    ])
    def test_injection_attempts(self, url: str):
        """Test that URLs with injection attempts are rejected."""
        assert validate_rpc_url(url) is False

    def test_valid_schemes_constant(self):
        """Test that valid schemes are defined correctly."""
        assert "http" in VALID_RPC_SCHEMES
        assert "https" in VALID_RPC_SCHEMES
        assert "ws" in VALID_RPC_SCHEMES
        assert "wss" in VALID_RPC_SCHEMES
        assert "file" not in VALID_RPC_SCHEMES


class TestValidateWsUrl:
    """Tests for WebSocket URL validation."""

    @pytest.mark.parametrize("url", [
        "wss://ethereum-rpc.publicnode.com",
        "ws://localhost:8546",
        "wss://mainnet.infura.io/ws/v3/YOUR-PROJECT-ID",
        "ws://127.0.0.1:8545",
    ])
    def test_valid_ws_urls(self, url: str):
        """Test that valid WebSocket URLs are accepted."""
        assert validate_ws_url(url) is True

    @pytest.mark.parametrize("url", [
        "https://example.com",
        "http://example.com",
        "ftp://example.com",
        "file:///etc/passwd",
    ])
    def test_non_ws_schemes(self, url: str):
        """Test that non-WebSocket schemes are rejected."""
        assert validate_ws_url(url) is False

    @pytest.mark.parametrize("url", [
        "",
        None,
        "wss://",
        "not-a-url",
    ])
    def test_invalid_ws_urls(self, url):
        """Test that invalid WebSocket URLs are rejected."""
        assert validate_ws_url(url) is False


# =============================================================================
# Address Masking Tests
# =============================================================================


class TestMaskAddress:
    """Tests for address masking."""

    def test_mask_ethereum_address(self):
        """Test masking a standard Ethereum address."""
        address = "0x742d35Cc6634C0532925a3b844Bc9e7595f8fE23"
        result = mask_address(address)
        
        assert result == "0x742d35...f8fE23"
        assert len(result) < len(address)
        assert result.startswith("0x742d35")
        assert result.endswith("f8fE23")
        assert "..." in result

    def test_mask_address_custom_lengths(self):
        """Test masking with custom prefix and suffix lengths."""
        address = "0x742d35Cc6634C0532925a3b844Bc9e7595f8fE23"
        
        result = mask_address(address, prefix_length=4, suffix_length=4)
        
        assert result == "0x74...fE23"

    def test_mask_short_address(self):
        """Test that short addresses are not masked."""
        short_address = "0x1234"
        
        result = mask_address(short_address)
        
        assert result == short_address  # Unchanged

    def test_mask_address_at_threshold(self):
        """Test address at minimum masking threshold."""
        # Just under threshold
        address = "0x12345678"  # 10 chars, under 12
        assert mask_address(address) == address
        
        # At threshold
        address = "0x1234567890AB"  # 14 chars
        result = mask_address(address)
        assert "..." in result

    def test_mask_address_empty_string(self):
        """Test masking empty string."""
        assert mask_address("") == ""

    def test_mask_address_none(self):
        """Test masking None value."""
        assert mask_address(None) == ""

    def test_mask_address_non_string(self):
        """Test masking non-string value."""
        assert mask_address(123) == 123  # Returns as-is

    def test_mask_address_prefix_suffix_too_long(self):
        """Test when prefix + suffix >= address length."""
        address = "0x1234567890"  # 12 chars
        
        # prefix(8) + suffix(6) = 14 > 12, so no masking
        result = mask_address(address, prefix_length=8, suffix_length=6)
        
        assert result == address


class TestMaskTransactionId:
    """Tests for transaction ID masking."""

    def test_mask_transaction_id_basic(self):
        """Test basic transaction ID masking."""
        tx_id = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        
        result = mask_transaction_id(tx_id)
        
        assert result == "0x1234567890abcd..."
        assert len(result) == 19  # 16 chars + "..."

    def test_mask_transaction_id_custom_length(self):
        """Test transaction ID masking with custom visible length."""
        tx_id = "0x1234567890abcdef"
        
        result = mask_transaction_id(tx_id, visible_length=8)
        
        assert result == "0x123456..."

    def test_mask_transaction_id_short(self):
        """Test that short transaction IDs are not masked."""
        tx_id = "0x123456"
        
        result = mask_transaction_id(tx_id)
        
        assert result == tx_id  # Unchanged

    def test_mask_transaction_id_empty(self):
        """Test masking empty transaction ID."""
        assert mask_transaction_id("") == ""

    def test_mask_transaction_id_none(self):
        """Test masking None transaction ID."""
        assert mask_transaction_id(None) == ""


# =============================================================================
# Log Data Sanitization Tests
# =============================================================================


class TestSanitizeLogData:
    """Tests for log data sanitization."""

    def test_sanitize_basic_data(self):
        """Test sanitizing data with sensitive fields."""
        data = {
            "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f8fE23",
            "amount": "1.5",
            "currency": "ETH",
        }
        
        result = sanitize_log_data(data)
        
        assert "..." in result["wallet_address"]
        assert result["amount"] == "1.5"
        assert result["currency"] == "ETH"

    def test_sanitize_transaction_id(self):
        """Test sanitizing transaction ID field."""
        data = {
            "transaction_id": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        }
        
        result = sanitize_log_data(data)
        
        assert result["transaction_id"].endswith("...")

    def test_sanitize_nested_data(self):
        """Test sanitizing nested dictionaries."""
        data = {
            "transaction": {
                "from_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f8fE23",
                "to_address": "0x1234567890123456789012345678901234567890",
            },
            "status": "confirmed",
        }
        
        result = sanitize_log_data(data)
        
        assert "..." in result["transaction"]["from_address"]
        assert "..." in result["transaction"]["to_address"]
        assert result["status"] == "confirmed"

    def test_sanitize_sensitive_keys(self):
        """Test that sensitive keys are properly masked."""
        data = {
            "private_key": "super_secret_key_12345",
            "api_key": "api_key_abcdef",
            "password": "my_password",
            "secret": "secret_value",
            "token": "bearer_token_xyz",
        }
        
        result = sanitize_log_data(data)
        
        for key in data:
            assert result[key] == "***MASKED***"

    def test_sanitize_custom_keys(self):
        """Test sanitizing with custom keys to mask."""
        data = {
            "custom_field": "sensitive_value",
            "normal_field": "normal_value",
        }
        
        result = sanitize_log_data(data, keys_to_mask={"custom_field"})
        
        assert result["custom_field"] == "***MASKED***"
        assert result["normal_field"] == "normal_value"

    def test_sanitize_preserves_non_string_values(self):
        """Test that non-string sensitive values are preserved."""
        data = {
            "address": 12345,  # Non-string
            "amount": 100,
        }
        
        result = sanitize_log_data(data)
        
        assert result["address"] == 12345
        assert result["amount"] == 100

    def test_sanitize_empty_data(self):
        """Test sanitizing empty dictionary."""
        result = sanitize_log_data({})
        
        assert result == {}

    def test_sanitize_hash_field(self):
        """Test that 'hash' field is treated as transaction ID."""
        data = {
            "hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        }
        
        result = sanitize_log_data(data)
        
        assert result["hash"].endswith("...")


# =============================================================================
# Integration Tests
# =============================================================================


class TestSecurityIntegration:
    """Integration tests for security module."""

    def test_full_transaction_sanitization(self):
        """Test sanitizing a complete transaction record."""
        transaction = {
            "transaction_id": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            "from_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f8fE23",
            "to_address": "0x1234567890123456789012345678901234567890",
            "amount": "1.5",
            "currency": "ETH",
            "status": "confirmed",
            "metadata": {
                "api_key": "secret_api_key",
                "wallet_address": "0xabcdef1234567890abcdef1234567890abcdef12",
            },
        }
        
        result = sanitize_log_data(transaction)
        
        # Check top-level masking
        assert "..." in result["transaction_id"]
        assert "..." in result["from_address"]
        assert "..." in result["to_address"]
        
        # Check nested masking
        assert result["metadata"]["api_key"] == "***MASKED***"
        assert "..." in result["metadata"]["wallet_address"]
        
        # Check non-sensitive fields preserved
        assert result["amount"] == "1.5"
        assert result["currency"] == "ETH"
        assert result["status"] == "confirmed"

    def test_url_validation_with_real_endpoints(self):
        """Test URL validation with realistic endpoint patterns."""
        valid_endpoints = [
            "https://mainnet.infura.io/v3/abc123",
            "https://eth-mainnet.g.alchemy.com/v2/xyz789",
            "wss://mainnet.infura.io/ws/v3/abc123",
            "https://rpc.ankr.com/eth",
            "https://cloudflare-eth.com",
        ]
        
        for endpoint in valid_endpoints:
            assert validate_rpc_url(endpoint) is True, f"Failed for: {endpoint}"

    def test_address_masking_various_formats(self):
        """Test address masking with various blockchain address formats."""
        addresses = {
            "ethereum": "0x742d35Cc6634C0532925a3b844Bc9e7595f8fE23",
            "bitcoin_legacy": "1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2",
            "bitcoin_segwit": "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq",
            "solana": "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
        }
        
        for name, address in addresses.items():
            result = mask_address(address)
            assert "..." in result, f"Failed for {name}: {address}"
            assert len(result) < len(address), f"Masking didn't shorten {name}"
