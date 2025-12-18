#!/usr/bin/env python3
"""
スラリーくん ヘルスチェックスクリプト
システムが正常に動作しているか確認します
"""

import sys
import os
import subprocess
from pathlib import Path


# 色付き出力用
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    END = "\033[0m"


def print_success(message):
    print(f"{Colors.GREEN}✓{Colors.END} {message}")


def print_error(message):
    print(f"{Colors.RED}✗{Colors.END} {message}")


def print_warning(message):
    print(f"{Colors.YELLOW}⚠{Colors.END} {message}")


def print_info(message):
    print(f"{Colors.BLUE}ℹ{Colors.END} {message}")


def check_python():
    """Pythonのバージョンを確認"""
    print_info("Pythonのバージョンを確認中...")
    try:
        result = subprocess.run(
            ["python3", "--version"], capture_output=True, text=True
        )
        version = result.stdout.strip()
        print_success(f"Python: {version}")
        return True
    except Exception as e:
        print_error(f"Pythonが見つかりません: {e}")
        return False


def check_virtual_env():
    """仮想環境の存在を確認"""
    print_info("仮想環境を確認中...")
    venv_path = Path(".venv")
    if venv_path.exists():
        print_success("仮想環境が存在します")
        return True
    else:
        print_error("仮想環境が見つかりません（.venv/ ディレクトリが存在しません）")
        print_info("セットアップを実行してください: ./setup.sh")
        return False


def check_packages():
    """必要なパッケージがインストールされているか確認"""
    print_info("必要なパッケージを確認中...")
    try:
        # 仮想環境のPythonを使用
        venv_python = Path(".venv/bin/python3")
        if not venv_python.exists():
            print_error("仮想環境のPythonが見つかりません")
            return False

        required_packages = [
            "cv2",  # opencv-python-headless
            "numpy",
            "RPi.GPIO",
            "requests",
            "paramiko",
        ]

        missing_packages = []
        for package in required_packages:
            try:
                if package == "cv2":
                    result = subprocess.run(
                        [str(venv_python), "-c", f"import {package}"],
                        capture_output=True,
                        timeout=5,
                    )
                else:
                    result = subprocess.run(
                        [str(venv_python), "-c", f"import {package}"],
                        capture_output=True,
                        timeout=5,
                    )

                if result.returncode == 0:
                    print_success(f"パッケージ '{package}' がインストールされています")
                else:
                    missing_packages.append(package)
                    print_error(f"パッケージ '{package}' が見つかりません")
            except Exception as e:
                missing_packages.append(package)
                print_error(f"パッケージ '{package}' の確認中にエラー: {e}")

        if missing_packages:
            print_warning(f"不足しているパッケージ: {', '.join(missing_packages)}")
            print_info(
                "パッケージをインストールしてください: pip install -r requirements.txt"
            )
            return False

        return True
    except Exception as e:
        print_error(f"パッケージの確認中にエラー: {e}")
        return False


def check_config():
    """設定ファイルの存在を確認"""
    print_info("設定ファイルを確認中...")
    config_path = Path("config.py")
    if config_path.exists():
        print_success("設定ファイル（config.py）が存在します")

        # 設定ファイルの内容を簡単に確認
        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location("config", "config.py")
            config = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config)

            # 必須設定の確認
            checks = [
                ("INFLUXDB_SETTINGS", "INFLUXDB_URL"),
                ("INFLUXDB_SETTINGS", "INFLUXDB_TOKEN"),
                ("SCP_SETTINGS", "HOST"),
            ]

            for section, key in checks:
                if hasattr(config, section):
                    section_obj = getattr(config, section)
                    if key in section_obj:
                        value = section_obj[key]
                        if value and not value.startswith("YOUR_") and value != "None":
                            print_success(
                                f"設定値 '{section}.{key}' が設定されています"
                            )
                        else:
                            print_warning(
                                f"設定値 '{section}.{key}' が未設定またはデフォルト値です"
                            )
                    else:
                        print_error(f"設定値 '{section}.{key}' が見つかりません")
                else:
                    print_error(f"設定セクション '{section}' が見つかりません")
        except Exception as e:
            print_warning(f"設定ファイルの内容確認中にエラー: {e}")

        return True
    else:
        print_error("設定ファイル（config.py）が見つかりません")
        print_info("テンプレートからコピーしてください: cp config.py.example config.py")
        return False


def check_camera():
    """USBカメラの接続を確認"""
    print_info("USBカメラを確認中...")
    try:
        # USBデバイスを確認
        result = subprocess.run(["lsusb"], capture_output=True, text=True)
        if (
            "Camera" in result.stdout
            or "Webcam" in result.stdout
            or "Video" in result.stdout
        ):
            print_success("USBカメラが検出されました")
        else:
            print_warning(
                "USBカメラが検出されませんでした（lsusbの結果に含まれていません）"
            )

        # ビデオデバイスを確認
        video_devices = list(Path("/dev").glob("video*"))
        if video_devices:
            print_success(
                f"ビデオデバイスが見つかりました: {', '.join(str(d) for d in video_devices)}"
            )
            return True
        else:
            print_error("ビデオデバイス（/dev/video*）が見つかりません")
            return False
    except Exception as e:
        print_error(f"カメラの確認中にエラー: {e}")
        return False


def check_gpio():
    """GPIOのアクセス権限を確認"""
    print_info("GPIOアクセス権限を確認中...")
    gpio_path = Path("/sys/class/gpio")
    if gpio_path.exists():
        print_success("GPIOインターフェースが利用可能です")
        return True
    else:
        print_warning(
            "GPIOインターフェースが見つかりません（Raspberry Pi以外で実行している可能性があります）"
        )
        return False


def check_directories():
    """必要なディレクトリの存在を確認"""
    print_info("必要なディレクトリを確認中...")
    directories = ["saveimages"]
    all_exist = True

    for dir_name in directories:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print_success(f"ディレクトリ '{dir_name}' が存在します")
        else:
            print_warning(
                f"ディレクトリ '{dir_name}' が存在しません（自動的に作成されます）"
            )
            all_exist = False

    return all_exist


def check_log_file():
    """ログファイルの存在とサイズを確認"""
    print_info("ログファイルを確認中...")
    log_path = Path("slurrykun.log")
    if log_path.exists():
        size = log_path.stat().st_size
        size_mb = size / (1024 * 1024)
        print_success(f"ログファイルが存在します（サイズ: {size_mb:.2f} MB）")

        if size_mb > 100:
            print_warning(
                "ログファイルが大きくなっています（100MB超）。ローテーションを検討してください"
            )

        return True
    else:
        print_info("ログファイルはまだ作成されていません（初回実行時は正常です）")
        return True


def main():
    """メイン関数"""
    print("=" * 50)
    print("スラリーくん ヘルスチェック")
    print("=" * 50)
    print()

    checks = [
        ("Python環境", check_python),
        ("仮想環境", check_virtual_env),
        ("パッケージ", check_packages),
        ("設定ファイル", check_config),
        ("USBカメラ", check_camera),
        ("GPIO", check_gpio),
        ("ディレクトリ", check_directories),
        ("ログファイル", check_log_file),
    ]

    results = []
    for name, check_func in checks:
        print(f"\n[{name}]")
        result = check_func()
        results.append((name, result))

    print("\n" + "=" * 50)
    print("チェック結果のサマリー")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓" if result else "✗"
        color = Colors.GREEN if result else Colors.RED
        print(f"{color}{status}{Colors.END} {name}")

    print(f"\n合計: {passed}/{total} のチェックが成功しました")

    if passed == total:
        print_success(
            "すべてのチェックが成功しました！システムは正常に動作する準備ができています。"
        )
        return 0
    else:
        print_warning(
            "一部のチェックが失敗しました。上記のメッセージを確認して問題を解決してください。"
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
