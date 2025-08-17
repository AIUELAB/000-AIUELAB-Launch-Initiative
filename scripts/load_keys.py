#!/usr/bin/env python3
"""
APIキーをキーフォルダから読み込んで.env.mcpファイルを生成するスクリプト
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

def load_config():
    """設定ファイルを読み込む"""
    config_path = Path(__file__).parent.parent / "config" / "keys.json"
    
    if not config_path.exists():
        print(f"❌ 設定ファイルが見つかりません: {config_path}")
        return None
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def read_key_file(file_path):
    """キーファイルから最初の行を読み込む"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # 最初の非空白行を返す
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    return line
        return None
    except Exception as e:
        print(f"⚠️  ファイル読み込みエラー: {file_path}")
        print(f"   {str(e)}")
        return None

def generate_env_file(config, output_path, overwrite=False):
    """環境変数ファイルを生成"""
    keys_dir = Path(config['keys_directory'])
    
    if not keys_dir.exists():
        print(f"❌ キーディレクトリが見つかりません: {keys_dir}")
        return False
    
    output_file = Path(output_path)
    
    # 既存ファイルのチェック
    if output_file.exists() and not overwrite:
        response = input(f"⚠️  {output_file} は既に存在します。上書きしますか？ (y/n): ")
        if response.lower() != 'y':
            print("❌ 操作をキャンセルしました")
            return False
    
    env_content = []
    env_content.append("# MCP Server Environment Variables")
    env_content.append(f"# Auto-generated from {keys_dir}")
    env_content.append(f"# Generated at: {datetime.now().isoformat()}")
    env_content.append("")
    
    success_count = 0
    failed_count = 0
    
    # キーマッピングに基づいて環境変数を生成
    for env_var, key_file in config['key_mappings'].items():
        key_path = keys_dir / key_file
        
        if key_path.exists():
            key_value = read_key_file(key_path)
            if key_value:
                env_content.append(f"{env_var}={key_value}")
                print(f"✅ {env_var}: {key_file} から読み込み成功")
                success_count += 1
            else:
                env_content.append(f"# {env_var}= # {key_file} から読み込み失敗")
                print(f"⚠️  {env_var}: {key_file} が空です")
                failed_count += 1
        else:
            env_content.append(f"# {env_var}= # {key_file} が見つかりません")
            print(f"⚠️  {env_var}: {key_file} が見つかりません")
            failed_count += 1
    
    # その他の環境変数（デフォルト値）
    env_content.append("")
    env_content.append("# Application Settings")
    env_content.append("APP_NAME=Claude Code MCP Template")
    env_content.append("APP_VERSION=1.0.0")
    env_content.append("ENVIRONMENT=development")
    env_content.append("DEBUG=False")
    env_content.append("LOG_LEVEL=INFO")
    
    # ファイルに書き込み
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(env_content))
    
    # ファイル権限の設定（読み書き権限を所有者のみに）
    os.chmod(output_file, 0o600)
    
    print("")
    print(f"✅ 環境変数ファイルを生成しました: {output_file}")
    print(f"   成功: {success_count} 個のキー")
    print(f"   失敗: {failed_count} 個のキー")
    
    return True

def main():
    """メイン処理"""
    print("🔐 APIキー読み込みスクリプト")
    print("=" * 50)
    
    # 設定ファイルの読み込み
    config = load_config()
    if not config:
        sys.exit(1)
    
    print(f"📁 キーディレクトリ: {config['keys_directory']}")
    print(f"🔑 マッピング数: {len(config['key_mappings'])} 個")
    print("")
    
    # 出力先の決定
    project_root = Path(__file__).parent.parent
    output_options = [
        project_root / ".env.mcp",
        project_root / "mcp-config" / ".env.mcp"
    ]
    
    print("📝 出力先を選択してください:")
    for i, path in enumerate(output_options, 1):
        print(f"   {i}. {path}")
    print(f"   3. カスタムパス")
    
    choice = input("\n選択 (1-3): ").strip()
    
    if choice == '1':
        output_path = output_options[0]
    elif choice == '2':
        output_path = output_options[1]
    elif choice == '3':
        custom_path = input("出力パスを入力: ").strip()
        output_path = Path(custom_path)
    else:
        print("❌ 無効な選択です")
        sys.exit(1)
    
    print("")
    
    # 環境変数ファイルの生成
    if generate_env_file(config, output_path):
        print("")
        print("✨ 完了しました！")
        print(f"   次のコマンドで環境変数を読み込めます:")
        print(f"   source {output_path}")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()