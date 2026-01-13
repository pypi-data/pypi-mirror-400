"""
Unit tests for metrics module.
"""

import asyncio
import pytest
import time

from cryptoscan.metrics import (
    MetricsCollector,
    RequestMetric,
    MetricsSummary,
    get_global_metrics,
    enable_global_metrics,
    disable_global_metrics,
)


# =============================================================================
# RequestMetric Tests
# =============================================================================


class TestRequestMetric:
    """Tests for RequestMetric dataclass."""

    def test_create_metric(self):
        """Test creating a RequestMetric."""
        metric = RequestMetric(
            method="eth_blockNumber",
            endpoint="https://rpc.example.com",
            start_time=1000.0,
            end_time=1000.5,
            success=True,
            response_size=100,
        )
        
        assert metric.method == "eth_blockNumber"
        assert metric.endpoint == "https://rpc.example.com"
        assert metric.success is True
        assert metric.response_size == 100

    def test_duration_calculation(self):
        """Test duration calculation."""
        metric = RequestMetric(
            method="test",
            endpoint="http://test.com",
            start_time=1000.0,
            end_time=1000.5,
        )
        
        assert metric.duration_ms == 500.0
        assert metric.duration_s == 0.5

    def test_duration_no_end_time(self):
        """Test duration when end_time is not set."""
        metric = RequestMetric(
            method="test",
            endpoint="http://test.com",
            start_time=1000.0,
        )
        
        assert metric.duration_ms == 0.0
        assert metric.duration_s == 0.0

    def test_failed_metric(self):
        """Test creating a failed metric."""
        metric = RequestMetric(
            method="eth_call",
            endpoint="https://rpc.example.com",
            start_time=1000.0,
            end_time=1001.0,
            success=False,
            error="Connection timeout",
        )
        
        assert metric.success is False
        assert metric.error == "Connection timeout"
        assert metric.duration_ms == 1000.0


# =============================================================================
# MetricsCollector Tests
# =============================================================================


class TestMetricsCollector:
    """Tests for MetricsCollector class."""

    @pytest.fixture
    def collector(self) -> MetricsCollector:
        """Create a MetricsCollector instance."""
        return MetricsCollector(max_history=100, enabled=True)

    def test_initialization(self, collector: MetricsCollector):
        """Test collector initialization."""
        assert collector.enabled is True
        
        summary = collector.get_summary()
        assert summary.total_requests == 0
        assert summary.successful_requests == 0
        assert summary.failed_requests == 0

    def test_disabled_collector(self):
        """Test that disabled collector doesn't record metrics."""
        collector = MetricsCollector(enabled=False)
        
        collector.record_request(
            method="test",
            endpoint="http://test.com",
            duration_ms=100,
        )
        
        summary = collector.get_summary()
        assert summary.total_requests == 0

    def test_enable_disable(self, collector: MetricsCollector):
        """Test enabling and disabling collector."""
        assert collector.enabled is True
        
        collector.enabled = False
        assert collector.enabled is False
        
        collector.enabled = True
        assert collector.enabled is True

    def test_record_request(self, collector: MetricsCollector):
        """Test recording a request."""
        collector.record_request(
            method="eth_blockNumber",
            endpoint="https://rpc.example.com",
            duration_ms=50.0,
            success=True,
            response_size=100,
        )
        
        summary = collector.get_summary()
        assert summary.total_requests == 1
        assert summary.successful_requests == 1
        assert summary.failed_requests == 0
        assert summary.total_response_bytes == 100

    def test_record_failed_request(self, collector: MetricsCollector):
        """Test recording a failed request."""
        collector.record_request(
            method="eth_call",
            endpoint="https://rpc.example.com",
            duration_ms=100.0,
            success=False,
            error="Timeout",
        )
        
        summary = collector.get_summary()
        assert summary.total_requests == 1
        assert summary.successful_requests == 0
        assert summary.failed_requests == 1

    def test_multiple_requests(self, collector: MetricsCollector):
        """Test recording multiple requests."""
        for i in range(10):
            collector.record_request(
                method="eth_blockNumber",
                endpoint="https://rpc.example.com",
                duration_ms=50.0 + i * 10,
                success=i % 3 != 0,  # Every 3rd request fails
            )
        
        summary = collector.get_summary()
        assert summary.total_requests == 10
        assert summary.successful_requests == 6
        assert summary.failed_requests == 4

    def test_average_response_time(self, collector: MetricsCollector):
        """Test average response time calculation."""
        collector.record_request("test", "http://test.com", duration_ms=100)
        collector.record_request("test", "http://test.com", duration_ms=200)
        collector.record_request("test", "http://test.com", duration_ms=300)
        
        summary = collector.get_summary()
        assert summary.avg_response_time_ms == pytest.approx(200.0)

    def test_min_max_response_time(self, collector: MetricsCollector):
        """Test min/max response time calculation."""
        collector.record_request("test", "http://test.com", duration_ms=100)
        collector.record_request("test", "http://test.com", duration_ms=500)
        collector.record_request("test", "http://test.com", duration_ms=200)
        
        summary = collector.get_summary()
        assert summary.min_response_time_ms == pytest.approx(100.0)
        assert summary.max_response_time_ms == pytest.approx(500.0)

    def test_error_rate(self, collector: MetricsCollector):
        """Test error rate calculation."""
        collector.record_request("test", "http://test.com", duration_ms=100, success=True)
        collector.record_request("test", "http://test.com", duration_ms=100, success=False)
        collector.record_request("test", "http://test.com", duration_ms=100, success=True)
        collector.record_request("test", "http://test.com", duration_ms=100, success=False)
        
        summary = collector.get_summary()
        assert summary.error_rate == 0.5

    def test_method_counts(self, collector: MetricsCollector):
        """Test per-method counting."""
        collector.record_request("eth_blockNumber", "http://test.com", duration_ms=50)
        collector.record_request("eth_blockNumber", "http://test.com", duration_ms=50)
        collector.record_request("eth_getBalance", "http://test.com", duration_ms=100)
        
        summary = collector.get_summary()
        assert summary.method_counts["eth_blockNumber"] == 2
        assert summary.method_counts["eth_getBalance"] == 1

    def test_method_errors(self, collector: MetricsCollector):
        """Test per-method error counting."""
        collector.record_request("eth_call", "http://test.com", duration_ms=100, success=False)
        collector.record_request("eth_call", "http://test.com", duration_ms=100, success=True)
        collector.record_request("eth_call", "http://test.com", duration_ms=100, success=False)
        
        summary = collector.get_summary()
        assert summary.method_errors["eth_call"] == 2

    def test_method_avg_times(self, collector: MetricsCollector):
        """Test per-method average time calculation."""
        collector.record_request("eth_blockNumber", "http://test.com", duration_ms=100)
        collector.record_request("eth_blockNumber", "http://test.com", duration_ms=200)
        
        summary = collector.get_summary()
        assert summary.method_avg_times["eth_blockNumber"] == pytest.approx(150.0)

    def test_get_recent_requests(self, collector: MetricsCollector):
        """Test getting recent requests."""
        for i in range(20):
            collector.record_request(f"method_{i}", "http://test.com", duration_ms=100)
        
        recent = collector.get_recent_requests(limit=5)
        assert len(recent) == 5
        assert recent[-1].method == "method_19"

    def test_get_errors(self, collector: MetricsCollector):
        """Test getting error requests."""
        collector.record_request("test1", "http://test.com", duration_ms=100, success=True)
        collector.record_request("test2", "http://test.com", duration_ms=100, success=False, error="Error 1")
        collector.record_request("test3", "http://test.com", duration_ms=100, success=True)
        collector.record_request("test4", "http://test.com", duration_ms=100, success=False, error="Error 2")
        
        errors = collector.get_errors(limit=10)
        assert len(errors) == 2
        assert all(not e.success for e in errors)

    def test_get_method_stats(self, collector: MetricsCollector):
        """Test getting method-specific stats."""
        collector.record_request("eth_call", "http://test.com", duration_ms=100, success=True)
        collector.record_request("eth_call", "http://test.com", duration_ms=200, success=False)
        collector.record_request("eth_call", "http://test.com", duration_ms=300, success=True)
        
        stats = collector.get_method_stats("eth_call")
        assert stats["method"] == "eth_call"
        assert stats["total_calls"] == 3
        assert stats["errors"] == 1
        assert stats["error_rate"] == pytest.approx(1/3)
        assert stats["avg_time_ms"] == pytest.approx(200.0)

    def test_reset(self, collector: MetricsCollector):
        """Test resetting metrics."""
        collector.record_request("test", "http://test.com", duration_ms=100)
        collector.record_request("test", "http://test.com", duration_ms=200)
        
        collector.reset()
        
        summary = collector.get_summary()
        assert summary.total_requests == 0
        assert summary.successful_requests == 0
        assert len(collector.get_recent_requests()) == 0

    def test_max_history_limit(self):
        """Test that history is limited to max_history."""
        collector = MetricsCollector(max_history=10, enabled=True)
        
        for i in range(20):
            collector.record_request(f"method_{i}", "http://test.com", duration_ms=100)
        
        recent = collector.get_recent_requests(limit=100)
        assert len(recent) == 10
        # Should have the last 10 requests
        assert recent[0].method == "method_10"
        assert recent[-1].method == "method_19"

    def test_callback_on_request_complete(self):
        """Test callback is called on request completion."""
        received_metrics = []
        
        def callback(metric: RequestMetric):
            received_metrics.append(metric)
        
        collector = MetricsCollector(enabled=True, on_request_complete=callback)
        collector.record_request("test", "http://test.com", duration_ms=100)
        
        assert len(received_metrics) == 1
        assert received_metrics[0].method == "test"

    def test_callback_exception_handling(self):
        """Test that callback exceptions don't crash collector."""
        def bad_callback(metric: RequestMetric):
            raise RuntimeError("Callback error")
        
        collector = MetricsCollector(enabled=True, on_request_complete=bad_callback)
        
        # Should not raise
        collector.record_request("test", "http://test.com", duration_ms=100)
        
        summary = collector.get_summary()
        assert summary.total_requests == 1

    @pytest.mark.asyncio
    async def test_track_request_async(self, collector: MetricsCollector):
        """Test async context manager for tracking requests."""
        async with collector.track_request("eth_blockNumber", "http://test.com") as metric:
            await asyncio.sleep(0.01)
            metric.response_size = 50
        
        summary = collector.get_summary()
        assert summary.total_requests == 1
        assert summary.total_response_bytes == 50

    @pytest.mark.asyncio
    async def test_track_request_async_error(self, collector: MetricsCollector):
        """Test async context manager with error."""
        with pytest.raises(ValueError):
            async with collector.track_request("eth_call", "http://test.com"):
                raise ValueError("Test error")
        
        summary = collector.get_summary()
        assert summary.total_requests == 1
        assert summary.failed_requests == 1
        
        errors = collector.get_errors()
        assert len(errors) == 1
        assert "Test error" in errors[0].error

    def test_track_request_sync(self, collector: MetricsCollector):
        """Test sync context manager for tracking requests."""
        with collector.track_request_sync("eth_blockNumber", "http://test.com") as metric:
            time.sleep(0.01)
            metric.response_size = 100
        
        summary = collector.get_summary()
        assert summary.total_requests == 1
        assert summary.total_response_bytes == 100

    def test_track_request_sync_error(self, collector: MetricsCollector):
        """Test sync context manager with error."""
        with pytest.raises(RuntimeError):
            with collector.track_request_sync("eth_call", "http://test.com"):
                raise RuntimeError("Sync error")
        
        summary = collector.get_summary()
        assert summary.failed_requests == 1

    def test_repr(self, collector: MetricsCollector):
        """Test string representation."""
        collector.record_request("test", "http://test.com", duration_ms=100)
        
        repr_str = repr(collector)
        assert "MetricsCollector" in repr_str
        assert "requests=1" in repr_str

    def test_export_prometheus(self, collector: MetricsCollector):
        """Test Prometheus export format."""
        collector.record_request("eth_blockNumber", "http://test.com", duration_ms=100)
        collector.record_request("eth_getBalance", "http://test.com", duration_ms=200, success=False)
        
        output = collector.export_prometheus()
        
        assert "cryptoscan_requests_total 2" in output
        assert "cryptoscan_requests_failed_total 1" in output
        assert "cryptoscan_request_duration_ms" in output
        assert 'method="eth_blockNumber"' in output
        assert 'method="eth_getBalance"' in output


# =============================================================================
# Global Metrics Tests
# =============================================================================


class TestGlobalMetrics:
    """Tests for global metrics functions."""

    def test_get_global_metrics(self):
        """Test getting global metrics instance."""
        metrics = get_global_metrics()
        
        assert isinstance(metrics, MetricsCollector)

    def test_enable_global_metrics(self):
        """Test enabling global metrics."""
        metrics = enable_global_metrics(max_history=500)
        
        assert metrics.enabled is True
        assert metrics is get_global_metrics()

    def test_disable_global_metrics(self):
        """Test disabling global metrics."""
        enable_global_metrics()
        disable_global_metrics()
        
        metrics = get_global_metrics()
        assert metrics.enabled is False

    def test_global_metrics_with_callback(self):
        """Test global metrics with callback."""
        received = []
        
        def callback(metric):
            received.append(metric)
        
        metrics = enable_global_metrics(on_request_complete=callback)
        metrics.record_request("test", "http://test.com", duration_ms=100)
        
        assert len(received) == 1


# =============================================================================
# Thread Safety Tests
# =============================================================================


class TestThreadSafety:
    """Tests for thread safety of MetricsCollector."""

    def test_concurrent_recording(self):
        """Test concurrent request recording."""
        import threading
        
        collector = MetricsCollector(max_history=1000, enabled=True)
        
        def record_requests():
            for i in range(100):
                collector.record_request(
                    method=f"method_{threading.current_thread().name}",
                    endpoint="http://test.com",
                    duration_ms=10,
                )
        
        threads = [threading.Thread(target=record_requests) for _ in range(10)]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        summary = collector.get_summary()
        assert summary.total_requests == 1000
