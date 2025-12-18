# 変更履歴

このプロジェクトのすべての重要な変更は、このファイルに記録されます。

形式は [Keep a Changelog](https://keepachangelog.com/ja/1.0.0/) に基づいており、
このプロジェクトは [Semantic Versioning](https://semver.org/lang/ja/) に準拠しています。

## [0.9.0-beta] - 2024-12-19

### 追加
- スラリー濃度の自動測定機能
- OpenCVを使用した画像解析機能
- InfluxDBへの自動データ送信機能
- Grafanaでの可視化対応
- 画像の自動保存とリモートサーバーへのアップロード機能
- 古い画像ファイルの自動クリーンアップ機能
- リレー制御による自動的な注水・排水・測定サイクル
- ヘルスチェックスクリプト（`check_health.py`）
- systemdサービスファイルとタイマーファイル
- 詳細なデプロイ手順書（`DEPLOYMENT.md`）
- ハードウェアセットアップガイド（`HARDWARE_SETUP.md`）
- 配線図と回路図の説明（`WIRING_DIAGRAM.md`）
- 自動セットアップスクリプト（`setup.sh`）

### 変更
- 初期リリース

### セキュリティ
- 機密情報（`config.py`）を`.gitignore`に追加
- 設定ファイルのテンプレート（`config.py.example`）を提供

[0.9.0-beta]: https://github.com/hiromura16/SlullyKun/releases/tag/v0.9.0-beta

