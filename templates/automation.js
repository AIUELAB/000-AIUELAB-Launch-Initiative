/**
 * 🤖 自動化スクリプトのテンプレート
 * 用途: ブラウザ操作やWeb自動化の雛形
 * 使い方: このファイルをコピーして、必要な部分を変更する
 */

// 必要なパッケージをインポート
const puppeteer = require('puppeteer'); // ブラウザ自動化
const fs = require('fs').promises;       // ファイル操作
const path = require('path');            // パスの操作

// ========================================
// ⚙️ 設定
// ========================================
const CONFIG = {
    // ブラウザの設定
    browser: {
        headless: false,        // false: ブラウザを表示, true: 非表示
        slowMo: 50,            // 操作を遅くする（デバッグ用）
        defaultViewport: {
            width: 1280,
            height: 800
        }
    },

    // タイムアウト設定（ミリ秒）
    timeout: {
        navigation: 30000,      // ページ読み込み
        element: 10000         // 要素の待機
    },

    // 保存先
    output: {
        screenshots: './screenshots',
        data: './data'
    }
};

// ========================================
// 🔧 ユーティリティ関数
// ========================================

/**
 * 指定時間待機する
 * @param {number} ms - ミリ秒
 */
async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * ディレクトリを作成（存在しない場合）
 * @param {string} dirPath - ディレクトリパス
 */
async function ensureDir(dirPath) {
    try {
        await fs.mkdir(dirPath, { recursive: true });
    } catch (error) {
        console.error(`ディレクトリ作成エラー: ${error.message}`);
    }
}

/**
 * スクリーンショットを保存
 * @param {Page} page - Puppeteerのページオブジェクト
 * @param {string} name - ファイル名
 */
async function takeScreenshot(page, name) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `${name}_${timestamp}.png`;
    const filepath = path.join(CONFIG.output.screenshots, filename);

    await ensureDir(CONFIG.output.screenshots);
    await page.screenshot({ path: filepath, fullPage: true });
    console.log(`📸 スクリーンショット保存: ${filepath}`);
}

/**
 * データをJSONファイルに保存
 * @param {object} data - 保存するデータ
 * @param {string} filename - ファイル名
 */
async function saveData(data, filename) {
    const filepath = path.join(CONFIG.output.data, `${filename}.json`);

    await ensureDir(CONFIG.output.data);
    await fs.writeFile(filepath, JSON.stringify(data, null, 2));
    console.log(`💾 データ保存: ${filepath}`);
}

// ========================================
// 🎯 メインの自動化処理
// ========================================
async function runAutomation() {
    // ブラウザを起動
    console.log('🚀 ブラウザを起動中...');
    const browser = await puppeteer.launch(CONFIG.browser);

    try {
        // 新しいページを開く
        const page = await browser.newPage();

        // ========================================
        // 📝 例1: Googleで検索
        // ========================================
        console.log('\n📝 例1: Google検索');

        // Googleにアクセス
        await page.goto('https://www.google.com', {
            waitUntil: 'networkidle2',
            timeout: CONFIG.timeout.navigation
        });
        console.log('✅ Googleにアクセスしました');

        // 検索ボックスに入力
        const searchBox = 'input[name="q"]';
        await page.waitForSelector(searchBox, { timeout: CONFIG.timeout.element });
        await page.type(searchBox, 'Claude AI');
        console.log('✅ 検索キーワードを入力しました');

        // Enterキーを押して検索
        await page.keyboard.press('Enter');
        await page.waitForNavigation();
        console.log('✅ 検索を実行しました');

        // スクリーンショットを撮る
        await takeScreenshot(page, 'google_search_result');

        // 検索結果を取得
        const searchResults = await page.evaluate(() => {
            const results = [];
            const items = document.querySelectorAll('h3');

            items.forEach((item, index) => {
                if (index < 5) { // 上位5件のみ
                    results.push({
                        rank: index + 1,
                        title: item.textContent
                    });
                }
            });

            return results;
        });

        console.log('📊 検索結果:');
        searchResults.forEach(result => {
            console.log(`  ${result.rank}. ${result.title}`);
        });

        // 結果を保存
        await saveData(searchResults, 'search_results');

        // ========================================
        // 📝 例2: フォームの自動入力
        // ========================================
        console.log('\n📝 例2: フォーム自動入力のデモ');

        // デモページに移動（実際のURLに変更してください）
        // await page.goto('https://example.com/form');

        // フォーム入力の例（コメントアウト）
        /*
        // テキスト入力
        await page.type('#name', '山田太郎');
        await page.type('#email', 'taro@example.com');

        // ドロップダウン選択
        await page.select('#country', 'JP');

        // チェックボックス
        await page.click('#agree');

        // ラジオボタン
        await page.click('input[name="plan"][value="premium"]');

        // ボタンクリック
        await page.click('#submit');
        */

        // ========================================
        // 📝 例3: ページの情報を取得
        // ========================================
        console.log('\n📝 例3: ページ情報の取得');

        await page.goto('https://example.com');

        // ページタイトルを取得
        const title = await page.title();
        console.log(`📄 ページタイトル: ${title}`);

        // ページのURLを取得
        const url = page.url();
        console.log(`🔗 現在のURL: ${url}`);

        // ページの内容を取得
        const pageContent = await page.evaluate(() => {
            return {
                title: document.title,
                headings: Array.from(document.querySelectorAll('h1')).map(h => h.textContent),
                paragraphs: Array.from(document.querySelectorAll('p')).slice(0, 3).map(p => p.textContent)
            };
        });

        await saveData(pageContent, 'page_content');

        // ========================================
        // 🎬 終了処理
        // ========================================
        console.log('\n✨ 自動化処理が完了しました！');

    } catch (error) {
        console.error('❌ エラーが発生しました:', error.message);

        // エラー時のスクリーンショット
        const page = (await browser.pages())[0];
        if (page) {
            await takeScreenshot(page, 'error');
        }

    } finally {
        // ブラウザを閉じる
        await browser.close();
        console.log('👋 ブラウザを終了しました');
    }
}

// ========================================
// 🏃 実行
// ========================================
if (require.main === module) {
    // このスクリプトが直接実行された場合
    console.log('================================');
    console.log('🤖 自動化スクリプト開始');
    console.log('================================\n');

    runAutomation()
        .then(() => {
            console.log('\n✅ 正常終了');
            process.exit(0);
        })
        .catch(error => {
            console.error('\n❌ 異常終了:', error);
            process.exit(1);
        });
}

// エクスポート（他のファイルから使用する場合）
module.exports = {
    runAutomation,
    takeScreenshot,
    saveData,
    sleep
};

/**
 * 💡 カスタマイズのヒント:
 *
 * 1. 別のサイトを自動化:
 *    - URLを変更
 *    - セレクタを調整（DevToolsで確認）
 *
 * 2. 認証が必要な場合:
 *    - ログイン処理を追加
 *    - Cookieを保存/読み込み
 *
 * 3. 複雑な操作:
 *    - マウスホバー: page.hover(selector)
 *    - ドラッグ&ドロップ: page.drag(source, target)
 *    - ファイルアップロード: input.uploadFile(filePath)
 *
 * 4. エラー処理:
 *    - try-catchを追加
 *    - リトライ処理
 *    - タイムアウト調整
 */
