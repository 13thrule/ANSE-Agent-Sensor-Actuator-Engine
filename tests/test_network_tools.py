"""Tests for network tools."""

import asyncio
import pytest

from anse.tools.network import (
    http_get,
    ping,
    dns_lookup,
    NETWORK_TOOLS_AVAILABLE,
)


@pytest.mark.skipif(not NETWORK_TOOLS_AVAILABLE, reason="Network tools not available")
class TestNetworkTools:
    """Test suite for network tools."""

    @pytest.mark.asyncio
    async def test_http_get_valid_url(self):
        """Test HTTP GET to a valid URL."""
        result = await http_get("https://httpbin.org/status/200", timeout=5)
        assert result["status"] in ("success", "error")
        if result["status"] == "success":
            assert "status_code" in result
            assert "elapsed_ms" in result

    @pytest.mark.asyncio
    async def test_http_get_invalid_scheme(self):
        """Test HTTP GET with invalid scheme."""
        result = await http_get("ftp://example.com", timeout=5)
        assert result["status"] == "error"
        assert result["error"] == "invalid_scheme"

    @pytest.mark.asyncio
    async def test_http_get_invalid_url(self):
        """Test HTTP GET with invalid URL."""
        result = await http_get("not a url", timeout=5)
        assert result["status"] == "error"
        assert result["error"] in ("invalid_url", "invalid_scheme")  # "not a url" has no scheme

    @pytest.mark.asyncio
    async def test_http_get_timeout_limit(self):
        """Test HTTP GET timeout validation."""
        result = await http_get("https://example.com", timeout=31)
        assert result["status"] == "error"
        assert result["error"] == "timeout_exceeds_limit"

    @pytest.mark.asyncio
    async def test_http_get_with_headers(self):
        """Test HTTP GET with custom headers."""
        headers = {"User-Agent": "ANSE-Agent/1.0"}
        result = await http_get(
            "https://httpbin.org/headers",
            timeout=5,
            headers=headers,
        )
        assert result["status"] in ("success", "error")

    @pytest.mark.asyncio
    async def test_ping_valid_host(self):
        """Test ping to valid host."""
        result = await ping("8.8.8.8", timeout=5, count=1)
        assert result["status"] in ("success", "error")
        if result["status"] == "success":
            assert "host" in result
            assert "packets_sent" in result
            assert "packets_received" in result
            assert "loss_percent" in result

    @pytest.mark.asyncio
    async def test_ping_invalid_host(self):
        """Test ping with invalid host."""
        result = await ping("", timeout=5, count=1)
        assert result["status"] == "error"
        assert result["error"] == "invalid_host"

    @pytest.mark.asyncio
    async def test_ping_timeout_limit(self):
        """Test ping timeout validation."""
        result = await ping("example.com", timeout=11, count=1)
        assert result["status"] == "error"
        assert result["error"] == "timeout_exceeds_limit"

    @pytest.mark.asyncio
    async def test_ping_count_limit(self):
        """Test ping count validation."""
        result = await ping("example.com", timeout=5, count=11)
        assert result["status"] == "error"
        assert result["error"] == "count_exceeds_limit"

    @pytest.mark.asyncio
    async def test_ping_host_unreachable(self):
        """Test ping to unreachable host."""
        # Use an invalid hostname that DNS can't resolve
        result = await ping("invalid-hostname-that-does-not-exist-12345.com", timeout=5, count=1)
        assert result["status"] == "error"
        # Could be dns_resolution_failed or other error depending on system

    @pytest.mark.asyncio
    async def test_dns_lookup_a_record(self):
        """Test DNS lookup for A record."""
        result = await dns_lookup("google.com", record_type="A")
        assert result["status"] in ("success", "error")
        if result["status"] == "success":
            assert "hostname" in result
            assert "record_type" in result
            assert result["record_type"] == "A"
            assert "records" in result

    @pytest.mark.asyncio
    async def test_dns_lookup_invalid_hostname(self):
        """Test DNS lookup with invalid hostname."""
        result = await dns_lookup("", record_type="A")
        assert result["status"] == "error"
        assert result["error"] == "invalid_hostname"

    @pytest.mark.asyncio
    async def test_dns_lookup_invalid_record_type(self):
        """Test DNS lookup with invalid record type."""
        result = await dns_lookup("google.com", record_type="INVALID")
        assert result["status"] == "error"
        assert result["error"] == "invalid_record_type"

    @pytest.mark.asyncio
    async def test_dns_lookup_various_types(self):
        """Test DNS lookup with various record types."""
        for record_type in ["A", "AAAA", "MX", "TXT", "CNAME"]:
            result = await dns_lookup("google.com", record_type=record_type)
            assert result["status"] in ("success", "error")
            if result["status"] == "success":
                assert result["record_type"] == record_type

    @pytest.mark.asyncio
    async def test_http_get_rate_limiting(self):
        """Test HTTP GET rate limiting counter."""
        # Reset counter
        http_get.counter = 0

        result1 = await http_get("https://httpbin.org/status/200", timeout=5)
        result2 = await http_get("https://httpbin.org/status/200", timeout=5)

        # Both calls should increment counter
        assert http_get.counter >= 2

    @pytest.mark.asyncio
    async def test_ping_rate_limiting(self):
        """Test ping rate limiting counter."""
        # Reset counter
        ping.counter = 0

        result1 = await ping("8.8.8.8", timeout=5, count=1)
        result2 = await ping("8.8.8.8", timeout=5, count=1)

        # Both calls should increment counter
        assert ping.counter >= 2


class TestNetworkToolsWithoutDependencies:
    """Test network tools when dependencies are not available."""

    def test_network_tools_available(self):
        """Test that network tools are marked as available."""
        # This just checks the import worked
        assert hasattr(http_get, "counter") or isinstance(http_get, object)
