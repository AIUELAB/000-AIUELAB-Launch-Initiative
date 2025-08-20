"""
🎯 シンプルな自動化の例
このスクリプトは、日常的なタスクを自動化する例です
初心者の方でも理解しやすいように、詳しいコメントを付けています
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path

# ========================================
# 📌 1. ファイル整理の自動化
# ========================================
def organize_downloads_folder():
    """
    ダウンロードフォルダを自動で整理する
    ファイルの種類ごとにフォルダに振り分ける
    """
    print("📁 ダウンロードフォルダを整理中...")

    # ダウンロードフォルダのパス（お使いの環境に合わせて変更）
    downloads_path = Path.home() / "Downloads"

    # ファイルの種類と振り分け先フォルダ
    file_categories = {
        "画像": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
        "動画": [".mp4", ".avi", ".mov", ".wmv", ".flv"],
        "音楽": [".mp3", ".wav", ".flac", ".aac", ".m4a"],
        "文書": [".pdf", ".doc", ".docx", ".txt", ".odt"],
        "表計算": [".xls", ".xlsx", ".csv"],
        "プレゼン": [".ppt", ".pptx"],
        "圧縮ファイル": [".zip", ".rar", ".7z", ".tar", ".gz"],
        "プログラム": [".exe", ".dmg", ".pkg", ".app"],
        "コード": [".py", ".js", ".html", ".css", ".java", ".cpp"]
    }

    # 整理を実行
    moved_count = 0

    # ダウンロードフォルダ内のファイルを確認
    for file_path in downloads_path.iterdir():
        if file_path.is_file():  # ファイルの場合のみ処理
            file_extension = file_path.suffix.lower()

            # どのカテゴリに属するか確認
            for category, extensions in file_categories.items():
                if file_extension in extensions:
                    # カテゴリフォルダを作成（存在しない場合）
                    category_folder = downloads_path / category
                    category_folder.mkdir(exist_ok=True)

                    # ファイルを移動
                    new_path = category_folder / file_path.name

                    # 同名ファイルが存在する場合は番号を付ける
                    if new_path.exists():
                        counter = 1
                        while new_path.exists():
                            name_parts = file_path.stem, counter, file_extension
                            new_name = f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                            new_path = category_folder / new_name
                            counter += 1

                    try:
                        file_path.rename(new_path)
                        print(f"  ✅ {file_path.name} → {category}/")
                        moved_count += 1
                    except Exception as e:
                        print(f"  ❌ {file_path.name} の移動に失敗: {e}")

                    break

    print(f"📊 結果: {moved_count}個のファイルを整理しました！")
    return moved_count

# ========================================
# 📌 2. TODOリストの管理
# ========================================
class SimpleTodoManager:
    """シンプルなTODOリスト管理システム"""

    def __init__(self, filename="todos.json"):
        """初期化"""
        self.filename = filename
        self.todos = self.load_todos()

    def load_todos(self):
        """TODOリストを読み込む"""
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_todos(self):
        """TODOリストを保存する"""
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.todos, f, ensure_ascii=False, indent=2)

    def add_todo(self, task):
        """新しいタスクを追加"""
        todo = {
            "id": len(self.todos) + 1,
            "task": task,
            "completed": False,
            "created_at": datetime.now().isoformat(),
            "completed_at": None
        }
        self.todos.append(todo)
        self.save_todos()
        print(f"✅ タスク追加: {task}")
        return todo

    def complete_todo(self, todo_id):
        """タスクを完了にする"""
        for todo in self.todos:
            if todo["id"] == todo_id:
                todo["completed"] = True
                todo["completed_at"] = datetime.now().isoformat()
                self.save_todos()
                print(f"✅ タスク完了: {todo['task']}")
                return True
        print(f"❌ ID {todo_id} のタスクが見つかりません")
        return False

    def list_todos(self, show_completed=False):
        """TODOリストを表示"""
        print("\n📝 TODOリスト:")
        print("-" * 50)

        for todo in self.todos:
            if not show_completed and todo["completed"]:
                continue

            status = "✅" if todo["completed"] else "⏳"
            print(f"{status} [{todo['id']}] {todo['task']}")

            if todo["completed"] and todo["completed_at"]:
                completed_date = datetime.fromisoformat(todo["completed_at"])
                print(f"   完了日: {completed_date.strftime('%Y/%m/%d %H:%M')}")

        print("-" * 50)

        # 統計を表示
        total = len(self.todos)
        completed = sum(1 for t in self.todos if t["completed"])
        pending = total - completed

        print(f"📊 合計: {total} | 完了: {completed} | 未完了: {pending}")

    def get_daily_summary(self):
        """今日の進捗をまとめる"""
        today = datetime.now().date()
        completed_today = []

        for todo in self.todos:
            if todo["completed"] and todo["completed_at"]:
                completed_date = datetime.fromisoformat(todo["completed_at"]).date()
                if completed_date == today:
                    completed_today.append(todo["task"])

        print(f"\n📅 今日（{today}）の実績:")
        if completed_today:
            for task in completed_today:
                print(f"  ✅ {task}")
        else:
            print("  まだ完了したタスクはありません")

        return completed_today

# ========================================
# 📌 3. 簡単なバックアップシステム
# ========================================
def backup_important_files():
    """
    重要なファイルを自動バックアップ
    """
    print("\n💾 バックアップを開始...")

    # バックアップ元とバックアップ先の設定
    backup_config = {
        "source_dirs": [
            Path.home() / "Documents",
            # Path.home() / "Pictures",  # 必要に応じてコメントを外す
            # Path.home() / "Desktop",
        ],
        "backup_dir": Path.home() / "Backups" / datetime.now().strftime("%Y%m%d_%H%M%S"),
        "file_extensions": [".txt", ".pdf", ".docx", ".xlsx", ".py", ".js"]  # バックアップする拡張子
    }

    # バックアップフォルダを作成
    backup_dir = backup_config["backup_dir"]
    backup_dir.mkdir(parents=True, exist_ok=True)

    backed_up_files = []

    # 各ソースディレクトリからファイルをバックアップ
    for source_dir in backup_config["source_dirs"]:
        if not source_dir.exists():
            print(f"  ⚠️  {source_dir} が見つかりません")
            continue

        print(f"  📂 {source_dir.name} をスキャン中...")

        # 指定された拡張子のファイルを探す
        for ext in backup_config["file_extensions"]:
            for file_path in source_dir.glob(f"*{ext}"):
                if file_path.is_file():
                    # バックアップ先のパスを作成
                    relative_path = file_path.relative_to(source_dir.parent)
                    backup_path = backup_dir / relative_path

                    # ディレクトリ構造を維持
                    backup_path.parent.mkdir(parents=True, exist_ok=True)

                    try:
                        # ファイルをコピー
                        import shutil
                        shutil.copy2(file_path, backup_path)
                        backed_up_files.append(file_path.name)
                        print(f"    ✅ {file_path.name}")
                    except Exception as e:
                        print(f"    ❌ {file_path.name}: {e}")

    # バックアップ情報を記録
    info_file = backup_dir / "backup_info.json"
    backup_info = {
        "timestamp": datetime.now().isoformat(),
        "files_count": len(backed_up_files),
        "files": backed_up_files,
        "backup_location": str(backup_dir)
    }

    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(backup_info, f, ensure_ascii=False, indent=2)

    print(f"\n📊 バックアップ完了:")
    print(f"  • ファイル数: {len(backed_up_files)}")
    print(f"  • 保存先: {backup_dir}")

    return backup_info

# ========================================
# 📌 4. 実行例
# ========================================
def main():
    """メイン処理"""
    print("=" * 60)
    print("🤖 自動化スクリプト実行例")
    print("=" * 60)

    while True:
        print("\n何を実行しますか？")
        print("1. 📁 ダウンロードフォルダを整理")
        print("2. 📝 TODOリストを管理")
        print("3. 💾 重要ファイルをバックアップ")
        print("4. 🚪 終了")

        choice = input("\n番号を選択 (1-4): ").strip()

        if choice == "1":
            # ファイル整理
            organize_downloads_folder()

        elif choice == "2":
            # TODOリスト管理
            todo_manager = SimpleTodoManager()

            while True:
                print("\nTODOリスト操作:")
                print("a. タスク追加")
                print("b. タスク完了")
                print("c. リスト表示")
                print("d. 今日の進捗")
                print("e. 戻る")

                todo_choice = input("選択 (a-e): ").strip().lower()

                if todo_choice == "a":
                    task = input("新しいタスク: ")
                    todo_manager.add_todo(task)
                elif todo_choice == "b":
                    todo_manager.list_todos()
                    try:
                        todo_id = int(input("完了するタスクのID: "))
                        todo_manager.complete_todo(todo_id)
                    except ValueError:
                        print("❌ 数字を入力してください")
                elif todo_choice == "c":
                    show_all = input("完了済みも表示？ (y/n): ").lower() == 'y'
                    todo_manager.list_todos(show_completed=show_all)
                elif todo_choice == "d":
                    todo_manager.get_daily_summary()
                elif todo_choice == "e":
                    break

        elif choice == "3":
            # バックアップ
            backup_important_files()

        elif choice == "4":
            print("\n👋 終了します")
            break
        else:
            print("❌ 1-4の数字を入力してください")

        # 少し待機
        time.sleep(1)

# ========================================
# 🏃 スクリプト実行
# ========================================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  中断されました")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        print("Claudeに相談してください！")
