#!/usr/bin/env python3
"""
セッション管理モジュール
作業状態の保存と復元、クラッシュリカバリー機能を提供
"""

import json
import os
import pickle
import signal
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from loguru import logger


class SessionManager:
    """セッション管理クラス"""
    
    def __init__(self, session_dir: str = ".sessions"):
        """
        セッションマネージャーの初期化
        
        Args:
            session_dir: セッションファイルを保存するディレクトリ
        """
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(exist_ok=True)
        self.session_file = self.session_dir / "current_session.json"
        self.backup_dir = self.session_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        self.session_data: Dict[str, Any] = {}
        self.auto_save_interval = 60  # 秒
        self.auto_save_thread: Optional[threading.Thread] = None
        self.stop_auto_save = threading.Event()
        
        # シグナルハンドラーの設定（クラッシュ対策）
        self._setup_signal_handlers()
        
        # 前回のセッションを復元
        self.restore_session()
    
    def _setup_signal_handlers(self):
        """シグナルハンドラーの設定"""
        def signal_handler(signum, frame):
            logger.warning(f"Signal {signum} received, saving session...")
            self.save_session()
            sys.exit(0)
        
        # 各種シグナルに対してハンドラーを設定
        signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
        signal.signal(signal.SIGTERM, signal_handler)  # kill
        
        # Windowsではこれらのシグナルは使用できない
        if hasattr(signal, 'SIGHUP'):
            signal.signal(signal.SIGHUP, signal_handler)  # ハングアップ
        if hasattr(signal, 'SIGQUIT'):
            signal.signal(signal.SIGQUIT, signal_handler)  # Quit
    
    def start_auto_save(self):
        """自動保存を開始"""
        if self.auto_save_thread and self.auto_save_thread.is_alive():
            logger.warning("Auto-save is already running")
            return
        
        self.stop_auto_save.clear()
        self.auto_save_thread = threading.Thread(target=self._auto_save_worker, daemon=True)
        self.auto_save_thread.start()
        logger.info(f"Auto-save started (interval: {self.auto_save_interval}s)")
    
    def stop_auto_save_thread(self):
        """自動保存を停止"""
        self.stop_auto_save.set()
        if self.auto_save_thread:
            self.auto_save_thread.join(timeout=5)
        logger.info("Auto-save stopped")
    
    def _auto_save_worker(self):
        """自動保存ワーカースレッド"""
        while not self.stop_auto_save.is_set():
            time.sleep(self.auto_save_interval)
            if not self.stop_auto_save.is_set():
                self.save_session(is_auto_save=True)
    
    def save_session(self, is_auto_save: bool = False):
        """
        セッションを保存
        
        Args:
            is_auto_save: 自動保存かどうか
        """
        try:
            # タイムスタンプを追加
            self.session_data['last_saved'] = datetime.now().isoformat()
            self.session_data['is_auto_save'] = is_auto_save
            
            # メインセッションファイルに保存
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(self.session_data, f, indent=2, ensure_ascii=False)
            
            # バックアップを作成（自動保存以外の場合）
            if not is_auto_save:
                backup_file = self.backup_dir / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(self.session_data, f, indent=2, ensure_ascii=False)
                
                # 古いバックアップを削除（最新10個を保持）
                self._cleanup_old_backups()
            
            if not is_auto_save:
                logger.success("Session saved successfully")
            else:
                logger.debug("Auto-save completed")
                
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
    
    def restore_session(self) -> bool:
        """
        前回のセッションを復元
        
        Returns:
            復元に成功した場合True
        """
        if not self.session_file.exists():
            logger.info("No previous session found")
            return False
        
        try:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                self.session_data = json.load(f)
            
            last_saved = self.session_data.get('last_saved', 'Unknown')
            logger.success(f"Session restored from {last_saved}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore session: {e}")
            
            # バックアップから復元を試みる
            return self._restore_from_backup()
    
    def _restore_from_backup(self) -> bool:
        """バックアップから復元"""
        backups = sorted(self.backup_dir.glob("session_*.json"), reverse=True)
        
        for backup_file in backups[:3]:  # 最新3つのバックアップを試す
            try:
                with open(backup_file, 'r', encoding='utf-8') as f:
                    self.session_data = json.load(f)
                
                logger.warning(f"Session restored from backup: {backup_file.name}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to restore from {backup_file.name}: {e}")
        
        logger.error("Failed to restore from any backup")
        return False
    
    def _cleanup_old_backups(self, keep_count: int = 10):
        """古いバックアップを削除"""
        backups = sorted(self.backup_dir.glob("session_*.json"), reverse=True)
        
        for backup_file in backups[keep_count:]:
            try:
                backup_file.unlink()
                logger.debug(f"Deleted old backup: {backup_file.name}")
            except Exception as e:
                logger.error(f"Failed to delete {backup_file.name}: {e}")
    
    def set(self, key: str, value: Any):
        """
        セッションデータを設定
        
        Args:
            key: キー
            value: 値
        """
        self.session_data[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        セッションデータを取得
        
        Args:
            key: キー
            default: デフォルト値
            
        Returns:
            セッションデータ
        """
        return self.session_data.get(key, default)
    
    def delete(self, key: str):
        """
        セッションデータを削除
        
        Args:
            key: キー
        """
        if key in self.session_data:
            del self.session_data[key]
    
    def clear(self):
        """セッションデータをクリア"""
        self.session_data.clear()
    
    def get_all(self) -> Dict[str, Any]:
        """
        すべてのセッションデータを取得
        
        Returns:
            セッションデータ
        """
        return self.session_data.copy()
    
    def create_checkpoint(self, name: str = "checkpoint"):
        """
        チェックポイントを作成
        
        Args:
            name: チェックポイント名
        """
        checkpoint_file = self.backup_dir / f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        
        try:
            with open(checkpoint_file, 'wb') as f:
                pickle.dump(self.session_data, f)
            
            logger.success(f"Checkpoint created: {checkpoint_file.name}")
            
        except Exception as e:
            logger.error(f"Failed to create checkpoint: {e}")
    
    def restore_checkpoint(self, checkpoint_name: str) -> bool:
        """
        チェックポイントから復元
        
        Args:
            checkpoint_name: チェックポイントファイル名
            
        Returns:
            復元に成功した場合True
        """
        checkpoint_file = self.backup_dir / checkpoint_name
        
        if not checkpoint_file.exists():
            logger.error(f"Checkpoint not found: {checkpoint_name}")
            return False
        
        try:
            with open(checkpoint_file, 'rb') as f:
                self.session_data = pickle.load(f)
            
            logger.success(f"Restored from checkpoint: {checkpoint_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore checkpoint: {e}")
            return False
    
    def list_checkpoints(self) -> list:
        """
        利用可能なチェックポイントをリスト
        
        Returns:
            チェックポイントファイルのリスト
        """
        checkpoints = list(self.backup_dir.glob("*.pkl"))
        return [cp.name for cp in sorted(checkpoints, reverse=True)]
    
    def __enter__(self):
        """コンテキストマネージャーのエントリー"""
        self.start_auto_save()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャーのイグジット"""
        self.stop_auto_save_thread()
        self.save_session()
        
        if exc_type is not None:
            logger.error(f"Exception occurred: {exc_type.__name__}: {exc_val}")
            self.create_checkpoint("crash_recovery")


# グローバルセッションマネージャー
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """
    グローバルセッションマネージャーを取得
    
    Returns:
        セッションマネージャーインスタンス
    """
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager


def init_session(auto_save: bool = True):
    """
    セッションを初期化
    
    Args:
        auto_save: 自動保存を有効にするか
    """
    manager = get_session_manager()
    if auto_save:
        manager.start_auto_save()
    return manager


if __name__ == "__main__":
    # テスト実行
    with SessionManager() as session:
        session.set("test_key", "test_value")
        session.set("timestamp", datetime.now().isoformat())
        session.set("counter", 42)
        
        print("Session data:", session.get_all())
        
        # チェックポイントのテスト
        session.create_checkpoint("test")
        print("Checkpoints:", session.list_checkpoints())
        
        # 5秒待って自動保存をテスト
        time.sleep(5)