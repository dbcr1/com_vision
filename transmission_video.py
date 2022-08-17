import cv2 as cv
from flask import Flask, render_template, Response, request
import time
import argparse
import serial
import numpy as np

camera = cv.VideoCapture(0)
app = Flask(__name__)

robot = serial.Serial('/dev/ttyACM0', 115200)
START_BYTE = 0xFF
END_BYTE = 0xFE

buffer = [' ' for i in range(6)]
buffer[0] = START_BYTE
buffer[5] = END_BYTE
buffer[1] = 1
buffer[2] = 0
buffer[3] = 1
buffer[4] = 0
time.sleep(1)
robot.write(buffer)

ek = 0
speed = 110

size = [240, 320]

src = np.float32([[0, 210],
                 [320, 210],
                 [240, 110],
                 [60, 110]])
dst = np.float32([[0, size[0]],
                    [size[1], size[0]],
                    [size[1], 0],
                    [0, 0]])

src_draw = np.array(src, dtype=np.int32)
def clamp(x, min, max):
    if x < min:
        return min
    if x > max:
        return max
    return x

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
            binary[(ligh_channel > 65)] = 255
            cv.polylines(frame, [src_draw], True, 0)
            M = cv.getPerspectiveTransform(src, dst)
            recangle = cv.warpPerspective(binary, M, (size[1], size[0]), flags= cv.INTER_LINEAR)
            
            # поиск самого темного пикселя
            midpoint = recangle.shape[1]//2
            for i in range(6):
                pixelL = np.argmin(recangle[i*40+20][0:midpoint])
                widthLine = np.argmax(recangle[i*40+20][pixelL:])
                pixelL = pixelL + int(widthLine/2)
                recangle = cv.circle(recangle, (pixelL, i*40+20), 5, (110), -1)

                pixelR = np.argmin(recangle[i*40+20][midpoint:])+midpoint
                widthLine = np.argmax(recangle[i*40+20][pixelR:])
                pixelR = pixelR + int(widthLine/2)
                recangle = cv.circle(recangle, (pixelR, i*40+20), 5, (110), -1)
                
                error = (midpoint-pixelL)+(midpoint-pixelR)
                print (str(pixelL), '\t', str(pixelR), '\t', str(error))
            _, buf = cv.imencode('.jpg', recangle)
            buffer[1] = 1
            buffer[2] = clamp(int(speed+(error*0.5)), 0, 255)
            buffer[3] = 1
            buffer[4] = clamp(int(speed-(error*0.5)), 0, 255)
            robot.write(buffer)
            print ('='*20)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buf.tobytes() + b'\r\n')

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

robot.close()