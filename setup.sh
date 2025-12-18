#!/bin/bash

# スラリーくん セットアップスクリプト
# このスクリプトは、ラズパイにスラリーくんをセットアップします

set -e  # エラーが発生したらスクリプトを停止

echo "=========================================="
echo "スラリーくん セットアップを開始します"
echo "=========================================="

# スクリプトのディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

# Python3とpip3がインストールされているか確認
if ! command -v python3 &> /dev/null; then
    echo "エラー: python3がインストールされていません"
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo "エラー: pip3がインストールされていません"
    exit 1
fi

echo "✓ Python3とpip3の確認完了"

# 仮想環境が存在しない場合は作成
if [ ! -d ".venv" ]; then
    echo "仮想環境を作成しています..."
    python3 -m venv .venv
    echo "✓ 仮想環境の作成完了"
else
    echo "✓ 仮想環境は既に存在します"
fi

# 仮想環境を有効化
echo "仮想環境を有効化しています..."
source .venv/bin/activate

# pipをアップグレード
echo "pipをアップグレードしています..."
pip install --upgrade pip

# 必要なパッケージをインストール
echo "必要なパッケージをインストールしています..."
pip install -r requirements.txt

echo "✓ パッケージのインストール完了"

# 設定ファイルが存在しない場合は、テンプレートからコピー
if [ ! -f "config.py" ]; then
    echo "設定ファイルを作成しています..."
    cp config.py.example config.py
    echo "✓ 設定ファイルを作成しました"
    echo ""
    echo "⚠️  重要: config.py を編集して、実際の設定値を入力してください"
    echo "   特に以下の項目を設定する必要があります:"
    echo "   - InfluxDB接続情報（URL、トークン、組織名、バケット名）"
    echo "   - SCP転送設定（ホスト、ユーザー名、パスワードまたは鍵）"
    echo ""
else
    echo "✓ 設定ファイルは既に存在します"
fi

# saveimagesディレクトリを作成
if [ ! -d "saveimages" ]; then
    echo "画像保存ディレクトリを作成しています..."
    mkdir -p saveimages
    echo "✓ 画像保存ディレクトリの作成完了"
else
    echo "✓ 画像保存ディレクトリは既に存在します"
fi

# 実行スクリプトに実行権限を付与
chmod +x run_slurrykun.sh

echo ""
echo "=========================================="
echo "セットアップが完了しました！"
echo "=========================================="
echo ""
echo "次のステップ:"
echo "1. config.py を編集して設定値を入力してください"
echo "2. USBカメラが接続されているか確認してください"
echo "3. カメラテストを実行: python3 test_camera.py"
echo "4. 実行テスト: ./run_slurrykun.sh"
echo ""

# 仮想環境を無効化
deactivate

