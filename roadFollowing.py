import cv2 as cv
import time
import serial
import numpy as np

camera = cv.VideoCapture(0)

robot = serial.Serial('/dev/ttyACM0', 115200)
START_BYTE = 0xFF
END_BYTE = 0xFE

buffer = [' ' for i in range(6)]
buffer[0] = START_BYTE
buffer[5] = END_BYTE

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
                recangle = cv.circle(recangle, (pixelL, i*40+20), 5, (110), -1)
                pixelR = np.argmin(recangle[i*40+20][midpoint:])+midpoint
                recangle = cv.circle(recangle, (pixelR, i*40+20), 5, (110), -1)
                error = (midpoint-pixelL)+(midpoint-pixelR)
                print (str(pixelL), '\t', str(pixelR), '\t', str(error))
            print ('='*20)
            buffer[1] = 1
            buffer[2] = clamp(int(speed+(error)), 0, 255)
            buffer[3] = 1
            buffer[4] = clamp(int(speed-(error)), 0, 255)
            robot.write(buffer)
                
            



if __name__ == '__main__':
    getFramesGenerator()


robot.close()
