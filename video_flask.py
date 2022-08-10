import cv2 as cv
from flask import Flask, render_template, Response, request
import time
import argparse

camera = cv.VideoCapture(0)
app = Flask(__name__)

def getFramesGenerator():
    """ Генератор фреймов для вывода в веб-страницу, тут же можно поиграть с openCV"""
    while True:
        #time.sleep(0.01)    # ограничение fps (если видео тупит, можно убрать)
        success, frame = camera.read()  # Получаем фрейм с камеры
        if success:
            frame = cv.resize(frame, (320, 240))  # уменьшаем разрешение кадров (если видео тупит, можно уменьшить еще больше)
            _, buffer = cv.imencode('.jpg', frame)
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
    