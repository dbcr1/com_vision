import cv2 as cv
from flask import Flask, render_template, Response, request
import time
import argparse
import serial
import numpy as np

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

pi = 0
speed = 200
sum_error = 0
error = 0

camera = cv.VideoCapture(0)
app = Flask(__name__)

size = [240, 320]

src = np.float32([[0, 180],
                 [320, 180],
                 [250, 50],
                 [70, 50]]) 
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
    global sum_error
    error = 0
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
            recangle = cv.rectangle(recangle, (130, 220), (190, 240), (255,255,255), -1)
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
                
                error = (error + ((midpoint-pixelL)+(midpoint-pixelR)))*(i*0.1)
                #print (str(pixelL).ljust(5), '|', str(pixelR).ljust(5), '|', str(error).ljust(4))
            pi = error * 0.5+ sum_error*0.7
            
            sum_error = sum_error*0.5 + error
            print (error ,'\t',round(pi, 3), '\t', round(sum_error,3))
            buffer[1] = 1
            buffer[2] = clamp(int(speed + pi), 80, 230)
            buffer[3] = 1
            buffer[4] = clamp(int(speed - pi), 80, 230)
            robot.write(buffer)
            print ('='*20)

            _, buf = cv.imencode('.jpg', recangle)
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
