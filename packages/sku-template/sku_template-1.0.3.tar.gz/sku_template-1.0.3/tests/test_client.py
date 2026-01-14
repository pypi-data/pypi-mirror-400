"""
Tests for AppID Manager Client
"""
import pytest
import requests
from unittest.mock import Mock, patch
from sku_template import AppIdClient


class TestAppIdClient:
    """Test cases for AppIdClient"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.client = AppIdClient("http://test-server:5000",auth_token="test_auth_token", timeout=5)
    
    def test_init(self):
        """Test client initialization"""
        client = AppIdClient("http://example.com", auth_token="test_auth_token", timeout=10)
        assert client.base_url == "http://example.com"
        assert client.timeout == 10
    
    def test_init_with_trailing_slash(self):
        """Test client initialization with trailing slash"""
        client = AppIdClient("http://example.com/", auth_token="test_auth_token", timeout=10)
        assert client.base_url == "http://example.com"
    
    @patch('requests.post')
    def test_acquire_appid_success(self, mock_post):
        """Test successful AppID acquisition""" 
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "appid": "test_appid",
            "vid": "test_vid",
            "starttime": 1234567890,
            "productName": "test_product"
        }
        mock_post.return_value = mock_response
        
        appid, vid, start_time, product_name = self.client.acquire_appid("test_product")
        
        assert appid == "test_appid"
        assert vid == "test_vid"
        assert start_time == 1234567890
        assert product_name == "test_product"
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_acquire_appid_waiting(self, mock_post):
        """Test AppID acquisition with waiting"""
        mock_response = Mock()
        mock_response.status_code = 202
        mock_response.json.return_value = {
            "error": "waiting",
            "message": "All appids in use",
            "retry_after": 60
        }
        mock_post.return_value = mock_response
        
        with pytest.raises(Exception):
            self.client.acquire_appid("test_product", max_retries=1)
    
    def test_acquire_appid_empty_product_name(self):
        """Test AppID acquisition with empty product name"""
        with pytest.raises(ValueError, match="product_name is required"):
            self.client.acquire_appid("")
    
    @patch('requests.post')
    def test_release_appid_success(self, mock_post):
        """Test successful AppID release"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"stoptime": 1234567890}
        mock_post.return_value = mock_response
        
        result = self.client.release_appid("test_appid", "test_product")
        
        assert result is True
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_release_appid_failure(self, mock_post):
        """Test AppID release failure"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "AppID not found"}
        mock_post.return_value = mock_response
        
        with pytest.raises(Exception):
            self.client.release_appid("test_appid", "test_product")
    
    def test_release_appid_empty_product_name(self):
        """Test AppID release with empty product name"""
        with pytest.raises(ValueError, match="product_name is required"):
            self.client.release_appid("test_appid", "")
    
    @patch('requests.get')
    def test_get_status_success(self, mock_get):
        """Test successful status retrieval"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"total": 10, "available": 5}
        mock_get.return_value = mock_response
        
        status = self.client.get_status("test_product")
        
        assert status == {"total": 10, "available": 5}
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_get_status_failure(self, mock_get):
        """Test status retrieval failure"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        status = self.client.get_status("test_product")
        
        assert status is None
    
    @patch('requests.post')
    def test_init_product_success(self, mock_post):
        """Test successful product initialization"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Product initialized"}
        mock_post.return_value = mock_response
        
        result = self.client.init_product("test_product", {"appid1": "vid1"})
        
        assert result is True
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_init_product_failure(self, mock_post):
        """Test product initialization failure"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Invalid config"}
        mock_post.return_value = mock_response
        
        with pytest.raises(Exception):
            self.client.init_product("test_product", {"appid1": "vid1"})
    
    @patch('requests.get')
    def test_health_check_success(self, mock_get):
        """Test successful health check"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = self.client.health_check()
        
        assert result is True
    
    @patch('requests.get')
    def test_health_check_failure(self, mock_get):
        """Test health check failure"""
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        result = self.client.health_check()
        
        assert result is False
    
    @patch('requests.post')
    def test_acquire_appid_timeout(self, mock_post):
        """Test AppID acquisition timeout"""
        mock_post.side_effect = requests.exceptions.Timeout()
        
        with pytest.raises(Exception):
            self.client.acquire_appid("test_product", max_retries=1)
    
    @patch('requests.post')
    def test_acquire_appid_connection_error(self, mock_post):
        """Test AppID acquisition connection error"""
        mock_post.side_effect = requests.exceptions.ConnectionError()
        
        with pytest.raises(Exception):
            self.client.acquire_appid("test_product", max_retries=1)
