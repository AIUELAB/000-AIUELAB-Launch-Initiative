#!/usr/bin/env python3
"""
main.pyのテストモジュール
"""

import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

# srcディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import AppConfig, Application, calculate_sum, cli, validate_email


class TestAppConfig:
    """AppConfigクラスのテスト"""

    def test_from_env_default_values(self):
        """デフォルト値でのAppConfig生成をテスト"""
        with patch.dict(os.environ, {}, clear=True):
            config = AppConfig.from_env()

            assert config.app_name == "Claude Code MCP Template"
            assert config.version == "1.0.0"
            assert config.debug is False
            assert config.environment == "development"

    def test_from_env_with_custom_values(self):
        """カスタム環境変数でのAppConfig生成をテスト"""
        env_vars = {
            "APP_NAME": "Test App",
            "APP_VERSION": "2.0.0",
            "DEBUG": "true",
            "ENVIRONMENT": "production",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = AppConfig.from_env()

            assert config.app_name == "Test App"
            assert config.version == "2.0.0"
            assert config.debug is True
            assert config.environment == "production"


class TestApplication:
    """Applicationクラスのテスト"""

    @pytest.fixture
    def app_config(self):
        """テスト用のAppConfigを作成"""
        return AppConfig(
            app_name="Test App", 
            version="1.0.0", 
            debug=False, 
            environment="test",
            mcp_enabled=False
        )

    @pytest.fixture
    def app(self, app_config):
        """テスト用のApplicationインスタンスを作成"""
        return Application(app_config)

    def test_initialization(self, app_config):
        """Applicationの初期化をテスト"""
        app = Application(app_config)
        assert app.config == app_config

    def test_process_data(self, app):
        """process_dataメソッドをテスト"""
        result = app.process_data()

        assert result["status"] == "success"
        assert result["items_processed"] == 42
        assert "successfully" in result["message"]

    @patch("main.console")
    def test_display_info(self, mock_console, app):
        """display_infoメソッドをテスト"""
        app.display_info()

        # consoleのprintメソッドが呼ばれたことを確認
        mock_console.print.assert_called()

    @patch("main.logger")
    def test_run(self, mock_logger, app):
        """runメソッドをテスト"""
        with patch.object(app, "display_info") as mock_display:
            with patch.object(app, "check_mcp_status") as mock_check_mcp:
                with patch.object(app, "process_data") as mock_process:
                    app.run()

                    # 各メソッドが呼ばれたことを確認
                    mock_display.assert_called_once()
                    mock_check_mcp.assert_called_once()
                    mock_process.assert_called_once()

                    # ログが記録されたことを確認
                    assert mock_logger.info.call_count >= 2


class TestUtilityFunctions:
    """ユーティリティ関数のテスト"""

    @pytest.mark.parametrize(
        "numbers, expected",
        [
            ([1, 2, 3], 6),
            ([0], 0),
            ([-1, 1], 0),
            ([1.5, 2.5], 4.0),
            ([], 0),
        ],
    )
    def test_calculate_sum(self, numbers, expected):
        """calculate_sum関数をテスト"""
        assert calculate_sum(numbers) == expected

    @pytest.mark.parametrize(
        "email, expected",
        [
            ("test@example.com", True),
            ("user.name@domain.co.jp", True),
            ("invalid.email", False),
            ("@example.com", False),
            ("user@", False),
            ("", False),
            ("user name@example.com", False),
        ],
    )
    def test_validate_email(self, email, expected):
        """validate_email関数をテスト"""
        assert validate_email(email) == expected


class TestCLI:
    """CLIコマンドのテスト"""

    @pytest.fixture
    def runner(self):
        """CLIテスト用のRunnerを作成"""
        return CliRunner()

    def test_cli_version(self, runner):
        """バージョン表示をテスト"""
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "1.0.0" in result.output

    @patch("main.Application")
    def test_run_command(self, mock_app_class, runner):
        """runコマンドをテスト"""
        mock_app = Mock()
        mock_app_class.return_value = mock_app

        result = runner.invoke(cli, ["run"])

        assert result.exit_code == 0
        mock_app.run.assert_called_once()

    @patch("main.Application")
    def test_run_command_with_debug(self, mock_app_class, runner):
        """debugフラグ付きrunコマンドをテスト"""
        mock_app = Mock()
        mock_app_class.return_value = mock_app

        result = runner.invoke(cli, ["run", "--debug"])

        assert result.exit_code == 0
        mock_app.run.assert_called_once()

    @patch("main.Application")
    def test_info_command(self, mock_app_class, runner):
        """infoコマンドをテスト"""
        mock_app = Mock()
        mock_app_class.return_value = mock_app

        result = runner.invoke(cli, ["info"])

        assert result.exit_code == 0
        mock_app.display_info.assert_called_once()
        mock_app.check_mcp_status.assert_called_once()

    def test_sum_command(self, runner):
        """sumコマンドをテスト"""
        result = runner.invoke(cli, ["sum", "1", "2", "3"])

        assert result.exit_code == 0
        assert "6" in result.output

    def test_sum_command_no_args(self, runner):
        """引数なしのsumコマンドをテスト"""
        result = runner.invoke(cli, ["sum"])

        assert result.exit_code == 0
        assert "No numbers provided" in result.output

    def test_validate_command_valid(self, runner):
        """有効なメールでのvalidateコマンドをテスト"""
        result = runner.invoke(cli, ["validate", "test@example.com"])

        assert result.exit_code == 0
        assert "is valid" in result.output

    def test_validate_command_invalid(self, runner):
        """無効なメールでのvalidateコマンドをテスト"""
        result = runner.invoke(cli, ["validate", "invalid.email"])

        assert result.exit_code == 0
        assert "is invalid" in result.output


@pytest.fixture(autouse=True)
def reset_environment():
    """各テストの前後で環境をリセット"""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
