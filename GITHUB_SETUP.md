# GitHubリポジトリのセットアップ手順

このドキュメントは、スラリーくんをGitHubで管理するための手順書です。

## 前提条件

- GitHubアカウントを持っていること
- Gitがインストールされていること（ラズパイにインストールする場合は `sudo apt install git -y`）

## 手順

### 1. GitHubでリポジトリを作成

1. GitHubにログインします
2. 右上の「+」ボタンをクリック → 「New repository」を選択
3. リポジトリ名を入力（例: `slurrykun`）
4. 説明を入力（例: 「スラリー濃度自動測定システム」）
5. 公開設定を選択（Private推奨：機密情報を含む可能性があるため）
6. 「Create repository」をクリック

### 2. ローカルでGitリポジトリを初期化

プロジェクトディレクトリで以下のコマンドを実行します：

```bash
cd /Users/pirosea/Projects/SlullyKun
git init
```

### 3. ファイルをステージング

```bash
git add .
```

**注意**: `.gitignore`に含まれているファイル（`config.py`、`.venv/`、`saveimages/`など）は自動的に除外されます。

### 4. 初回コミット

```bash
git commit -m "Initial commit: スラリーくんの初期バージョン"
```

### 5. リモートリポジトリを追加

GitHubで作成したリポジトリのURLをコピーします：

```bash
git remote add origin https://github.com/hiromura16/SlullyKun.git
```

### 6. コードをプッシュ

```bash
git branch -M main
git push -u origin main
```

**注意**: 初回プッシュ時は、GitHubの認証情報を求められます。
ユーザー名とパスワード（またはPersonal Access Token）を入力してください。

### 7. 確認

GitHubのリポジトリページを開いて、ファイルが正しくアップロードされているか確認してください。

## 今後の更新手順

コードを変更した後は、以下のコマンドでGitHubに反映します：

```bash
# 変更を確認
git status

# 変更をステージング
git add .

# コミット
git commit -m "変更内容の説明"

# プッシュ
git push
```

## 注意事項

### 機密情報の管理

- `config.py` は `.gitignore` に含まれているため、GitHubにアップロードされません
- 機密情報（InfluxDBトークン、パスワードなど）は `config.py` にのみ保存してください
- `config.py.example` はテンプレートとしてGitHubにアップロードされます（機密情報は含まれていません）

### ブランチ管理

本番環境で使用するコードは、`main`ブランチで管理することを推奨します。
新機能の開発は、別ブランチを作成してから`main`にマージすることをおすすめします。

## トラブルシューティング

### 「Permission denied」エラー

SSH鍵を設定するか、Personal Access Tokenを使用してください。

**Personal Access Tokenの作成方法**:
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 「Generate new token」をクリック
3. 必要な権限を選択（`repo`権限が必要）
4. トークンをコピーして保存
5. パスワードの代わりにこのトークンを使用

### 「remote origin already exists」エラー

既にリモートリポジトリが設定されている場合：

```bash
git remote remove origin
git remote add origin https://github.com/hiromura16/SlullyKun.git
```

### ファイルが追加されない

`.gitignore`に含まれているファイルは追加されません。
これは正常な動作です（機密情報を誤ってアップロードしないため）。


