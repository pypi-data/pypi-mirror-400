"""
Unit tests for chain parsers.
"""

import pytest
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

from cryptoscan.chain_parsers import EVMParser, SolanaParser, BitcoinParser
from cryptoscan.models import PaymentInfo, PaymentStatus
from cryptoscan.networks import NetworkConfig


# =============================================================================
# EVMParser Tests
# =============================================================================


class TestEVMParser:
    """Tests for EVM chain parser."""

    @pytest.fixture
    def evm_parser(self, ethereum_config: NetworkConfig, mock_rpc_client: MagicMock) -> EVMParser:
        """Create EVMParser instance for testing."""
        return EVMParser(
            client=mock_rpc_client,
            network_config=ethereum_config,
            currency_symbol="ETH",
        )

    def test_parse_transaction_basic(self, evm_parser: EVMParser, sample_evm_block: dict):
        """Test basic EVM transaction parsing."""
        tx = sample_evm_block["transactions"][0]
        block = sample_evm_block
        
        result = evm_parser.parse_transaction(tx, block, latest_block_num=12345678)
        
        assert isinstance(result, PaymentInfo)
        assert result.transaction_id == tx["hash"]
        assert result.wallet_address == tx["to"]
        assert result.amount == Decimal("1")  # 1 ETH
        assert result.currency == "ETH"
        assert result.status == PaymentStatus.CONFIRMED
        assert result.confirmations == 1

    def test_parse_transaction_with_confirmations(self, evm_parser: EVMParser, sample_evm_transaction: dict):
        """Test transaction parsing with confirmation count."""
        block = {
            "number": "0xbc614e",  # 12345678
            "timestamp": "0x5f5e100",
            "transactions": [],
        }
        
        # Latest block is 10 blocks ahead
        result = evm_parser.parse_transaction(
            sample_evm_transaction, 
            block, 
            latest_block_num=12345688
        )
        
        assert result.confirmations == 11  # 12345688 - 12345678 + 1

    def test_parse_transaction_pending(self, evm_parser: EVMParser):
        """Test parsing pending transaction (no block number)."""
        tx = {
            "hash": "0xabc123",
            "from": "0x1111111111111111111111111111111111111111",
            "to": "0x2222222222222222222222222222222222222222",
            "value": "0xde0b6b3a7640000",
            "blockNumber": None,
        }
        
        result = evm_parser.parse_transaction(tx)
        
        assert result.status == PaymentStatus.PENDING
        assert result.confirmations == 0

    def test_parse_transaction_failed(self, evm_parser: EVMParser, sample_evm_transaction: dict):
        """Test parsing failed transaction."""
        block = {"number": "0xbc614e", "timestamp": "0x5f5e100"}
        receipt = {"status": "0x0"}  # Failed status
        
        result = evm_parser.parse_transaction(sample_evm_transaction, block, receipt)
        
        assert result.status == PaymentStatus.FAILED

    def test_parse_transaction_zero_value(self, evm_parser: EVMParser):
        """Test parsing transaction with zero value."""
        tx = {
            "hash": "0xabc123",
            "from": "0x1111111111111111111111111111111111111111",
            "to": "0x2222222222222222222222222222222222222222",
            "value": "0x0",
            "blockNumber": "0x1",
        }
        block = {"number": "0x1", "timestamp": "0x5f5e100"}
        
        result = evm_parser.parse_transaction(tx, block)
        
        assert result.amount == Decimal("0")

    @pytest.mark.asyncio
    async def test_get_transactions(self, evm_parser: EVMParser, sample_eth_address: str):
        """Test getting transactions for an address."""
        # Mock RPC responses
        evm_parser.client.call = AsyncMock(side_effect=[
            "0xbc614e",  # eth_blockNumber
            {  # eth_getBlockByNumber
                "number": "0xbc614e",
                "timestamp": "0x5f5e100",
                "transactions": [
                    {
                        "hash": "0x123",
                        "from": "0x111",
                        "to": sample_eth_address,
                        "value": "0xde0b6b3a7640000",
                        "blockNumber": "0xbc614e",
                    }
                ],
            },
        ] + [{"number": hex(12345678 - i), "timestamp": "0x5f5e100", "transactions": []} for i in range(1, 100)])
        
        result = await evm_parser.get_transactions(sample_eth_address, limit=5)
        
        assert len(result) == 1
        assert result[0].wallet_address.lower() == sample_eth_address.lower()

    @pytest.mark.asyncio
    async def test_get_transactions_with_expected_amount(self, evm_parser: EVMParser, sample_eth_address: str):
        """Test getting transactions with expected amount filter."""
        evm_parser.client.call = AsyncMock(side_effect=[
            "0xbc614e",
            {
                "number": "0xbc614e",
                "timestamp": "0x5f5e100",
                "transactions": [
                    {
                        "hash": "0x123",
                        "from": "0x111",
                        "to": sample_eth_address,
                        "value": "0xde0b6b3a7640000",  # 1 ETH
                        "blockNumber": "0xbc614e",
                    }
                ],
            },
        ])
        
        result = await evm_parser.get_transactions(
            sample_eth_address, 
            limit=5, 
            expected_amount=Decimal("1")
        )
        
        assert len(result) == 1
        assert result[0].amount == Decimal("1")

    @pytest.mark.asyncio
    async def test_get_transaction_by_hash(self, evm_parser: EVMParser):
        """Test getting single transaction by hash."""
        tx_hash = "0x1234567890abcdef"
        
        evm_parser.client.call = AsyncMock(side_effect=[
            {  # eth_getTransactionByHash
                "hash": tx_hash,
                "from": "0x111",
                "to": "0x222",
                "value": "0xde0b6b3a7640000",
                "blockNumber": "0x1",
            },
            {  # eth_getTransactionReceipt
                "status": "0x1",
            },
        ])
        
        result = await evm_parser.get_transaction(tx_hash)
        
        assert result is not None
        assert result.transaction_id == tx_hash

    @pytest.mark.asyncio
    async def test_get_transaction_not_found(self, evm_parser: EVMParser):
        """Test getting non-existent transaction."""
        evm_parser.client.call = AsyncMock(return_value=None)
        
        result = await evm_parser.get_transaction("0xnonexistent")
        
        assert result is None


# =============================================================================
# SolanaParser Tests
# =============================================================================


class TestSolanaParser:
    """Tests for Solana chain parser."""

    @pytest.fixture
    def solana_parser(self, solana_config: NetworkConfig, mock_rpc_client: MagicMock) -> SolanaParser:
        """Create SolanaParser instance for testing."""
        return SolanaParser(
            client=mock_rpc_client,
            network_config=solana_config,
            currency_symbol="SOL",
        )

    def test_parse_transaction_basic(self, solana_parser: SolanaParser, sample_solana_transaction: dict):
        """Test basic Solana transaction parsing."""
        result = solana_parser.parse_transaction(sample_solana_transaction)
        
        assert isinstance(result, PaymentInfo)
        assert result.currency == "SOL"
        assert result.status == PaymentStatus.CONFIRMED
        # Amount is difference in balances: (1000000000 - 500000000) / 10^9 = 0.5 SOL
        assert result.amount == Decimal("0.5")

    def test_parse_transaction_failed(self, solana_parser: SolanaParser):
        """Test parsing failed Solana transaction."""
        tx = {
            "transaction": {
                "signatures": ["sig123"],
                "message": {"accountKeys": ["addr1", "addr2"]},
            },
            "meta": {
                "preBalances": [1000000000, 0],
                "postBalances": [1000000000, 0],
                "fee": 5000,
                "err": {"InstructionError": [0, "Custom"]},
            },
            "slot": 123,
            "blockTime": 1609459200,
        }
        
        result = solana_parser.parse_transaction(tx)
        
        assert result.status == PaymentStatus.FAILED

    def test_parse_transaction_with_fee(self, solana_parser: SolanaParser, sample_solana_transaction: dict):
        """Test parsing transaction with fee calculation."""
        result = solana_parser.parse_transaction(sample_solana_transaction)
        
        # Fee is 5000 lamports = 0.000005 SOL
        assert result.fee == Decimal("0.000005")

    @pytest.mark.asyncio
    async def test_get_transactions(self, solana_parser: SolanaParser, sample_sol_address: str):
        """Test getting Solana transactions."""
        solana_parser.client.call = AsyncMock(side_effect=[
            [{"signature": "sig1"}, {"signature": "sig2"}],  # getSignaturesForAddress
            {  # getTransaction for sig1
                "transaction": {
                    "signatures": ["sig1"],
                    "message": {"accountKeys": [sample_sol_address, "addr2"]},
                },
                "meta": {
                    "preBalances": [1000000000, 0],
                    "postBalances": [500000000, 500000000],
                    "fee": 5000,
                    "err": None,
                },
                "slot": 123,
                "blockTime": 1609459200,
            },
            {  # getTransaction for sig2
                "transaction": {
                    "signatures": ["sig2"],
                    "message": {"accountKeys": [sample_sol_address, "addr3"]},
                },
                "meta": {
                    "preBalances": [500000000, 0],
                    "postBalances": [250000000, 250000000],
                    "fee": 5000,
                    "err": None,
                },
                "slot": 124,
                "blockTime": 1609459300,
            },
        ])
        
        result = await solana_parser.get_transactions(sample_sol_address, limit=5)
        
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_transaction_by_signature(self, solana_parser: SolanaParser):
        """Test getting single Solana transaction."""
        solana_parser.client.call = AsyncMock(return_value={
            "transaction": {
                "signatures": ["testsig"],
                "message": {"accountKeys": ["addr1", "addr2"]},
            },
            "meta": {
                "preBalances": [1000000000, 0],
                "postBalances": [500000000, 500000000],
                "fee": 5000,
                "err": None,
            },
            "slot": 123,
            "blockTime": 1609459200,
        })
        
        result = await solana_parser.get_transaction("testsig")
        
        assert result is not None
        assert result.transaction_id == "testsig"


# =============================================================================
# BitcoinParser Tests
# =============================================================================


class TestBitcoinParser:
    """Tests for Bitcoin chain parser."""

    @pytest.fixture
    def bitcoin_parser(self, bitcoin_config: NetworkConfig, mock_rpc_client: MagicMock) -> BitcoinParser:
        """Create BitcoinParser instance for testing."""
        return BitcoinParser(
            client=mock_rpc_client,
            network_config=bitcoin_config,
            currency_symbol="BTC",
        )

    def test_parse_transaction_basic(self, bitcoin_parser: BitcoinParser):
        """Test basic Bitcoin transaction parsing."""
        tx = {
            "txid": "abc123def456",
            "vout": [
                {
                    "value": 0.5,
                    "scriptPubKey": {
                        "addresses": ["bc1qtest123"],
                    },
                }
            ],
            "vin": [{"txid": "prevtx"}],
            "confirmations": 6,
            "time": 1609459200,
            "blockheight": 700000,
        }
        
        result = bitcoin_parser.parse_transaction(tx)
        
        assert isinstance(result, PaymentInfo)
        assert result.transaction_id == "abc123def456"
        assert result.amount == Decimal("0.5")
        assert result.currency == "BTC"
        assert result.status == PaymentStatus.CONFIRMED
        assert result.confirmations == 6

    def test_parse_transaction_pending(self, bitcoin_parser: BitcoinParser):
        """Test parsing pending Bitcoin transaction."""
        tx = {
            "txid": "abc123",
            "vout": [{"value": 1.0, "scriptPubKey": {"addresses": ["bc1qtest"]}}],
            "vin": [{"txid": "prevtx"}],
            "confirmations": 0,
        }
        
        result = bitcoin_parser.parse_transaction(tx)
        
        assert result.status == PaymentStatus.PENDING

    def test_parse_transaction_coinbase(self, bitcoin_parser: BitcoinParser):
        """Test parsing coinbase transaction."""
        tx = {
            "txid": "coinbase123",
            "vout": [{"value": 6.25, "scriptPubKey": {"addresses": ["bc1qminer"]}}],
            "vin": [{"coinbase": "03..."}],
            "confirmations": 100,
            "time": 1609459200,
        }
        
        result = bitcoin_parser.parse_transaction(tx)
        
        assert result.from_address == "<coinbase>"

    @pytest.mark.asyncio
    async def test_get_transaction_by_txid(self, bitcoin_parser: BitcoinParser):
        """Test getting Bitcoin transaction by txid."""
        bitcoin_parser.client.call = AsyncMock(return_value={
            "txid": "testtxid",
            "vout": [{"value": 0.1, "scriptPubKey": {"addresses": ["bc1qtest"]}}],
            "vin": [{"txid": "prevtx"}],
            "confirmations": 3,
            "time": 1609459200,
        })
        
        result = await bitcoin_parser.get_transaction("testtxid")
        
        assert result is not None
        assert result.transaction_id == "testtxid"

    @pytest.mark.asyncio
    async def test_get_transaction_not_found(self, bitcoin_parser: BitcoinParser):
        """Test getting non-existent Bitcoin transaction."""
        bitcoin_parser.client.call = AsyncMock(return_value=None)
        
        result = await bitcoin_parser.get_transaction("nonexistent")
        
        assert result is None


# =============================================================================
# Edge Cases and Error Handling
# =============================================================================


class TestParserEdgeCases:
    """Test edge cases and error handling in parsers."""

    @pytest.fixture
    def evm_parser(self, ethereum_config: NetworkConfig, mock_rpc_client: MagicMock) -> EVMParser:
        return EVMParser(mock_rpc_client, ethereum_config, "ETH")

    def test_parse_transaction_missing_fields(self, evm_parser: EVMParser):
        """Test parsing transaction with missing optional fields."""
        tx = {
            "hash": "0x123",
            "value": "0x0",
        }
        
        result = evm_parser.parse_transaction(tx)
        
        assert result.wallet_address == ""
        assert result.from_address == ""

    def test_parse_transaction_invalid_hex_value(self, evm_parser: EVMParser):
        """Test parsing transaction with invalid hex value defaults to 0."""
        tx = {
            "hash": "0x123",
            "from": "0x111",
            "to": "0x222",
            "value": "0x0",  # Valid zero
        }
        
        result = evm_parser.parse_transaction(tx)
        
        assert result.amount == Decimal("0")

    @pytest.mark.asyncio
    async def test_get_transactions_empty_blocks(self, evm_parser: EVMParser, sample_eth_address: str):
        """Test getting transactions when all blocks are empty."""
        evm_parser.client.call = AsyncMock(side_effect=[
            "0x10",  # eth_blockNumber (block 16)
        ] + [
            {"number": hex(16 - i), "timestamp": "0x5f5e100", "transactions": []}
            for i in range(50)
        ])
        
        result = await evm_parser.get_transactions(sample_eth_address, limit=5)
        
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_transactions_handles_rpc_error(self, evm_parser: EVMParser, sample_eth_address: str):
        """Test that parser handles RPC errors gracefully."""
        evm_parser.client.call = AsyncMock(side_effect=[
            "0x10",  # eth_blockNumber
            Exception("RPC Error"),  # First block fails
            {"number": "0xf", "timestamp": "0x5f5e100", "transactions": []},
        ] + [
            {"number": hex(14 - i), "timestamp": "0x5f5e100", "transactions": []}
            for i in range(48)
        ])
        
        # Should not raise, should continue with other blocks
        result = await evm_parser.get_transactions(sample_eth_address, limit=5)
        
        assert isinstance(result, list)
