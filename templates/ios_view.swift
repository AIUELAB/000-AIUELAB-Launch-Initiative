// 📱 iOSアプリの基本的な画面テンプレート
// 用途: 新しい画面を作るときの雛形
// 使い方: このファイルをコピーして、必要な部分を変更する

import SwiftUI

// ========================================
// 📋 メイン画面の構造
// ========================================
struct BasicView: View {
    // 📌 状態を管理する変数（画面が更新される）
    @State private var userName = ""           // テキスト入力用
    @State private var counter = 0             // カウンター用
    @State private var isShowingAlert = false  // アラート表示用
    @State private var selectedOption = 0      // 選択肢用

    // 選択肢のリスト
    let options = ["オプション1", "オプション2", "オプション3"]

    // ========================================
    // 🎨 画面のレイアウト
    // ========================================
    var body: some View {
        // ナビゲーションビュー（画面遷移用）
        NavigationView {
            // 縦に並べる
            VStack(spacing: 20) {

                // ========================================
                // 📝 テキスト入力
                // ========================================
                VStack(alignment: .leading, spacing: 10) {
                    Text("👤 お名前")
                        .font(.headline)

                    TextField("名前を入力してください", text: $userName)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .padding(.horizontal)

                    if !userName.isEmpty {
                        Text("こんにちは、\(userName)さん！")
                            .foregroundColor(.blue)
                            .padding(.horizontal)
                    }
                }
                .padding()
                .background(Color.gray.opacity(0.1))
                .cornerRadius(10)
                .padding(.horizontal)

                // ========================================
                // 🔢 カウンター
                // ========================================
                VStack(spacing: 15) {
                    Text("カウンター: \(counter)")
                        .font(.largeTitle)
                        .fontWeight(.bold)

                    HStack(spacing: 20) {
                        // マイナスボタン
                        Button(action: {
                            if counter > 0 {
                                counter -= 1
                            }
                        }) {
                            Image(systemName: "minus.circle.fill")
                                .font(.system(size: 40))
                                .foregroundColor(.red)
                        }

                        // リセットボタン
                        Button(action: {
                            counter = 0
                        }) {
                            Text("リセット")
                                .padding(.horizontal, 20)
                                .padding(.vertical, 10)
                                .background(Color.gray)
                                .foregroundColor(.white)
                                .cornerRadius(8)
                        }

                        // プラスボタン
                        Button(action: {
                            counter += 1
                        }) {
                            Image(systemName: "plus.circle.fill")
                                .font(.system(size: 40))
                                .foregroundColor(.green)
                        }
                    }
                }
                .padding()
                .background(Color.blue.opacity(0.1))
                .cornerRadius(10)
                .padding(.horizontal)

                // ========================================
                // 🎯 選択肢（ピッカー）
                // ========================================
                VStack(alignment: .leading, spacing: 10) {
                    Text("🎯 オプションを選択")
                        .font(.headline)

                    Picker("オプション", selection: $selectedOption) {
                        ForEach(0..<options.count) { index in
                            Text(options[index]).tag(index)
                        }
                    }
                    .pickerStyle(SegmentedPickerStyle())
                    .padding(.horizontal)

                    Text("選択: \(options[selectedOption])")
                        .padding(.horizontal)
                        .foregroundColor(.green)
                }
                .padding()
                .background(Color.green.opacity(0.1))
                .cornerRadius(10)
                .padding(.horizontal)

                // ========================================
                // 🔘 アクションボタン
                // ========================================
                Button(action: {
                    // ボタンが押されたときの処理
                    performAction()
                }) {
                    HStack {
                        Image(systemName: "paperplane.fill")
                        Text("実行")
                    }
                    .font(.headline)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(
                        LinearGradient(
                            gradient: Gradient(colors: [Color.blue, Color.purple]),
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
                    .cornerRadius(10)
                }
                .padding(.horizontal)

                Spacer() // 余白を追加
            }
            .navigationTitle("📱 基本画面")
            .navigationBarTitleDisplayMode(.large)

            // ========================================
            // 🔔 アラート
            // ========================================
            .alert(isPresented: $isShowingAlert) {
                Alert(
                    title: Text("実行完了"),
                    message: Text(createAlertMessage()),
                    dismissButton: .default(Text("OK"))
                )
            }

            // ========================================
            // ⚙️ ナビゲーションバーのボタン
            // ========================================
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        resetAll()
                    }) {
                        Image(systemName: "arrow.clockwise")
                    }
                }
            }
        }
    }

    // ========================================
    // 🔧 機能の実装
    // ========================================

    // アクション実行
    func performAction() {
        // ここに実行したい処理を書く
        print("実行ボタンが押されました")
        print("名前: \(userName)")
        print("カウンター: \(counter)")
        print("選択: \(options[selectedOption])")

        // アラートを表示
        isShowingAlert = true
    }

    // アラートメッセージを作成
    func createAlertMessage() -> String {
        var message = "設定内容:\n"

        if !userName.isEmpty {
            message += "• 名前: \(userName)\n"
        }
        message += "• カウント: \(counter)\n"
        message += "• 選択: \(options[selectedOption])"

        return message
    }

    // 全てリセット
    func resetAll() {
        userName = ""
        counter = 0
        selectedOption = 0
    }
}

// ========================================
// 👁️ プレビュー（開発時の表示確認用）
// ========================================
struct BasicView_Previews: PreviewProvider {
    static var previews: some View {
        BasicView()
    }
}

// ========================================
// 💡 使い方のヒント
// ========================================
/*
 1. このファイルをコピーして新しい名前で保存
 2. struct名を変更（BasicView → YourViewName）
 3. 必要な部分だけ残して、不要な部分を削除
 4. 独自の機能を追加

 よく使うUI部品:
 - Text: テキスト表示
 - TextField: テキスト入力
 - Button: ボタン
 - Image: 画像表示
 - List: リスト表示
 - NavigationLink: 画面遷移
 - Toggle: ON/OFFスイッチ
 - Slider: スライダー
 - DatePicker: 日付選択
 */
