# スラリーくん (SlullyKun)

スラリーの濃度を自動測定し、Grafanaで可視化・管理するためのラズパイアプリケーションです。

## 概要

スラリーくんは、ラズパイとUSBカメラを使用してスラリー（泥水）の濃度を自動測定するシステムです。測定したデータはInfluxDBに送信され、Grafanaで可視化できます。

### 主な機能

- **自動測定**: リレー制御による自動的な注水・排水・測定サイクル
- **画像解析**: OpenCVを使用した沈降した泥の面積比の自動計算
- **データ送信**: InfluxDBへの自動データ送信
- **画像管理**: 測定画像の自動保存とリモートサーバーへのアップロード
- **自動クリーンアップ**: 古い画像ファイルの自動削除

## 必要なハードウェア

- Raspberry Pi（GPIO対応）
- USBカメラ
- リレーHAT（注水ソレノイド、排水ソレノイド、水中ポンプ用）
- メスシリンダー（測定容器）

## 必要なソフトウェア

- Raspberry Pi OS（最新版推奨）
- Python 3.7以上
- pip3

## クイックスタート

### 1. リポジトリのクローン

```bash
cd ~/app
git clone https://github.com/your-org/slurrykun.git
cd slurrykun
```

### 2. 自動セットアップの実行

```bash
chmod +x setup.sh
./setup.sh
```

このスクリプトは以下を自動で実行します：
- 仮想環境の作成
- 必要なパッケージのインストール
- 設定ファイルのテンプレート作成
- 必要なディレクトリの作成

### 3. 設定ファイルの編集

`config.py` を編集して、実際の設定値を入力してください：

```bash
nano config.py
```

特に以下の項目を設定する必要があります：
- **InfluxDB接続情報**: URL、トークン、組織名、バケット名
- **SCP転送設定**: ホスト、ユーザー名、パスワードまたはSSH鍵

### 4. カメラのテスト

USBカメラが正しく動作するか確認します：

```bash
source .venv/bin/activate
python3 test_camera.py
```

`test_image.jpg` が作成されていれば、カメラは正常に動作しています。

### 5. ヘルスチェック

システムが正常に動作する準備ができているか確認します：

```bash
chmod +x check_health.py
python3 check_health.py
```

### 6. 実行テスト

実際に測定を実行してみます：

```bash
./run_slurrykun.sh
```

## 使用方法

### 手動実行

```bash
./run_slurrykun.sh
```

### 自動実行の設定

定期的に測定を実行する場合は、**systemd**（推奨）または**cron**を使用します。

詳細な設定方法については、[DEPLOYMENT.md](DEPLOYMENT.md)の「自動実行の設定」セクションを参照してください。

## 設定項目の説明

詳細な設定項目については、`config.py.example` を参照してください。

### GPIO設定

リレーHATの接続ピンを設定します。

### 時間設定

- `DRAIN_TIME`: 排水処理時間（秒）
- `INJECT_TIME`: 注水処理時間（秒）
- `WAITING_TIME`: 沈降を待つ時間（秒）

### 画像解析設定

- `CROP_SETTINGS`: 画像の切り抜き領域（座標）
- `BINARY_THRESHOLD`: 二値化の閾値（0-255）
- `CROP_SCALE_FACTOR`: クロップ領域が実際に占める面積の比率

## トラブルシューティング

### カメラが認識されない

```bash
# USBデバイスを確認
lsusb

# ビデオデバイスを確認
ls -l /dev/video*
```

### GPIOエラーが発生する

- リレーHATが正しく接続されているか確認
- GPIOピン番号が正しいか確認（`config.py`の`GPIO_SETTINGS`）

### InfluxDBへの接続エラー

- ネットワーク接続を確認
- `config.py`のInfluxDB設定を確認
- トークンが有効か確認

### SCP転送エラー

- SSH接続をテスト: `ssh username@host`
- パスワードまたはSSH鍵が正しいか確認
- リモートディレクトリの権限を確認

## ファイル構成

```
slurrykun/
├── main.py              # メインプログラム
├── config.py            # 設定ファイル（git管理外）
├── config.py.example    # 設定ファイルのテンプレート
├── requirements.txt     # Pythonパッケージ一覧
├── setup.sh            # セットアップスクリプト
├── run_slurrykun.sh    # 実行スクリプト
├── test_camera.py      # カメラテスト用スクリプト
├── check_health.py     # ヘルスチェックスクリプト
├── slurrykun.service   # systemdサービスファイル
├── slurrykun.timer     # systemdタイマーファイル
├── README.md           # このファイル
├── DEPLOYMENT.md       # 詳細なデプロイ手順書
├── HARDWARE_SETUP.md   # ハードウェアセットアップガイド
├── WIRING_DIAGRAM.md   # 配線図と回路図の説明
├── GITHUB_SETUP.md     # GitHubリポジトリセットアップ手順
├── LICENSE             # ライセンスファイル
├── .gitignore          # Git除外設定
└── saveimages/         # 画像保存ディレクトリ（git管理外）
```

## 詳細なドキュメント

- **デプロイ手順**: [DEPLOYMENT.md](DEPLOYMENT.md) - 詳細なデプロイ手順書
- **ハードウェアセットアップ**: [HARDWARE_SETUP.md](HARDWARE_SETUP.md) - ハードウェア接続ガイド
- **配線図と回路図**: [WIRING_DIAGRAM.md](WIRING_DIAGRAM.md) - 回路図と配線図の説明

## ライセンス

MIT License

Copyright (c) 2024 Hiroshi Murakami

詳細は [LICENSE](LICENSE) ファイルを参照してください。

## サポート

問題が発生した場合は、GitHubのIssuesで報告してください。

