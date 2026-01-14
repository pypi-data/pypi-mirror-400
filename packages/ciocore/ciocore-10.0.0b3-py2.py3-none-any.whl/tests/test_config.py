# -*- coding: utf-8 -*-
 
import unittest
import base64
import sys
import os
import logging

from unittest import mock

MOCK_API_KEY = '''{
    "type": "service_account",
    "project_id": "mock-project",
    "private_key_id": "mock-key-id",
    "private_key": "-----BEGIN PRIVATE KEY-----\\nMOCKKEY\\n-----END PRIVATE KEY-----\\n",
    "client_email": "mock@example.com",
    "client_id": "123456789",
    "auth_uri": "https://accounts.example.com/oauth2/auth",
    "token_uri": "https://oauth2.example.com/token",
    "auth_provider_x509_cert_url": "https://www.example.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.example.com/robot/v1/metadata/x509/mock%40example.com"
}'''

PY3 = sys.version_info >= (3, 0)
BUILTIN_OPEN = "builtins.open" if PY3 else "__builtin__.open"


from ciocore import config
from ciocore import loggeria


class ConfigInitTest(unittest.TestCase):
    def up(self, **overrides):
        """
        Call this setup before every test.

        It Mocks the 2 api_key functions, the multiprocessing package, and the os environment.
        """
        self.cpu_count_patcher = mock.patch(
            "os.cpu_count", return_value=overrides.get("cpu_count", 4)
        )
        self.mock_cpu_count = self.cpu_count_patcher.start()
        if overrides.get("cpu_count_raise", False):
            self.mock_cpu_count.side_effect = NotImplementedError()

        self.get_api_key_from_variable_patcher = mock.patch.object(
            config.Config,
            "get_api_key_from_variable",
            autospec=True,
            return_value=overrides.get("api_key_from_variable"),
        )
        self.mock_get_api_key_from_variable = self.get_api_key_from_variable_patcher.start()

        self.get_api_key_from_file_patcher = mock.patch.object(
            config.Config,
            "get_api_key_from_file",
            autospec=True,
            return_value=overrides.get("api_key_from_file"),
        )
        self.mock_get_api_key_from_file = self.get_api_key_from_file_patcher.start()

        self.env_patcher = mock.patch.dict("os.environ", overrides.get("env", {}))
        self.mock_env = self.env_patcher.start()

    def down(self):
        self.cpu_count_patcher.stop()
        self.get_api_key_from_variable_patcher.stop()
        self.get_api_key_from_file_patcher.stop()
        self.env_patcher.stop()

    def test_create(self):
        cfg = config.Config()
        self.assertEqual(cfg.__class__.__name__, "Config")

    # DOWNLOADER PAGE SIZE
    def test_downloader_page_size_default_to_50(self):
        self.up()
        cfg = config.Config()
        self.assertEqual(cfg.config["downloader_page_size"], 50)
        self.down()
        
    def test_downloader_page_size_variable_overrides_default(self):
        self.up(env={"CONDUCTOR_DOWNLOADER_PAGE_SIZE": "10"})
        cfg = config.Config()
        self.assertEqual(cfg.config["downloader_page_size"], 10)
        self.down()
        
        
    # THREAD COUNT
    def test_thread_count_is_cpu_count_minus_one(self):
        self.up(cpu_count=4)
        cfg = config.Config()
        self.assertEqual(cfg.config["thread_count"], 3)
        self.down()

    def test_thread_count_is_max_15(self):
        self.up(cpu_count=20)
        cfg = config.Config()
        self.assertEqual(cfg.config["thread_count"], 15)
        self.down()

    def test_thread_count_is_15_if_an_exception_is_thrown(self):
        self.up(cpu_count_raise=True)
        cfg = config.Config()
        self.assertEqual(cfg.config["thread_count"], 15)
        self.down()

    def test_thread_count_variable_overrides_default(self):
        self.up(env={"CONDUCTOR_THREAD_COUNT": "10"})
        cfg = config.Config()
        self.assertEqual(cfg.config["thread_count"], 10)
        self.down()

    # LOG LEVEL
    def test_log_level_default_to_INFO(self):
        self.up()
        cfg = config.Config()
        self.assertEqual(cfg.config["log_level"], "INFO")
        self.down()

    def test_log_level_variable_overrides_default(self):
        self.up(env={"CONDUCTOR_LOG_LEVEL": "DEBUG"})
        cfg = config.Config()
        self.assertEqual(cfg.config["log_level"], "DEBUG")
        self.down()

    def test_log_level_info_if_invalid_level_specified(self):
        self.up(env={"CONDUCTOR_LOG_LEVEL": "JUNK"})
        cfg = config.Config()
        self.assertEqual(cfg.config["log_level"], "INFO")
        self.down()

    # PRIORITY
    def test_priority_default_to_5(self):
        self.up()
        cfg = config.Config()
        self.assertEqual(cfg.config["priority"], 5)
        self.down()

    def test_priority_variable_overrides_default(self):
        self.up(env={"CONDUCTOR_PRIORITY": "3"})
        cfg = config.Config()
        self.assertEqual(cfg.config["priority"], 3)
        self.down()

    # MD5
    def test_md5_caching_default_to_true(self):
        self.up()
        cfg = config.Config()
        self.assertTrue(cfg.config["md5_caching"])
        self.down()

    def test_md5_caching_true_if_variable_set_and_is_truthy(self):
        self.up(env={"CONDUCTOR_MD5_CACHING": "TRUE"})
        cfg = config.Config()
        self.assertTrue(cfg.config["md5_caching"])
        self.down()

    def test_md5_caching_true_if_variable_set_and_is_a_mistake(self):
        self.up(env={"CONDUCTOR_MD5_CACHING": "UNKNOWN"})
        cfg = config.Config()
        self.assertTrue(cfg.config["md5_caching"])
        self.down()

    def test_md5_caching_false_if_variable_set_and_is_falsy(self):
        self.up(env={"CONDUCTOR_MD5_CACHING": "FALSE"})
        cfg = config.Config()
        self.assertFalse(cfg.config["md5_caching"])
        self.down()

    # URLS
    def test_project_url_defaults_to_dashboard(self):
        self.up()
        cfg = config.Config()
        expected = "https://dashboard.conductortech.com"
        self.assertEqual(cfg.config["url"], expected)
        self.down()

    def test_validate_project_url_from_variable_if_valid(self):
        self.up(env={"CONDUCTOR_URL": "https://dashboard.conductortech.com"})
        cfg = config.Config()
        expected = "https://dashboard.conductortech.com"
        self.assertEqual(cfg.config["url"], expected)
        self.down()

    def test_validate_project_url_from_variable_raises_if_invalid(self):
        self.up(env={"CONDUCTOR_URL": "htt://dashboard.conductortech.com"})
        with self.assertRaises(ValueError):
            config.Config()
        self.down()

    def test_validate_project_url_from_variable_raises_if_invalid_due_to_slack_quotes(self):
        self.up(env={"CONDUCTOR_URL": '“https://dashboard.dev-conductortech.com”'})
        with self.assertRaises(ValueError):
            config.Config()
        self.down()

    
    def test_validate_api_url_from_variable_raises_if_invalid_due_to_slack_quotes(self):
        self.up(env={"CONDUCTOR_API_URL": '“https://api.dev-conductortech.com”'})
        with self.assertRaises(ValueError):
            config.Config()
        self.down()

    def test_api_url_default_derived_from_url(self):
        something = "https://dashboard.something.com"
        self.up(env={"CONDUCTOR_URL": something})
        cfg = config.Config()
        expected = "https://api.something.com"
        self.assertEqual(cfg.config["api_url"], expected)
        self.down()

    # API KEY
    def test_api_key_none_if_none_from_variable_or_file(self):
        self.up()
        cfg = config.Config()
        self.assertEqual(cfg.config["api_key"], None)
        self.down()

    def test_api_key_variable_takes_priority(self):
        self.up(api_key_from_variable="a", api_key_from_file="b")
        cfg = config.Config()
        self.assertEqual(cfg.config["api_key"], "a")
        self.down()

    def test_api_key_set_from_file_if_variable_none(self):
        self.up(api_key_from_file="b")
        cfg = config.Config()
        self.assertEqual(cfg.config["api_key"], "b")
        self.down()

    # GET
    def test_config_method_returns_config_object(self):
        self.up()
        cfg = config.config()
        self.assertEqual(cfg.__class__.__name__, "Config")
        self.down()

    def test_config_returns_same_object_if_not_force(self):
        self.up()
        cfg0 = config.config()
        cfg1 = config.config()
        self.assertEqual(cfg0, cfg1)
        self.down()

    def test_config_returns_fresh_object_if_force(self):
        self.up()
        cfg0 = config.config()
        cfg1 = config.config(force=True)
        self.assertNotEqual(cfg0, cfg1)
        self.down()


class ApiKeyFromVariableTest(unittest.TestCase):
    def up(self, **overrides):
        """
        Mock the os env.
        """
        self.env_patcher = mock.patch.dict("os.environ", overrides.get("env", {}))
        self.mock_env = self.env_patcher.start()

    def down(self):
        self.env_patcher.stop()

    def test_returns_none_if_env_var_missing(self):
        self.up()
        result = config.Config.get_api_key_from_variable()
        self.assertEqual(result, None)
        self.down()

    def test_returns_dict_if_key_is_valid_json(self):
        self.up(env={"CONDUCTOR_API_KEY": '{"a":1}'})
        result = config.Config.get_api_key_from_variable()
        self.assertIsInstance(result, dict)
        self.down()

    def test_returns_dict_if_key_is_b64encoded(self):
        key = MOCK_API_KEY
        if sys.version_info < (3, 0):
            self.up(env={"CONDUCTOR_API_KEY": base64.b64encode(key)})
        else:
            self.up(
                env={"CONDUCTOR_API_KEY": base64.b64encode(key.encode("ascii")).decode("ascii")}
            )
        result = config.Config.get_api_key_from_variable()
        self.assertIsInstance(result, dict)
        self.down()

    def test_raises_if_key_is_unresolvable(self):
        self.up(env={"CONDUCTOR_API_KEY": "junk"})
        with self.assertRaises(ValueError):
            config.Config.get_api_key_from_variable()
        self.down()


class ApiKeyFromFileTest(unittest.TestCase):
    def up(self, **overrides):
        """
        Mock the os env.
        """
        self.env_patcher = mock.patch.dict("os.environ", overrides.get("env", {}))
        self.mock_env = self.env_patcher.start()

    def down(self):
        self.env_patcher.stop()

    def test_returns_none_if_api_key_path_env_var_missing(self):
        self.up()
        result = config.Config.get_api_key_from_file()
        self.assertEqual(result, None)
        self.down()

    @mock.patch(BUILTIN_OPEN, new_callable=mock.mock_open, read_data=MOCK_API_KEY, create=True)
    def test_open_called_with_api_key_path(self, mock_file_open):
        self.up(env={"CONDUCTOR_API_KEY_PATH": "path/to/api_key"})
        config.Config.get_api_key_from_file()
        mock_file_open.assert_called_with("path/to/api_key", "r")
        self.down()

    @mock.patch(BUILTIN_OPEN, new_callable=mock.mock_open, read_data="junk", create=True)
    def test_raises_if_key_is_unresolvable(self, mock_file_open):
        self.up(env={"CONDUCTOR_API_KEY_PATH": "path/to/api_key"})
        with self.assertRaises(ValueError):
            config.Config.get_api_key_from_file()
        self.down()

    @mock.patch(BUILTIN_OPEN, new_callable=mock.mock_open, read_data=MOCK_API_KEY, create=True)
    def test_returns_dict_if_key_is_valid_json(self, mock_file_open):
        self.up(env={"CONDUCTOR_API_KEY_PATH": "path/to/api_key"})
        result = config.Config.get_api_key_from_file()
        self.assertIsInstance(result, dict)
        self.down()
