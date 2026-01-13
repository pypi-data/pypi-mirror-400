import pytest
from surfgeo.payload import (
    build_payload,
    normalize_path,
    extract_user_agent,
    extract_referrer
)
from surfgeo.types import RequestMetadata


class TestPayloadBuilder:
    def test_build_payload_includes_required_fields(self):
        """Should include timestamp, path, method, user_agent"""
        metadata: RequestMetadata = {
            'path': '/test',
            'method': 'GET',
            'headers': {'User-Agent': 'test-agent'},
            'status_code': 200
        }
        
        payload = build_payload(metadata)
        
        assert 'timestamp' in payload
        assert payload['path'] == '/test'
        assert payload['method'] == 'GET'
        assert payload['user_agent'] == 'test-agent'
        assert payload['status_code'] == 200

    def test_build_payload_generates_request_id(self):
        """Should generate UUID for request_id"""
        metadata: RequestMetadata = {
            'path': '/test',
            'method': 'GET',
            'headers': {}
        }
        
        payload = build_payload(metadata)
        
        assert 'request_id' in payload
        assert len(payload['request_id']) > 0

    def test_normalize_path_removes_query_string(self):
        """Should strip query parameters"""
        assert normalize_path('/test?page=1') == '/test'
        assert normalize_path('/api/users?id=123') == '/api/users'

    def test_normalize_path_removes_trailing_slash(self):
        """Should remove trailing slash (except root)"""
        assert normalize_path('/test/') == '/test'
        assert normalize_path('/') == '/'
        assert normalize_path('/api/users/') == '/api/users'

    def test_extract_user_agent_handles_missing(self):
        """Should return 'Unknown' if header missing"""
        assert extract_user_agent({}) == 'Unknown'

    def test_extract_user_agent_handles_list(self):
        """Should handle list values"""
        headers = {'User-Agent': ['Mozilla/5.0', 'Chrome/1.0']}
        assert extract_user_agent(headers) == 'Mozilla/5.0'

    def test_extract_referrer_returns_none_if_missing(self):
        """Should return None if Referer missing"""
        assert extract_referrer({}) is None

    def test_extract_referrer_handles_different_casings(self):
        """Should handle different header casings"""
        assert extract_referrer({'Referer': 'https://example.com'}) == 'https://example.com'
        assert extract_referrer({'referer': 'https://example.com'}) == 'https://example.com'
        assert extract_referrer({'REFERER': 'https://example.com'}) == 'https://example.com'

