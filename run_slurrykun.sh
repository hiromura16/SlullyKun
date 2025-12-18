#!/bin/bash

# スラリーくん実行スクリプト
# このスクリプトは、仮想環境を有効化してPythonスクリプトを実行します

# スクリプトのディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 仮想環境を有効化
source "${SCRIPT_DIR}/.venv/bin/activate"

# スクリプトのディレクトリに移動
cd "${SCRIPT_DIR}"

# Pythonスクリプトを実行
python3 main.py

# 仮想環境を無効化
deactivate