import cv2
import time


def test_camera():
    cap = cv2.VideoCapture(0)  # /dev/video0 を使用
    if not cap.isOpened():
        print("カメラが開けません")
        return
    # カメラのウォームアップ
    time.sleep(2)  # 2秒待機（必要に応じて調整）
    for _ in range(5):  # 最初の5フレームを破棄
        cap.read()

    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("画像取得に失敗しました")
        return

    cv2.imwrite("test_image.jpg", frame)
    print("画像を保存しました: test_image.jpg")

if __name__ == "__main__":
    test_camera()