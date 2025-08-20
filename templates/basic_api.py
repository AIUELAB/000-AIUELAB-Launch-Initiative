"""
📌 基本的なAPIのテンプレート
用途: Web APIを作るときの雛形
使い方: このファイルをコピーして、必要な部分を変更する
"""

from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv

# 環境変数を読み込む（APIキーなどの秘密情報用）
load_dotenv()

# Flaskアプリを作成
app = Flask(__name__)

# ========================================
# 🏠 ホームページ（ルート）
# ========================================
@app.route('/')
def home():
    """
    APIのトップページ
    ブラウザで http://localhost:5000 を開くと表示される
    """
    return jsonify({
        "message": "🎉 APIが動いています！",
        "endpoints": {
            "/": "このページ",
            "/hello": "挨拶を返す",
            "/calculate": "計算する",
            "/data": "データを保存・取得"
        }
    })

# ========================================
# 👋 シンプルな例：挨拶
# ========================================
@app.route('/hello')
def hello():
    """
    例: http://localhost:5000/hello?name=太郎
    結果: {"message": "こんにちは、太郎さん！"}
    """
    # URLパラメータから名前を取得
    name = request.args.get('name', 'ゲスト')

    return jsonify({
        "message": f"こんにちは、{name}さん！"
    })

# ========================================
# 🔢 計算の例
# ========================================
@app.route('/calculate', methods=['POST'])
def calculate():
    """
    POSTリクエストで計算を実行

    使い方:
    curl -X POST http://localhost:5000/calculate \
         -H "Content-Type: application/json" \
         -d '{"a": 10, "b": 20, "operation": "add"}'
    """
    try:
        # リクエストからデータを取得
        data = request.get_json()
        a = data.get('a', 0)
        b = data.get('b', 0)
        operation = data.get('operation', 'add')

        # 計算を実行
        if operation == 'add':
            result = a + b
        elif operation == 'subtract':
            result = a - b
        elif operation == 'multiply':
            result = a * b
        elif operation == 'divide':
            if b != 0:
                result = a / b
            else:
                return jsonify({"error": "0で割ることはできません"}), 400
        else:
            return jsonify({"error": "不明な操作です"}), 400

        return jsonify({
            "result": result,
            "operation": operation,
            "a": a,
            "b": b
        })

    except Exception as e:
        # エラーが発生した場合
        return jsonify({"error": str(e)}), 500

# ========================================
# 💾 データの保存と取得
# ========================================
# 簡単なメモリ内データベース（実際のアプリではDBを使う）
stored_data = {}

@app.route('/data', methods=['GET', 'POST'])
def handle_data():
    """
    GET: データを取得
    POST: データを保存
    """
    if request.method == 'POST':
        # データを保存
        data = request.get_json()
        key = data.get('key')
        value = data.get('value')

        if not key:
            return jsonify({"error": "キーが必要です"}), 400

        stored_data[key] = value

        return jsonify({
            "message": "保存しました",
            "key": key,
            "value": value
        })

    else:
        # データを取得
        key = request.args.get('key')

        if key:
            # 特定のキーのデータを返す
            value = stored_data.get(key, None)
            if value is not None:
                return jsonify({"key": key, "value": value})
            else:
                return jsonify({"error": "データが見つかりません"}), 404
        else:
            # 全てのデータを返す
            return jsonify(stored_data)

# ========================================
# 🔐 APIキーを使った認証の例
# ========================================
@app.route('/protected')
def protected_route():
    """
    APIキーが必要なエンドポイントの例
    ヘッダーに X-API-Key を含める必要がある
    """
    # ヘッダーからAPIキーを取得
    api_key = request.headers.get('X-API-Key')

    # 環境変数から正しいAPIキーを取得
    correct_api_key = os.getenv('API_KEY', 'secret-key-123')

    # APIキーをチェック
    if api_key != correct_api_key:
        return jsonify({"error": "認証エラー：APIキーが無効です"}), 401

    return jsonify({
        "message": "🔓 認証成功！秘密のデータにアクセスできます",
        "secret_data": "これは保護されたデータです"
    })

# ========================================
# 🚨 エラーハンドリング
# ========================================
@app.errorhandler(404)
def not_found(error):
    """404エラー（ページが見つからない）の処理"""
    return jsonify({"error": "ページが見つかりません"}), 404

@app.errorhandler(500)
def internal_error(error):
    """500エラー（サーバーエラー）の処理"""
    return jsonify({"error": "サーバーエラーが発生しました"}), 500

# ========================================
# 🏃 アプリを起動
# ========================================
if __name__ == '__main__':
    # デバッグモードで起動（開発時のみ）
    # 本番環境では debug=False にする
    port = int(os.getenv('PORT', 5000))

    print("=" * 50)
    print("🚀 APIサーバーが起動しました！")
    print(f"📍 URL: http://localhost:{port}")
    print("🛑 終了するには Ctrl+C を押してください")
    print("=" * 50)

    app.run(debug=True, port=port)
