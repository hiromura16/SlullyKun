import time
import cv2
import numpy as np
import RPi.GPIO as GPIO
import os
import datetime
import re
import requests
import paramiko
import shutil
import stat
from scp import SCPClient

# 設定ファイルのインポート
from config import (
    GPIO_SETTINGS, 
    TIME_SETTINGS, 
    IMAGE_SAVE_SETTINGS, 
    CROP_SETTINGS, 
    ANALYSIS_SETTINGS,
    INFLUXDB_SETTINGS,
    SCP_SETTINGS
)

# 設定値の展開
RELAY_PIN_INJECT = GPIO_SETTINGS['RELAY_PIN_INJECT']
RELAY_PIN_DRAIN = GPIO_SETTINGS['RELAY_PIN_DRAIN']
RELAY_PIN_PUMP = GPIO_SETTINGS['RELAY_PIN_PUMP']

DRAIN_TIME = TIME_SETTINGS['DRAIN_TIME']
INJECT_TIME = TIME_SETTINGS['INJECT_TIME']
WAITING_TIME = TIME_SETTINGS['WAITING_TIME']

SAVE_IMAGE_DIR = IMAGE_SAVE_SETTINGS['SAVE_IMAGE_DIR']
IMAGE_RETENTION_DAYS = IMAGE_SAVE_SETTINGS['IMAGE_RETENTION_DAYS']

CROP_X1 = CROP_SETTINGS['X1']
CROP_Y1 = CROP_SETTINGS['Y1']
CROP_X2 = CROP_SETTINGS['X2']
CROP_Y2 = CROP_SETTINGS['Y2']

BINARY_THRESHOLD = ANALYSIS_SETTINGS['BINARY_THRESHOLD']
CROP_SCALE_FACTOR = ANALYSIS_SETTINGS['CROP_SCALE_FACTOR']

INFLUXDB_URL = INFLUXDB_SETTINGS['INFLUXDB_URL']
INFLUXDB_TOKEN = INFLUXDB_SETTINGS['INFLUXDB_TOKEN']
INFLUXDB_ORG = INFLUXDB_SETTINGS['INFLUXDB_ORG']
INFLUXDB_BUCKET = INFLUXDB_SETTINGS['INFLUXDB_BUCKET']

# SCP設定値の展開
SCP_HOST = SCP_SETTINGS['HOST']
SCP_PORT = SCP_SETTINGS['PORT']
SCP_USERNAME = SCP_SETTINGS['USERNAME']
SCP_PASSWORD = SCP_SETTINGS.get('PASSWORD', None)
SCP_KEY_PATH = SCP_SETTINGS['KEY_PATH']
SCP_REMOTE_DIR = SCP_SETTINGS['REMOTE_DIR']

# GPIOセットアップ
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN_INJECT, GPIO.OUT)
GPIO.setup(RELAY_PIN_DRAIN, GPIO.OUT)
GPIO.setup(RELAY_PIN_PUMP, GPIO.OUT)

def relay_control(pin, state):
    """リレーの制御"""
    GPIO.output(pin, state)

def drain_water():
    """排水処理"""
    relay_control(RELAY_PIN_DRAIN, True)
    time.sleep(DRAIN_TIME) 
    relay_control(RELAY_PIN_DRAIN, False)

def inject_water():
    """注水処理"""
    relay_control(RELAY_PIN_INJECT, True)
    relay_control(RELAY_PIN_PUMP, True)
    time.sleep(INJECT_TIME) 
    relay_control(RELAY_PIN_INJECT, False)
    relay_control(RELAY_PIN_PUMP, False)


def capture_image():
    """USBカメラで画像を取得して保存"""
    if not os.path.exists(SAVE_IMAGE_DIR):
        os.makedirs(SAVE_IMAGE_DIR)
        
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("カメラが開けません")
        return None

    # カメラのウォームアップ（無いと、正しいフレームがキャプチャされなかった。）
    time.sleep(2)  # 2秒待機（必要に応じて調整）
    for _ in range(5):  # 最初の5フレームを破棄
        cap.read()

    ret, frame = cap.read()
    cap.release()
    if not ret:
        print("画像取得に失敗")
        return None
    
    # カメラが逆さまなので画像を180度回転
    frame = cv2.rotate(frame, cv2.ROTATE_180)
    
    # 画像を保存する
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = os.path.join(SAVE_IMAGE_DIR, f"slurry_{timestamp}.jpg")
    cv2.imwrite(save_path, frame)
    print(f"画像を保存しました: {save_path}")
    
    return frame, timestamp

def analyze_image(image, timestamp):
    """OpenCVで沈降した泥の面積比を判定"""
    # 指定された領域で画像を切り抜く
    cropped_image = image[CROP_Y1:CROP_Y2, CROP_X1:CROP_X2]
    
    # 切り抜いた画像を保存
    cropped_save_path = os.path.join(SAVE_IMAGE_DIR, f"slurry_{timestamp}_cropped.jpg")
    cv2.imwrite(cropped_save_path, cropped_image)
    print(f"切り取り画像を保存しました: {cropped_save_path}")
    
    # 切り抜いた画像に対して処理を行う
    gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, BINARY_THRESHOLD, 255, cv2.THRESH_BINARY_INV)

    # 沈降エリア（暗い部分）のピクセル数を計算
    total_pixels = binary.shape[0] * binary.shape[1]  # 画像の全ピクセル数
    sediment_pixels = np.count_nonzero(binary == 255)  # 二値化画像で白（255）になっているピクセル数
    
    # クロップ領域内での生の面積比を計算
    raw_percentage = (sediment_pixels / total_pixels) * 100
    
    # 実際の全体に対する調整済み面積比を計算
    sediment_percentage = raw_percentage * CROP_SCALE_FACTOR
    
    # 分析結果を可視化した画像を作成
    result_image = cropped_image.copy()
    
    # 二値化画像をカラーマップに変換して視覚化（沈降エリアを赤色で表示）
    color_mask = np.zeros_like(cropped_image)
    color_mask[:,:,2] = binary  # 赤チャンネルに二値化画像を設定
    
    # 元画像に半透明でマスクを重ねる
    alpha = 0.5  # 透明度
    result_image = cv2.addWeighted(result_image, 1, color_mask, alpha, 0)
    
    # 分析結果画像の表示テキストを更新 - 数値のみを2行で表示
    cv2.putText(result_image, f"{raw_percentage:.2f}%", 
              (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.putText(result_image, f"{sediment_percentage:.2f}%", 
              (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    # 分析結果画像を保存
    analysis_save_path = os.path.join(SAVE_IMAGE_DIR, f"slurry_{timestamp}_analysis.jpg")
    cv2.imwrite(analysis_save_path, result_image)
    print(f"分析結果画像を保存しました: {analysis_save_path}")

    # 二値化画像も保存
    binary_save_path = os.path.join(SAVE_IMAGE_DIR, f"slurry_{timestamp}_binary.jpg")
    cv2.imwrite(binary_save_path, binary)
    print(f"二値化画像を保存しました: {binary_save_path}")

    return sediment_percentage

def cleanup_old_images():
    """古い画像ファイルを削除"""
    if not os.path.exists(SAVE_IMAGE_DIR):
        return

    # 現在の日付から3ヶ月前の日付を計算
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=IMAGE_RETENTION_DAYS)
    print(f"古い画像ファイルを削除します：{cutoff_date.strftime('%Y/%m/%d')}以前")
    
    # 保存ディレクトリ内のすべてのファイルをチェック
    deleted_count = 0
    for filename in os.listdir(SAVE_IMAGE_DIR):
        if not filename.startswith("slurry_"):
            continue  # slurryで始まるファイルのみ処理
            
        file_path = os.path.join(SAVE_IMAGE_DIR, filename)
        
        # ファイル名からタイムスタンプを抽出 (slurry_YYYYMMDD_HHMMSS形式)
        timestamp_match = re.match(r'slurry_(\d{8})_(\d{6})', filename)
        
        if timestamp_match:
            # ファイル名からタイムスタンプを取得
            date_str = timestamp_match.group(1)
            time_str = timestamp_match.group(2)
            try:
                file_date = datetime.datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
                
                # ファイルの日付が閾値より古ければ削除
                if file_date < cutoff_date:
                    os.remove(file_path)
                    deleted_count += 1
            except ValueError:
                # 日付形式が間違っている場合はスキップ
                continue
        else:
            # ファイル名に日時情報がない場合はファイルの最終更新日時をチェック
            file_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_mtime < cutoff_date:
                os.remove(file_path)
                deleted_count += 1
    
    if deleted_count > 0:
        print(f"{deleted_count}個の古いファイルを削除しました")
    else:
        print("削除対象のファイルはありませんでした")

def write_to_influxdb(time_obj, values, measurement, location):
    """InfluxDB APIを使用してデータを送信
    values: 辞書形式で複数のフィールド値を指定可能 {'value': 10, 'url': 'http://...'}
    """
    full_url = INFLUXDB_URL
    
    headers = {
        "Authorization": f"Token {INFLUXDB_TOKEN}",
        "Content-Type": "text/plain; charset=utf-8",
    }

    timestamp_s = int(time_obj.timestamp()) 
    
    # 複数のフィールド値をカンマ区切りで連結
    fields_str = ",".join([f"{k}={v}" if isinstance(v, (int, float)) else f'{k}="{v}"' for k, v in values.items()])
    data_line = f"{measurement},location={location} {fields_str} {timestamp_s}"
    
    try:
        # リクエスト送信
        response = requests.post(full_url, headers=headers, data=data_line, timeout=10)
        
        if response.status_code == 204:
            print(f"InfluxDBにデータを送信しました: {measurement}")
            return True
        else:
            print(f"InfluxDBへのデータ送信に失敗しました: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"リクエスト例外が発生しました: {str(e)}")
        return False

def upload_images(timestamp):
    """SCPを使って画像をリモートサーバーにアップロード"""
    try:
        # 元画像ファイル名
        original_file = os.path.join(SAVE_IMAGE_DIR, f"slurry_{timestamp}.jpg")
        cropped_file = os.path.join(SAVE_IMAGE_DIR, f"slurry_{timestamp}_cropped.jpg")
        binary_file = os.path.join(SAVE_IMAGE_DIR, f"slurry_{timestamp}_binary.jpg")
        analysis_file = os.path.join(SAVE_IMAGE_DIR, f"slurry_{timestamp}_analysis.jpg")
        
        # 必要なファイルが存在するか確認
        if not all(os.path.exists(f) for f in [original_file, cropped_file, binary_file, analysis_file]):
            print("アップロード対象のファイルが見つかりません")
            return False

        # SSHクライアントの設定
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # SSH接続（鍵認証またはパスワード認証）
        if os.path.exists(SCP_KEY_PATH):
            private_key = paramiko.RSAKey.from_private_key_file(SCP_KEY_PATH)
            ssh.connect(SCP_HOST, port=SCP_PORT, username=SCP_USERNAME, pkey=private_key)
        else:
            ssh.connect(SCP_HOST, port=SCP_PORT, username=SCP_USERNAME, password=SCP_PASSWORD)
        
        # SCPクライアントの作成
        with SCPClient(ssh.get_transport()) as scp:
            # タイムスタンプ付きの画像をアップロード
            scp.put(original_file, f"{SCP_REMOTE_DIR}/slurry_{timestamp}.jpg")
            scp.put(cropped_file, f"{SCP_REMOTE_DIR}/slurry_{timestamp}_cropped.jpg")
            scp.put(binary_file, f"{SCP_REMOTE_DIR}/slurry_{timestamp}_binary.jpg")
            scp.put(analysis_file, f"{SCP_REMOTE_DIR}/slurry_{timestamp}_analysis.jpg")
            
            # 最新画像として固定名でもアップロード（上書き）
            scp.put(original_file, f"{SCP_REMOTE_DIR}/latest.jpg")
            scp.put(cropped_file, f"{SCP_REMOTE_DIR}/latest_cropped.jpg")
            scp.put(binary_file, f"{SCP_REMOTE_DIR}/latest_binary.jpg")
            scp.put(analysis_file, f"{SCP_REMOTE_DIR}/latest_analysis.jpg")
        
        # SSH切断
        ssh.close()
        print(f"画像のアップロードが完了しました: {SCP_HOST}:{SCP_REMOTE_DIR}")
        return True
        
    except Exception as e:
        print(f"画像アップロード中にエラーが発生しました: {e}")
        return False

def main():
    # 古い画像ファイルのクリーンアップ
    cleanup_old_images()
    
    drain_water()  # 排水
    inject_water()  # 注水
    time.sleep(WAITING_TIME)  # 待機

    capture_result = capture_image()
    if capture_result is not None:
        image, timestamp = capture_result
        sediment_percentage = analyze_image(image, timestamp)
        print(f"スラリー濃度: {sediment_percentage:.2f}%")

        # 画像のURL生成
        base_url = f"https://{SCP_HOST}/slurryimages"
        original_image_url = f"{base_url}/slurry_{timestamp}.jpg"
        analysis_image_url = f"{base_url}/slurry_{timestamp}_analysis.jpg"
        
        # 現在時刻
        current_time = datetime.datetime.now()
        
        # 1. 通常の測定データを送信
        values = {
            'value': sediment_percentage,
        }
        write_to_influxdb(current_time, values, "sediment_percentage", "slurrykun")
        
        # 2. アノテーション用のデータを送信
        # Grafanaでクリック可能なHTMLリンクを作成
        html_links = f'<a href="{original_image_url}" target="_blank">原画像</a> | <a href="{analysis_image_url}" target="_blank">分析結果</a>'
        
        annotation_values = {
            'title': f"スラリー濃度: {sediment_percentage:.2f}%",
            'text': html_links,
            'tags': "slurry,image"
        }
        write_to_influxdb(current_time, annotation_values, "slurry_annotations", "slurrykun")
        
        # 画像をサーバーにアップロード
        upload_images(timestamp)

    GPIO.cleanup()

if __name__ == "__main__":
    main()
