import cv2 as cv
from flask import Flask, render_template, Response, request
import time
import argparse
import serial
import numpy as np

camera = cv.VideoCapture(0)
app = Flask(__name__)

size = [240, 320]

src = np.float32([[0, 240],
                 [320, 240],
                 [280, 80],
                 [40, 80]])
dst = np.float32([[0, size[0]],
                    [size[1], size[0]],
                    [size[1], 0],
                    [0, 0]])

src_draw = np.array(src, dtype=np.int32)

def getFramesGenerator():
    """ Генератор фреймов для вывода в веб-страницу, тут же можно поиграть с openCV"""
    while True:
        time.sleep(0.01)    # ограничение fps (если видео тупит, можно убрать)
        success, frame = camera.read()  # Получаем фрейм с камеры
        if success:
            frame = cv.resize(frame, (size[1], size[0]), interpolation=cv.INTER_AREA)  # уменьшаем разрешение кадров (если видео тупит, можно уменьшить еще больше)
            frame = cv.GaussianBlur(frame,  (5,5), 1)
            hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
            ligh_channel = hsv[:,:,2]
            binary = np.zeros_like(ligh_channel)
            binary[(ligh_channel > 50)] = 255
            cv.polylines(binary, [src_draw], True, 0)
            M = cv.getPerspectiveTransform(src, dst)
            recangle = cv.warpPerspective(binary, M, (size[1], size[0]), flags= cv.INTER_LINEAR)
            _, buffer = cv.imencode('.jpg', recangle)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/')
def index():
    """ Выводим видеопоток """
    return Response(getFramesGenerator(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # пакет, посылаемый на робота
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5000, help="Running port")
    parser.add_argument("-i", "--ip", type=str, default='172.16.0.49', help="Ip address")
    args = parser.parse_args()
    app.run(debug=False, host=args.ip, port=args.port)   # запускаем flask приложение