import unittest
from unittest.mock import patch, MagicMock
import pytest

class TestAGClient(unittest.TestCase):
    
    @patch('antigranular_enterprise.client.AGClient')
    def test_login_success(self, MockAGClient):
        from antigranular_enterprise.client import login
        # Mocking AGClient initialization
        mock_instance = MockAGClient.return_value
        mock_instance.api_key = 'test_key'
        
        client = login(api_key='test_key')
        
        # Assertions
        MockAGClient.assert_called_once_with('test_key', 'default')
        self.assertEqual(client.api_key, 'test_key')
    
    @patch('antigranular_enterprise.client.AGClient')
    def test_login_failure(self, MockAGClient):
        from antigranular_enterprise.client import login
        # Simulate an exception when creating AGClient
        MockAGClient.side_effect = Exception('Connection failed')
        
        with self.assertRaises(ConnectionError) as context:
            login(api_key='invalid_key')
        
        # Assertions
        self.assertIn('Error while creating client', str(context.exception))

    @patch('antigranular_enterprise.client.config')
    def test_read_config(self, mock_config):
        from antigranular_enterprise.client import read_config
        # Test reading configuration
        read_config(profile='test_profile')
        mock_config.read_config.assert_called_once_with(profile='test_profile')

    @patch('antigranular_enterprise.client.config')
    def test_write_config(self, mock_config):
        from antigranular_enterprise.client import write_config
        # Test writing configuration
        yaml_config = {'key': 'value'}
        write_config(yaml_config, profile='test_profile')
        mock_config.write_config.assert_called_once_with(yaml_config, 'test_profile')

    @patch("antigranular_enterprise.client.get_ipython", side_effect=[True, True, None, None])
    @patch("requests.post")
    def test_agclient_test_init_with_ipython(self, mock_post, mock_ipython):
        
        from antigranular_enterprise.client import AGClient, write_config
        import json
        # Test AGClient initialization
        mock_response = MagicMock()
        mock_response.status_code = 200
        data = {"approval_status": "approved", "access_token": "access_token", "refresh_token": "refresh_token"}
        mock_response.iter_lines.return_value = [("data: "+json.dumps(data)).encode()]
        mock_post.return_value = mock_response
        
        mock_exec_response = MagicMock()
        mock_exec_response.status_code = 200
        data = {"session_id": "session_id"}
        mock_exec_response.text = json.dumps(data)
        with patch.object(AGClient, '_AGClient__exec', return_value=mock_exec_response) as mock_exec:
            write_config(profile='default', yaml_config="""
                agent_jupyter_url: <Jupyter URL>
                agent_jupyter_port: <Jupyter Port>
                agent_console_url: <Console URL>
                tls_enabled: true
                """)
            client = AGClient("apikey", "default")

        assert client.session_id == "session_id"
        
    @patch("antigranular_enterprise.client.get_ipython", side_effect=[False, True, None, None])
    @patch("requests.get")
    def test_agclient_test_init_without_ipython(self, mock_get, mock_ipython):
        
        from antigranular_enterprise.client import AGClient, write_config
        import json
        # Test AGClient initialization
        mock_response = MagicMock()
        mock_response.status_code = 200
        data = {"approval_status": "approved", "access_token": "access_token", "refresh_token": "refresh_token"}
        mock_response.iter_lines.return_value = [("data: "+json.dumps(data)).encode()]
        mock_get.return_value = mock_response
        
        mock_exec_response = MagicMock()
        mock_exec_response.status_code = 200
        data = {"session_id": "session_id"}
        mock_exec_response.text = json.dumps(data)
        with patch.object(AGClient, '_AGClient__exec', return_value=mock_exec_response) as mock_exec:
            write_config(profile='default', yaml_config="""
                agent_jupyter_url: <Jupyter URL>
                agent_jupyter_port: <Jupyter Port>
                agent_console_url: <Console URL>
                tls_enabled: true
                """)
            client = AGClient("apikey", "default")

        assert client.session_id == "session_id"
    
    
    @patch("antigranular_enterprise.client.get_ipython", side_effect=[False, True, None, None])
    @patch("requests.get")
    def test_interrupt_kernel(self, mock_get, mock_ipython):
        from antigranular_enterprise.client import AGClient, write_config
        import json
        # Test AGClient initialization
        mock_response = MagicMock()
        mock_response.status_code = 200
        data = {"approval_status": "approved", "access_token": "access_token", "refresh_token": "refresh_token"}
        mock_response.iter_lines.return_value = [("data: "+json.dumps(data)).encode()]
        mock_get.return_value = mock_response
        
        mock_exec_response1 = MagicMock()
        mock_exec_response1.status_code = 200
        data = {"session_id": "session_id"}
        mock_exec_response1.text = json.dumps(data)
        
        mock_exec_response2 = MagicMock()
        mock_exec_response2.status_code = 200
        data = {"success": "ok"}
        mock_exec_response2.text = json.dumps(data)
        
        with patch.object(AGClient, '_AGClient__exec', side_effect=[mock_exec_response1, mock_exec_response2, mock_exec_response2]) as mock_exec:
            write_config(profile='default', yaml_config="""
                agent_jupyter_url: <Jupyter URL>
                agent_jupyter_port: <Jupyter Port>
                agent_console_url: <Console URL>
                tls_enabled: true
                """)
            client = AGClient("apikey", "default")
            resp = client.interrupt_kernel()
        
        assert resp["success"] == "ok"
        # Mocking interrupt kernel

    @patch("antigranular_enterprise.client.get_ipython", side_effect=[False, True, None, None])
    @patch("requests.get")
    @patch("requests.delete")
    def test_terminate_session(self, mock_delete, mock_get, mock_ipython):
        from antigranular_enterprise.client import AGClient, write_config
        import json
        # Test AGClient initialization
        mock_response = MagicMock()
        mock_response.status_code = 200
        data = {"approval_status": "approved", "access_token": "access_token", "refresh_token": "refresh_token"}
        mock_response.iter_lines.return_value = [("data: "+json.dumps(data)).encode()]
        mock_get.return_value = mock_response
        
        mock_delete_response = MagicMock()
        mock_delete.return_value = mock_delete_response
        
        mock_exec_response1 = MagicMock()
        mock_exec_response1.status_code = 200
        data = {"session_id": "session_id"}
        mock_exec_response1.text = json.dumps(data)
        
        mock_exec_response2 = MagicMock()
        mock_exec_response2.status_code = 200
        data = {'status': 'terminated'}
        mock_exec_response2.text = json.dumps(data)
                
        with patch.object(AGClient, '_AGClient__exec', side_effect=[mock_exec_response1, mock_exec_response2, mock_exec_response2]) as mock_exec:
            write_config(profile='default', yaml_config="""
                agent_jupyter_url: <Jupyter URL>
                agent_jupyter_port: <Jupyter Port>
                agent_console_url: <Console URL>
                tls_enabled: true
                """)
            client = AGClient("apikey", "default")
            result = client.terminate_session()
        
        # Assertions
        self.assertEqual(result['status'], 'terminated')
    
    @patch("antigranular_enterprise.client.get_ipython", side_effect=[False, True, None, None])
    @patch("requests.get")
    def test_privacy_odometer(self, mock_get, mock_ipython):
        from antigranular_enterprise.client import AGClient, write_config
        import json
        # Test AGClient initialization
        mock_response = MagicMock()
        mock_response.status_code = 200
        data = {"approval_status": "approved", "access_token": "access_token", "refresh_token": "refresh_token"}
        mock_response.iter_lines.return_value = [("data: "+json.dumps(data)).encode()]
        mock_get.return_value = mock_response
        
        mock_exec_response1 = MagicMock()
        mock_exec_response1.status_code = 200
        data = {"session_id": "session_id"}
        mock_exec_response1.text = json.dumps(data)
        
        mock_exec_response2 = MagicMock()
        mock_exec_response2.status_code = 200
        data = {'privacy_budget': 100}
        mock_exec_response2.text = json.dumps(data)
        
        with patch.object(AGClient, '_AGClient__exec', side_effect=[mock_exec_response1, mock_exec_response2, mock_exec_response2]) as mock_exec:
            write_config(profile='default', yaml_config="""
                agent_jupyter_url: <Jupyter URL>
                agent_jupyter_port: <Jupyter Port>
                agent_console_url: <Console URL>
                tls_enabled: true
                """)
            client = AGClient("apikey", "default")
            result = client.privacy_odometer()
        
        # Assertions
        self.assertEqual(result, None)



if __name__ == '__main__':
    unittest.main()
