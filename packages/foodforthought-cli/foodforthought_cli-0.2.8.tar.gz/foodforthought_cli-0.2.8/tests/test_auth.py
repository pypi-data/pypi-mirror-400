import unittest
from unittest.mock import patch, mock_open, MagicMock
import sys
import os
import json
import io
from pathlib import Path

# Add parent directory to path to import ate
sys.path.append(str(Path(__file__).parent.parent))

from ate.cli import ATEClient, login_command, CONFIG_FILE

class TestATEAuth(unittest.TestCase):
    def setUp(self):
        # Reset environment variables before each test
        if "ATE_API_KEY" in os.environ:
            del os.environ["ATE_API_KEY"]
            
    def tearDown(self):
        if "ATE_API_KEY" in os.environ:
            del os.environ["ATE_API_KEY"]

    @patch("ate.cli.CONFIG_FILE")
    def test_client_init_env_var_priority(self, mock_config_file):
        """Test that environment variable takes priority over config file"""
        os.environ["ATE_API_KEY"] = "ate_env_key"
        
        # Mock config file existence and content to ensure it would be read if env var wasn't set
        mock_config_file.exists.return_value = True
        with patch("builtins.open", mock_open(read_data='{"api_key": "ate_file_key"}')):
            client = ATEClient()
            self.assertEqual(client.headers["Authorization"], "Bearer ate_env_key")

    @patch("ate.cli.CONFIG_FILE")
    def test_client_init_config_file(self, mock_config_file):
        """Test that config file is used when env var is missing"""
        mock_config_file.exists.return_value = True
        
        with patch("builtins.open", mock_open(read_data='{"api_key": "ate_file_key"}')):
            client = ATEClient()
            self.assertEqual(client.headers["Authorization"], "Bearer ate_file_key")

    @patch("ate.cli.CONFIG_FILE")
    def test_client_init_no_auth(self, mock_config_file):
        """Test fallback when no auth is present"""
        mock_config_file.exists.return_value = False
        
        # Capture stdout/stderr to check for warning
        with patch("sys.stderr", new=io.StringIO()) as fake_stderr:
            client = ATEClient()
            self.assertNotIn("Authorization", client.headers)
            self.assertIn("Warning: No API key found", fake_stderr.getvalue())

    @patch("ate.cli.CONFIG_FILE")
    @patch("ate.cli.CONFIG_DIR")
    @patch("getpass.getpass")
    def test_login_command_success(self, mock_getpass, mock_config_dir, mock_config_file):
        """Test successful login flow"""
        mock_getpass.return_value = "ate_new_key"
        mock_config_file.exists.return_value = False
        
        with patch("builtins.open", mock_open()) as mock_file:
            # Mock json.dump to verify what's written
            with patch("json.dump") as mock_json_dump:
                login_command()
                
                # Verify config dir created
                mock_config_dir.mkdir.assert_called_with(parents=True, exist_ok=True)
                
                # Verify file opened for writing
                mock_file.assert_called_with(mock_config_file, "w")
                
                # Verify correct json written
                mock_json_dump.assert_called()
                args, _ = mock_json_dump.call_args
                self.assertEqual(args[0], {"api_key": "ate_new_key"})

    @patch("getpass.getpass")
    def test_login_command_invalid_key_abort(self, mock_getpass):
        """Test login aborts on invalid key format if user says no"""
        mock_getpass.return_value = "invalid_format_key"
        
        with patch("builtins.input", return_value="n"):
            with self.assertRaises(SystemExit):
                login_command()

if __name__ == "__main__":
    unittest.main()
