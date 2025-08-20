#!/usr/bin/env python3
"""
エラーリカバリーモジュール
エラーハンドリングとクラッシュからの自動復旧機能を提供
"""

import functools
import sys
import time
import traceback
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import TypeVar

from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from session_manager import get_session_manager

console = Console()

T = TypeVar("T")


class ErrorRecovery:
    """エラーリカバリークラス"""

    def __init__(self, max_retries: int = 3, retry_delay: int = 1) -> None:
        """
        エラーリカバリーの初期化

        Args:
            max_retries: 最大リトライ回数
            retry_delay: リトライ間隔（秒）
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.error_log_file = Path(".sessions/error_log.txt")
        self.error_log_file.parent.mkdir(exist_ok=True)
        self.session_manager = get_session_manager()

    def log_error(self, error: Exception, context: str = "") -> None:
        """
        エラーをログに記録

        Args:
            error: エラーオブジェクト
            context: エラーのコンテキスト
        """
        timestamp = datetime.now().isoformat()
        error_info = {
            "timestamp": timestamp,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "traceback": traceback.format_exc(),
        }

        # セッションに記録
        current = self.session_manager.get("errors", [])
        errors_list = current if isinstance(current, list) else []
        errors_list.append(error_info)
        self.session_manager.set("errors", errors_list[-100:])  # 最新100件を保持

        # ファイルに記録
        with open(self.error_log_file, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Context: {context}\n")
            f.write(f"Error: {error_info['error_type']}: {error_info['error_message']}\n")
            f.write(f"Traceback:\n{error_info['traceback']}\n")

        logger.error(f"[{context}] {error_info['error_type']}: {error_info['error_message']}")

    def display_error(
        self, error: Exception, context: str = "", show_traceback: bool = False
    ) -> None:
        """
        エラーを見やすく表示

        Args:
            error: エラーオブジェクト
            context: エラーのコンテキスト
            show_traceback: トレースバックを表示するか
        """
        error_text = Text()
        error_text.append("⚠️ Error: ", style="bold red")
        error_text.append(f"{type(error).__name__}\n", style="red")
        error_text.append("Message: ", style="bold")
        error_text.append(f"{error!s}\n")

        if context:
            error_text.append("Context: ", style="bold")
            error_text.append(f"{context}\n")

        if show_traceback:
            error_text.append("\nTraceback:\n", style="bold")
            error_text.append(traceback.format_exc(), style="dim")

        panel = Panel(
            error_text,
            title="[bold red]Error Occurred[/bold red]",
            border_style="red",
            expand=False,
        )
        console.print(panel)

    def recover_from_error(
        self, _error: Exception, recovery_action: Callable | None = None
    ) -> bool:
        """
        エラーから復旧を試みる

        Args:
            error: エラーオブジェクト
            recovery_action: 復旧アクション

        Returns:
            復旧に成功した場合True
        """
        logger.info("Attempting error recovery...")

        # セッションマネージャーからの復旧
        if self.session_manager.restore_session():
            logger.success("Session restored successfully")

            if recovery_action:
                try:
                    recovery_action()
                    logger.success("Recovery action completed")
                    return True
                except Exception as e:
                    logger.error(f"Recovery action failed: {e}")
                    return False

            return True

        logger.error("Failed to recover from error")
        return False


def with_retry(max_retries: int = 3, delay: int = 1, backoff: float = 2.0):
    """
    リトライデコレーター

    Args:
        max_retries: 最大リトライ回数
        delay: 初期遅延時間（秒）
        backoff: バックオフ係数
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception: Exception | None = None
            current_delay: float = float(delay)

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                            f"Retrying in {current_delay} seconds..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed")

            if last_exception:
                raise last_exception

            # Should be unreachable, but helps type checkers
            raise AssertionError("with_retry wrapper reached unreachable state")

        return wrapper

    return decorator


def safe_execute(func: Callable[..., T], *args, **kwargs) -> T | None:
    """
    安全に関数を実行

    Args:
        func: 実行する関数
        *args: 位置引数
        **kwargs: キーワード引数

    Returns:
        関数の戻り値、エラーの場合はNone
    """
    recovery = ErrorRecovery()

    try:
        return func(*args, **kwargs)
    except Exception as e:
        recovery.log_error(e, context=f"Function: {func.__name__}")
        recovery.display_error(e, context=func.__name__)
        return None


class ErrorHandler:
    """コンテキストマネージャー型エラーハンドラー"""

    def __init__(
        self,
        context: str = "",
        suppress: bool = False,
        show_traceback: bool = False,
        recovery_action: Callable | None = None,
    ):
        """
        エラーハンドラーの初期化

        Args:
            context: エラーコンテキスト
            suppress: エラーを抑制するか
            show_traceback: トレースバックを表示するか
            recovery_action: 復旧アクション
        """
        self.context = context
        self.suppress = suppress
        self.show_traceback = show_traceback
        self.recovery_action = recovery_action
        self.recovery = ErrorRecovery()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.recovery.log_error(exc_val, self.context)
            self.recovery.display_error(exc_val, self.context, self.show_traceback)

            # 復旧を試みる
            if self.recovery_action:
                if self.recovery.recover_from_error(exc_val, self.recovery_action):
                    logger.success("Error recovery successful")
                else:
                    logger.error("Error recovery failed")

            return self.suppress


def setup_global_exception_handler():
    """グローバル例外ハンドラーの設定"""

    def exception_handler(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # Ctrl+Cは通常通り処理
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        recovery = ErrorRecovery()
        recovery.log_error(exc_value, context="Global Exception")
        recovery.display_error(exc_value, context="Unhandled Exception", show_traceback=True)

        # セッションを保存
        session_manager = get_session_manager()
        session_manager.create_checkpoint("crash_recovery")
        session_manager.save_session()

        console.print("\n[yellow]Session saved. You can restore it on next run.[/yellow]")

    sys.excepthook = exception_handler


# 一般的なエラーに対する復旧アクション
RECOVERY_ACTIONS = {
    FileNotFoundError: lambda e: logger.info(
        f"File not found: {e}. Creating necessary directories..."
    ),
    PermissionError: lambda e: logger.info(f"Permission denied: {e}. Check file permissions."),
    ConnectionError: lambda e: logger.info(f"Connection error: {e}. Check network connection."),
    KeyError: lambda e: logger.info(f"Key error: {e}. Check configuration."),
    ValueError: lambda e: logger.info(f"Value error: {e}. Check input values."),
}


def get_recovery_action(error: Exception) -> Callable | None:
    """
    エラータイプに応じた復旧アクションを取得

    Args:
        error: エラーオブジェクト

    Returns:
        復旧アクション関数
    """
    error_type = type(error)
    return RECOVERY_ACTIONS.get(error_type)


# デコレーター: エラーハンドリング付き関数
def error_handler(context: str = "", suppress: bool = False, show_traceback: bool = False):
    """
    エラーハンドリングデコレーター

    Args:
        context: エラーコンテキスト
        suppress: エラーを抑制するか
        show_traceback: トレースバックを表示するか
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T | None]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T | None:
            with ErrorHandler(
                context=context or func.__name__, suppress=suppress, show_traceback=show_traceback
            ):
                return func(*args, **kwargs)

        return wrapper

    return decorator


if __name__ == "__main__":
    # テスト実行
    setup_global_exception_handler()

    # リトライデコレーターのテスト
    @with_retry(max_retries=2, delay=0.5)
    def flaky_function():
        import random

        if random.random() > 0.5:
            raise ConnectionError("Random connection error")
        return "Success!"

    # エラーハンドラーのテスト
    with ErrorHandler(context="Test", suppress=True, show_traceback=True):
        raise ValueError("Test error")

    # 安全実行のテスト
    result = safe_execute(lambda x: 10 / x, 0)
    print(f"Result: {result}")

    # デコレーターのテスト
    @error_handler(context="Division", suppress=True)
    def divide(a, b):
        return a / b

    result = divide(10, 0)
    print(f"Division result: {result}")
