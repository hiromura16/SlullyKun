# スラリーくん デプロイ手順書

このドキュメントは、ラズパイにスラリーくんをデプロイするための詳細な手順書です。
Gitや仮想環境の知識がない方でも、この手順に従ってデプロイできるように説明しています。

## 目次

1. [事前準備](#事前準備)
2. [GitHubからコードを取得する](#githubからコードを取得する)
3. [セットアップの実行](#セットアップの実行)
4. [設定ファイルの編集](#設定ファイルの編集)
5. [動作確認](#動作確認)
6. [自動実行の設定](#自動実行の設定)
7. [トラブルシューティング](#トラブルシューティング)

---

## 事前準備

### 1. ラズパイのセットアップ

ラズパイにRaspberry Pi OSがインストールされていることを確認してください。

#### ラズパイの初期設定

1. ラズパイを起動します
2. ターミナルを開きます（デスクトップのターミナルアイコンをクリック、または `Ctrl + Alt + T`）

#### システムの更新

以下のコマンドを実行して、システムを最新の状態にします：

```bash
sudo apt update
sudo apt upgrade -y
```

**注意**: この処理には時間がかかります（10分〜30分程度）

### 2. 必要なソフトウェアの確認

以下のコマンドで、Python3とpip3がインストールされているか確認します：

```bash
python3 --version
pip3 --version
```

両方のコマンドでバージョン番号が表示されればOKです。
表示されない場合は、以下のコマンドでインストールします：

```bash
sudo apt install python3 python3-pip python3-venv -y
```

### 3. Gitのインストール（まだインストールされていない場合）

GitHubからコードを取得するために、Gitが必要です。
以下のコマンドでインストールします：

```bash
sudo apt install git -y
```

インストールが完了したか確認します：

```bash
git --version
```

### 4. 作業ディレクトリの作成

アプリケーションを配置するディレクトリを作成します：

```bash
mkdir -p ~/app
cd ~/app
```

---

## GitHubからコードを取得する

### 方法1: Gitを使う方法（推奨）

GitHubのリポジトリURLを用意します：

```bash
cd ~/app
git clone https://github.com/hiromura16/SlullyKun.git
cd SlullyKun
```

### 方法2: ZIPファイルをダウンロードする方法（Gitが使えない場合）

1. GitHubのリポジトリページを開きます
2. 緑色の「Code」ボタンをクリックします
3. 「Download ZIP」をクリックしてZIPファイルをダウンロードします
4. ダウンロードしたZIPファイルをラズパイに転送します（USBメモリ、SCP、など）
5. ラズパイでZIPファイルを解凍します：

```bash
cd ~/app
unzip SlullyKun-main.zip  # ファイル名は実際のファイル名に合わせてください
mv SlullyKun-main SlullyKun  # ディレクトリ名を統一
cd SlullyKun
```

---

## セットアップの実行

### 1. セットアップスクリプトに実行権限を付与

```bash
chmod +x setup.sh
```

### 2. セットアップスクリプトを実行

```bash
./setup.sh
```

このスクリプトは以下を自動で実行します：
- 仮想環境（`.venv`）の作成
- 必要なPythonパッケージのインストール
- 設定ファイル（`config.py`）のテンプレート作成
- 画像保存ディレクトリ（`saveimages`）の作成

**処理時間**: 5分〜15分程度かかります（パッケージのダウンロードとインストールに時間がかかります）

**注意**: エラーが発生した場合は、エラーメッセージを確認してください。
よくあるエラーについては、[トラブルシューティング](#トラブルシューティング)を参照してください。

### 3. セットアップ完了の確認

セットアップが正常に完了すると、以下のようなメッセージが表示されます：

```
==========================================
セットアップが完了しました！
==========================================

次のステップ:
1. config.py を編集して設定値を入力してください
2. USBカメラが接続されているか確認してください
3. カメラテストを実行: python3 test_camera.py
4. 実行テスト: ./run_slurrykun.sh
```

---

## 設定ファイルの編集

### 1. 設定ファイルを開く

```bash
nano config.py
```

**nanoエディタの使い方**:
- 編集: そのまま文字を入力します
- 保存: `Ctrl + O` を押して、`Enter` を押します
- 終了: `Ctrl + X` を押します

### 2. 必須設定項目

以下の項目を実際の値に置き換えてください：

#### InfluxDB設定

```python
INFLUXDB_SETTINGS = {
    'INFLUXDB_URL': "https://your-influxdb-server.com/api/v2/write?org=your_org&bucket=your_bucket&precision=s",
    'INFLUXDB_TOKEN': "YOUR_INFLUXDB_TOKEN_HERE",  # ← ここに実際のトークンを入力
    'INFLUXDB_ORG': "your_org",  # ← ここに実際の組織名を入力
    'INFLUXDB_BUCKET': "your_bucket",  # ← ここに実際のバケット名を入力
}
```

**InfluxDBの情報をどこで確認するか**:
- URL、組織名、バケット名: InfluxDBの管理画面で確認
- トークン: InfluxDBの管理画面で生成（読み書き権限が必要）

#### SCP転送設定

画像をアップロードするサーバーの情報を設定します：

```python
SCP_SETTINGS = {
    'HOST': 'your-server.com',  # ← サーバーのホスト名またはIPアドレス
    'PORT': 22,  # 通常は22のままでOK
    'USERNAME': 'your_username',  # ← サーバーにログインするユーザー名
    'PASSWORD': 'your_password',  # ← パスワード認証を使う場合（鍵認証の場合はNone）
    'KEY_PATH': os.path.expanduser('~/.ssh/id_rsa'),  # SSH鍵を使う場合のパス
    'REMOTE_DIR': '/var/www/html/slurryimages',  # ← 画像を保存するリモートディレクトリ
}
```

**認証方法の選択**:
- **パスワード認証**: `PASSWORD` にパスワードを入力し、`KEY_PATH` はそのままにします
- **SSH鍵認証**: `PASSWORD` を `None` にし、`KEY_PATH` にSSH鍵のパスを設定します

**SSH鍵の作成方法**（まだ鍵がない場合）:

```bash
ssh-keygen -t rsa -b 4096
# ファイル名を聞かれたら Enter を押す（デフォルトのまま）
# パスフレーズを聞かれたら Enter を押す（空のままでもOK）
```

公開鍵をサーバーにコピーします：

```bash
ssh-copy-id username@your-server.com
```

### 3. その他の設定項目（必要に応じて変更）

#### GPIO設定

リレーHATの接続ピンが異なる場合は変更してください：

```python
GPIO_SETTINGS = {
    'RELAY_PIN_INJECT': 4,  # 注水ソレノイドのピン番号
    'RELAY_PIN_DRAIN': 17,  # 排水ソレノイドのピン番号
    'RELAY_PIN_PUMP': 27,   # 水中ポンプのピン番号
}
```

#### 時間設定

測定サイクルの時間を調整できます：

```python
TIME_SETTINGS = {
    'DRAIN_TIME': 20,    # 排水処理時間（秒）
    'INJECT_TIME': 15,   # 注水処理時間（秒）
    'WAITING_TIME': 600,  # 沈降を待つ時間（秒）= 10分
}
```

#### 画像解析設定

カメラの位置やメスシリンダーの配置が異なる場合は調整が必要です：

```python
CROP_SETTINGS = {
    'X1': 550,  # 左上のX座標
    'Y1': 0,    # 左上のY座標
    'X2': 720,  # 右下のX座標
    'Y2': 705,  # 右下のY座標
}

ANALYSIS_SETTINGS = {
    'BINARY_THRESHOLD': 100,  # 二値化の閾値（0-255）
    'CROP_SCALE_FACTOR': 0.3,  # クロップ領域が実際に占める面積の比率
}
```

### 4. 設定ファイルの保存

`Ctrl + O` を押して保存し、`Ctrl + X` を押してエディタを終了します。

---

## 動作確認

### 1. USBカメラの確認

USBカメラが接続されているか確認します：

```bash
lsusb
```

USBカメラが表示されればOKです。

ビデオデバイスを確認します：

```bash
ls -l /dev/video*
```

`/dev/video0` が表示されればOKです。

### 2. カメラテストの実行

カメラが正しく動作するかテストします：

```bash
source .venv/bin/activate
python3 test_camera.py
deactivate
```

**注意**: 仮想環境を有効化する必要があります（`source .venv/bin/activate`）

正常に動作すれば、`test_image.jpg` が作成されます。
画像を確認してみてください：

```bash
ls -lh test_image.jpg
```

### 3. 実行テスト

実際に測定を実行してみます：

```bash
./run_slurrykun.sh
```

**処理の流れ**:
1. 古い画像ファイルのクリーンアップ
2. 排水処理（20秒）
3. 注水処理（15秒）
4. 沈降待機（10分）
5. 画像取得
6. 画像解析
7. InfluxDBへのデータ送信
8. 画像のアップロード

**注意**: 初回実行時は、沈降待機時間（10分）があるため、完了まで時間がかかります。

### 4. ログの確認

実行中にエラーが発生した場合は、ターミナルにエラーメッセージが表示されます。
また、`slurrykun.log` ファイルにもログが記録されます（cronで実行する場合）。

---

## 自動実行の設定

定期的に測定を実行するには、**cron**または**systemd**を使用できます。
systemdの方が管理しやすく、ログの確認も簡単です。

---

### 方法1: systemdを使用する（推奨）

systemdは、cronよりも管理しやすく、ログの確認も簡単です。

#### 1. サービスファイルとタイマーファイルのコピー

```bash
sudo cp slurrykun.service /etc/systemd/system/
sudo cp slurrykun.timer /etc/systemd/system/
```

#### 2. パスの確認と修正

サービスファイルのパスを実際のインストール場所に合わせて修正します：

```bash
sudo nano /etc/systemd/system/slurrykun.service
```

以下の行を実際のパスに変更してください：
- `WorkingDirectory=/home/pi/app/SlullyKun` → 実際のインストール場所
- `ExecStart=/home/pi/app/SlullyKun/run_slurrykun.sh` → 実際のスクリプトのパス
- `StandardOutput=append:/home/pi/app/SlullyKun/slurrykun.log` → 実際のログファイルのパス
- `User=pi` → 実際のユーザー名

#### 3. systemdの再読み込み

```bash
sudo systemctl daemon-reload
```

#### 4. タイマーの有効化と開始

```bash
sudo systemctl enable slurrykun.timer
sudo systemctl start slurrykun.timer
```

#### 5. タイマーの状態確認

```bash
# タイマーの状態を確認
sudo systemctl status slurrykun.timer

# タイマーの一覧を確認
systemctl list-timers slurrykun.timer

# 次回実行時刻を確認
systemctl list-timers --all | grep slurrykun
```

#### 6. ログの確認

```bash
# サービスのログを確認
sudo journalctl -u slurrykun.service -f

# 最新のログを確認
sudo journalctl -u slurrykun.service -n 50
```

#### 7. 手動実行（テスト用）

```bash
sudo systemctl start slurrykun.service
```

#### タイマーの無効化（必要に応じて）

```bash
sudo systemctl stop slurrykun.timer
sudo systemctl disable slurrykun.timer
```

#### 実行頻度の変更

`slurrykun.timer`ファイルを編集して実行頻度を変更できます：

```bash
sudo nano /etc/systemd/system/slurrykun.timer
```

変更例：
- 30分ごと: `OnCalendar=*:0/30`（毎時0分と30分）
- 2時間ごと: `OnCalendar=0/2:00`（2時間ごと）
- 毎日午前9時: `OnCalendar=09:00`

変更後は再読み込みが必要です：

```bash
sudo systemctl daemon-reload
sudo systemctl restart slurrykun.timer
```

---

### 方法2: cronを使用する

定期的に測定を実行するには、cronを使用します。

### 1. cronの設定

```bash
crontab -e
```

初回実行時は、エディタを選択する画面が表示されます。
`nano` を選択することをおすすめします（番号を入力してEnter）。

### 2. cronジョブの追加

エディタが開いたら、ファイルの最後に以下の行を追加します：

```
0 * * * * /home/pi/app/SlullyKun/run_slurrykun.sh >> /home/pi/app/SlullyKun/slurrykun.log 2>&1
```

**この設定の意味**:
- `0 * * * *`: 毎時0分に実行（毎時1回）
- `/home/pi/app/SlullyKun/run_slurrykun.sh`: 実行するスクリプトのパス
- `>> /home/pi/app/SlullyKun/slurrykun.log`: ログをファイルに追記
- `2>&1`: エラーもログファイルに出力

**実行頻度の変更例**:
- 30分ごと: `*/30 * * * *`
- 2時間ごと: `0 */2 * * *`
- 毎日午前9時: `0 9 * * *`

**注意**: パス（`/home/pi/app/SlullyKun`）は、実際のインストール場所に合わせて変更してください。

### 3. cronの保存と終了

`Ctrl + O` を押して保存し、`Ctrl + X` を押して終了します。

### 4. cronジョブの確認

設定したcronジョブを確認します：

```bash
crontab -l
```

### 5. cronの動作確認

cronが正しく動作しているか確認するために、ログファイルを確認します：

```bash
tail -f /home/pi/app/SlullyKun/slurrykun.log
```

次の実行時刻まで待って、ログが更新されるか確認してください。

---

## トラブルシューティング

### セットアップ時のエラー

#### 「python3が見つかりません」エラー

```bash
sudo apt install python3 python3-pip python3-venv -y
```

#### 「pip3が見つかりません」エラー

```bash
sudo apt install python3-pip -y
```

#### パッケージのインストールエラー

ネットワーク接続を確認してください：

```bash
ping -c 3 8.8.8.8
```

接続できない場合は、ネットワーク設定を確認してください。

### 実行時のエラー

#### 「カメラが開けません」エラー

1. USBカメラが接続されているか確認：
   ```bash
   lsusb
   ```

2. ビデオデバイスを確認：
   ```bash
   ls -l /dev/video*
   ```

3. カメラが他のプロセスで使用されていないか確認：
   ```bash
   lsof /dev/video0
   ```

4. カメラの権限を確認：
   ```bash
   groups $USER
   ```
   `video` グループに所属していない場合は追加：
   ```bash
   sudo usermod -a -G video $USER
   ```
   変更を反映するために、一度ログアウトして再ログインしてください。

#### GPIOエラー

1. リレーHATが正しく接続されているか確認
2. GPIOピン番号が正しいか確認（`config.py`の`GPIO_SETTINGS`）
3. スーパーユーザー権限が必要な場合があります：
   ```bash
   sudo ./run_slurrykun.sh
   ```
   **注意**: スーパーユーザーで実行する場合は、仮想環境のパスが異なる場合があります

#### InfluxDB接続エラー

1. ネットワーク接続を確認：
   ```bash
   ping -c 3 your-influxdb-server.com
   ```

2. `config.py`のInfluxDB設定を確認：
   - URLが正しいか
   - トークンが有効か
   - 組織名とバケット名が正しいか

3. 手動で接続テスト：
   ```bash
   curl -X POST "https://your-influxdb-server.com/api/v2/write?org=your_org&bucket=your_bucket&precision=s" \
     --header "Authorization: Token YOUR_TOKEN" \
     --data-raw "test,location=test value=1"
   ```

#### SCP転送エラー

1. SSH接続をテスト：
   ```bash
   ssh username@your-server.com
   ```

2. パスワード認証の場合：
   - `config.py`の`PASSWORD`が正しいか確認

3. SSH鍵認証の場合：
   - SSH鍵が存在するか確認：
     ```bash
     ls -l ~/.ssh/id_rsa
     ```
   - 公開鍵がサーバーに登録されているか確認：
     ```bash
     ssh-copy-id username@your-server.com
     ```

4. リモートディレクトリの権限を確認：
   ```bash
   ssh username@your-server.com "ls -ld /var/www/html/slurryimages"
   ```

### その他の問題

#### 仮想環境が有効化されない

セットアップスクリプトを再実行してください：

```bash
./setup.sh
```

#### パスの問題

`run_slurrykun.sh`のパスが正しいか確認してください。
スクリプトのディレクトリを確認：

```bash
pwd
```

#### ログファイルが作成されない

cronで実行する場合、ログファイルのディレクトリに書き込み権限があるか確認：

```bash
ls -ld ~/app/SlullyKun
```

権限がない場合は修正：

```bash
chmod 755 ~/app/SlullyKun
```

---

## よくある質問（FAQ）

### Q: 仮想環境とは何ですか？

A: 仮想環境は、Pythonパッケージをプロジェクトごとに分離して管理する仕組みです。
これにより、異なるプロジェクトで異なるバージョンのパッケージを使用できます。

### Q: cronとは何ですか？

A: cronは、Linux/Unixシステムで定期的にコマンドを実行するための仕組みです。
設定した時刻に自動的にスクリプトを実行できます。

### Q: 設定を変更したら、どうすれば反映されますか？

A: `config.py`を編集して保存すれば、次回実行時から新しい設定が反映されます。
cronで実行している場合は、次回の実行時刻まで待つか、手動で実行して確認してください。

### Q: 画像はどこに保存されますか？

A: ローカルには `saveimages/` ディレクトリに保存されます。
また、SCP設定で指定したリモートサーバーにもアップロードされます。

### Q: 古い画像は自動的に削除されますか？

A: はい、`IMAGE_RETENTION_DAYS`で設定した日数（デフォルト90日）を超えた画像は自動的に削除されます。

---

## サポート

問題が解決しない場合は、以下の情報を含めてGitHubのIssuesで報告してください：

- エラーメッセージの全文
- 実行したコマンド
- ラズパイのOSバージョン（`cat /etc/os-release`）
- Pythonのバージョン（`python3 --version`）

