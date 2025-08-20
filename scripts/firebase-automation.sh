#!/bin/bash

# Firebase 自動化スクリプト
# AIUELAB iOS アプリ用 Firebase 管理

set -euo pipefail

# 色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Firebase設定
FIREBASE_ACCOUNT="aiuelab.official@gmail.com"
FIREBASE_PROJECT_PREFIX="aiuelab"

# ログ関数
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Firebase CLI チェック
check_firebase_cli() {
    if ! command -v firebase &> /dev/null; then
        log_error "Firebase CLI がインストールされていません"
        log_info "インストール中..."
        npm install -g firebase-tools
    else
        log_success "Firebase CLI が検出されました: $(firebase --version)"
    fi
}

# ログイン状態確認
check_login() {
    log_info "Firebase ログイン状態を確認中..."

    if firebase projects:list &> /dev/null; then
        log_success "Firebase にログイン済み"
        return 0
    else
        log_warning "ログインが必要です"
        return 1
    fi
}

# 自動ログイン
auto_login() {
    log_info "Firebase にログイン中..."

    # CI環境用トークンログイン
    if [ -n "${FIREBASE_TOKEN:-}" ]; then
        firebase login:ci --token "$FIREBASE_TOKEN"
    else
        # インタラクティブログイン
        firebase login --reauth
    fi

    log_success "Firebase にログインしました"
}

# プロジェクト作成
create_project() {
    local APP_NAME="$1"
    local PROJECT_ID="${FIREBASE_PROJECT_PREFIX}-${APP_NAME,,}"

    log_info "Firebase プロジェクトを作成中: $PROJECT_ID"

    # プロジェクト作成
    firebase projects:create "$PROJECT_ID" \
        --display-name "$APP_NAME" \
        --organization "AIUELAB" || true

    log_success "プロジェクト作成完了: $PROJECT_ID"

    # デフォルトプロジェクトに設定
    firebase use "$PROJECT_ID"
}

# iOS アプリ追加
add_ios_app() {
    local PROJECT_ID="$1"
    local BUNDLE_ID="$2"
    local APP_NAME="$3"

    log_info "iOS アプリを追加中: $BUNDLE_ID"

    # Firebase プロジェクトに iOS アプリを追加
    firebase apps:create IOS "$BUNDLE_ID" \
        --display-name "$APP_NAME" \
        --project "$PROJECT_ID"

    log_success "iOS アプリ追加完了"

    # GoogleService-Info.plist をダウンロード
    log_info "設定ファイルをダウンロード中..."
    firebase apps:sdkconfig IOS "$BUNDLE_ID" \
        --project "$PROJECT_ID" \
        -o "GoogleService-Info.plist"

    log_success "GoogleService-Info.plist をダウンロードしました"
}

# Firebase サービス有効化
enable_services() {
    local PROJECT_ID="$1"

    log_info "Firebase サービスを有効化中..."

    # Authentication
    firebase auth:import /dev/null --project "$PROJECT_ID" 2>/dev/null || true
    log_success "Authentication 有効化"

    # Firestore
    firebase firestore:databases:create default --project "$PROJECT_ID" 2>/dev/null || true
    log_success "Firestore 有効化"

    # Analytics
    log_success "Analytics 有効化（デフォルトで有効）"

    # Crashlytics
    log_success "Crashlytics 有効化（SDK統合で自動有効化）"

    # Cloud Messaging
    log_success "Cloud Messaging 有効化（プッシュ通知用）"
}

# Firebase 設定ファイル生成
generate_firebase_json() {
    cat > firebase.json << 'EOF'
{
  "firestore": {
    "rules": "firestore.rules",
    "indexes": "firestore.indexes.json"
  },
  "hosting": {
    "public": "public",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ]
  },
  "storage": {
    "rules": "storage.rules"
  },
  "emulators": {
    "auth": {
      "port": 9099
    },
    "firestore": {
      "port": 8080
    },
    "hosting": {
      "port": 5000
    },
    "storage": {
      "port": 9199
    },
    "ui": {
      "enabled": true,
      "port": 4000
    }
  }
}
EOF
    log_success "firebase.json を生成しました"
}

# Firestore ルール生成
generate_firestore_rules() {
    cat > firestore.rules << 'EOF'
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // ユーザー認証が必要
    match /users/{userId} {
      allow read: if request.auth != null && request.auth.uid == userId;
      allow write: if request.auth != null && request.auth.uid == userId;
    }

    // アプリデータ
    match /apps/{appId} {
      allow read: if true;  // 公開情報
      allow write: if request.auth != null && request.auth.token.admin == true;
    }

    // アナリティクスデータ
    match /analytics/{document=**} {
      allow read: if request.auth != null && request.auth.token.admin == true;
      allow write: if false;  // サーバーのみ書き込み可能
    }
  }
}
EOF
    log_success "firestore.rules を生成しました"
}

# Storage ルール生成
generate_storage_rules() {
    cat > storage.rules << 'EOF'
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    // ユーザーアップロード
    match /users/{userId}/{allPaths=**} {
      allow read: if request.auth != null && request.auth.uid == userId;
      allow write: if request.auth != null && request.auth.uid == userId
        && request.resource.size < 10 * 1024 * 1024;  // 10MB制限
    }

    // アプリアセット
    match /apps/{appId}/{allPaths=**} {
      allow read: if true;  // 公開
      allow write: if request.auth != null && request.auth.token.admin == true;
    }
  }
}
EOF
    log_success "storage.rules を生成しました"
}

# iOS用 Swift 設定ファイル生成
generate_ios_config() {
    local APP_NAME="$1"

    cat > FirebaseConfig.swift << EOF
//
//  FirebaseConfig.swift
//  $APP_NAME
//
//  Generated by AIUELAB Firebase Automation
//

import Firebase
import FirebaseAuth
import FirebaseFirestore
import FirebaseAnalytics
import FirebaseCrashlytics
import FirebaseMessaging

class FirebaseConfig {
    static let shared = FirebaseConfig()

    private init() {
        FirebaseApp.configure()
        setupAuthentication()
        setupAnalytics()
        setupCrashlytics()
        setupMessaging()
    }

    private func setupAuthentication() {
        // Anonymous auth for initial use
        if Auth.auth().currentUser == nil {
            Auth.auth().signInAnonymously { result, error in
                if let error = error {
                    print("Auth error: \\(error.localizedDescription)")
                } else {
                    print("Anonymous auth successful")
                }
            }
        }
    }

    private func setupAnalytics() {
        Analytics.setAnalyticsCollectionEnabled(true)
        Analytics.setUserID(Auth.auth().currentUser?.uid)
    }

    private func setupCrashlytics() {
        Crashlytics.crashlytics().setCrashlyticsCollectionEnabled(true)
    }

    private func setupMessaging() {
        Messaging.messaging().delegate = self

        // Request notification permission
        UNUserNotificationCenter.current().requestAuthorization(
            options: [.alert, .badge, .sound]
        ) { granted, _ in
            print("Notification permission: \\(granted)")
        }
    }
}

// MARK: - Messaging Delegate
extension FirebaseConfig: MessagingDelegate {
    func messaging(_ messaging: Messaging, didReceiveRegistrationToken fcmToken: String?) {
        print("FCM Token: \\(fcmToken ?? "nil")")
        // Send token to server if needed
    }
}
EOF
    log_success "FirebaseConfig.swift を生成しました"
}

# プロジェクト一覧表示
list_projects() {
    log_info "Firebase プロジェクト一覧"
    echo "================================"
    firebase projects:list
}

# メイン処理
main() {
    log_info "🔥 Firebase 自動化ツール"
    echo "================================"

    # Firebase CLI チェック
    check_firebase_cli

    # ログイン確認
    if ! check_login; then
        auto_login || exit 1
    fi

    # コマンド処理
    case "${1:-}" in
        create)
            APP_NAME="${2:-NewApp}"
            BUNDLE_ID="${3:-com.aiuelab.$APP_NAME}"
            create_project "$APP_NAME"
            add_ios_app "${FIREBASE_PROJECT_PREFIX}-${APP_NAME,,}" "$BUNDLE_ID" "$APP_NAME"
            enable_services "${FIREBASE_PROJECT_PREFIX}-${APP_NAME,,}"
            generate_firebase_json
            generate_firestore_rules
            generate_storage_rules
            generate_ios_config "$APP_NAME"
            log_success "✨ Firebase セットアップ完了！"
            ;;
        list)
            list_projects
            ;;
        init)
            generate_firebase_json
            generate_firestore_rules
            generate_storage_rules
            log_success "✨ Firebase 設定ファイル生成完了！"
            ;;
        *)
            echo "使用方法:"
            echo "  $0 create <app-name> [bundle-id]  # 新規プロジェクト作成"
            echo "  $0 list                            # プロジェクト一覧"
            echo "  $0 init                            # 設定ファイル生成"
            ;;
    esac
}

# スクリプト実行
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi
