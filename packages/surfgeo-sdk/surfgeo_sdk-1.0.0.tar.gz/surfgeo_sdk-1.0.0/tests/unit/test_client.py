import pytest
import time
import asyncio
from unittest.mock import patch, MagicMock
from surfgeo.client import surfgeoClient, surfgeoConfig


class TestSurfGeoClient:
    def test_init_with_valid_config(self):
        """Should initialize with valid config"""
        config = surfgeoConfig(script_key='sk_test_key_123456789012345')
        client = surfgeoClient(config)
        assert client is not None
        assert client.config.script_key == 'sk_test_key_123456789012345'

    def test_init_raises_on_missing_script_key(self):
        """Should raise ValueError if script_key missing"""
        with pytest.raises(ValueError, match='script_key is required'):
            config = surfgeoConfig(script_key='')
            surfgeoClient(config)

    def test_init_validates_script_key_format(self):
        """Should validate script_key starts with sk_"""
        with pytest.raises(ValueError, match='must start with "sk_"'):
            config = surfgeoConfig(script_key='invalid_key')
            surfgeoClient(config)

    @patch('surfgeo.client.requests.post')
    def test_track_adds_script_key_and_source(self, mock_post):
        """Should add script_key and source='server' to payload"""
        config = surfgeoConfig(script_key='sk_test_key_123456789012345')
        client = surfgeoClient(config)
        
        payload = {'path': '/test', 'method': 'GET', 'user_agent': 'test'}
        client.track(payload)
        
        # Wait for thread to complete
        time.sleep(0.1)
        
        assert mock_post.called
        call_args = mock_post.call_args
        sent_payload = call_args[1]['json']
        assert sent_payload['script_key'] == 'sk_test_key_123456789012345'
        assert sent_payload['source'] == 'server'

    def test_track_doesnt_block(self):
        """Should return immediately without waiting"""
        config = surfgeoConfig(script_key='sk_test_key_123456789012345')
        client = surfgeoClient(config)
        
        start = time.time()
        client.track({'path': '/test', 'method': 'GET', 'user_agent': 'test'})
        elapsed = time.time() - start
        
        # Should return immediately (< 10ms)
        assert elapsed < 0.01

    def test_track_respects_enabled_flag(self):
        """Should skip tracking if enabled=False"""
        config = surfgeoConfig(
            script_key='sk_test_key_123456789012345',
            enabled=False
        )
        client = surfgeoClient(config)
        
        with patch('surfgeo.client.requests.post') as mock_post:
            client.track({'path': '/test', 'method': 'GET', 'user_agent': 'test'})
            time.sleep(0.1)
            assert not mock_post.called

    @patch('surfgeo.client.requests.post')
    def test_track_handles_network_error_silently(self, mock_post):
        """Should not raise on network error"""
        mock_post.side_effect = Exception('Network error')
        
        config = surfgeoConfig(script_key='sk_test_key_123456789012345')
        client = surfgeoClient(config)
        
        # Should not raise
        client.track({'path': '/test', 'method': 'GET', 'user_agent': 'test'})
        time.sleep(0.1)

    @pytest.mark.asyncio
    async def test_track_async_creates_task(self):
        """Should create asyncio task"""
        config = surfgeoConfig(script_key='sk_test_key_123456789012345')
        client = surfgeoClient(config)
        
        with patch('surfgeo.client.httpx.AsyncClient') as mock_client:
            await client.track_async({'path': '/test', 'method': 'GET', 'user_agent': 'test'})
            # Give task time to start
            await asyncio.sleep(0.1)

